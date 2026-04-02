"""
Advanced NLP Analysis Module for CSPOPS

Features:
- Transformer-based sentiment analysis (HuggingFace)
- Named Entity Recognition (NER)
- Emotion detection (anger, fear, joy, sadness, surprise)
- Topic modeling with BERTopic
- Key phrase extraction
- Text summarization
- Stance detection
- Credibility scoring
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

# Optional imports - system works with fallbacks
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None  # Prevent name errors

try:
    # Lazy load BERTopic to avoid numba/coverage conflict
    BERTOPIC_AVAILABLE = True
except ImportError:
    BERTOPIC_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


@dataclass
class SentimentResult:
    """Detailed sentiment analysis result."""
    text: str
    sentiment: str  # positive, negative, neutral
    confidence: float
    positive_score: float
    negative_score: float
    neutral_score: float
    compound_score: float  # -1 to 1


@dataclass
class EmotionResult:
    """Emotion detection result."""
    text: str
    emotions: Dict[str, float]  # anger, fear, joy, sadness, surprise, disgust
    dominant_emotion: str


@dataclass
class EntityResult:
    """Named entity recognition result."""
    text: str
    entities: List[Dict[str, Any]]  # [{text, label, start, end, confidence}]
    entity_summary: Dict[str, int]  # {label: count}


@dataclass
class TopicResult:
    """Topic modeling result."""
    topics: List[int]  # topic ID for each document
    topic_terms: Dict[int, List[str]]  # {topic_id: [top terms]}
    topic_distribution: Dict[int, float]  # {topic_id: proportion}


class AdvancedNLPAnalyzer:
    """
    Advanced NLP analysis for public opinion monitoring.
    
    Uses state-of-the-art transformer models for:
    - Sentiment analysis
    - Emotion detection
    - Named entity recognition
    - Topic modeling
    """
    
    def __init__(self, use_gpu: bool = False):
        self.use_gpu = use_gpu and TORCH_AVAILABLE and torch.cuda.is_available()
        self.device = 0 if self.use_gpu else -1
        
        # Initialize pipelines (lazy loading)
        self._sentiment_pipeline = None
        self._ner_pipeline = None
        self._emotion_pipeline = None
        self._topic_model = None
        
        # Emotion labels
        self.emotion_labels = [
            "anger", "fear", "joy", "sadness", "surprise", "disgust", "neutral"
        ]
    
    @property
    def sentiment_pipeline(self):
        """Lazy load sentiment pipeline."""
        if self._sentiment_pipeline is None:
            if TRANSFORMERS_AVAILABLE:
                self._sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    device=self.device
                )
            else:
                raise ImportError("transformers not installed")
        return self._sentiment_pipeline
    
    @property
    def ner_pipeline(self):
        """Lazy load NER pipeline."""
        if self._ner_pipeline is None:
            if TRANSFORMERS_AVAILABLE:
                self._ner_pipeline = pipeline(
                    "ner",
                    model="dslim/bert-base-NER",
                    device=self.device,
                    aggregation_strategy="simple"
                )
            else:
                raise ImportError("transformers not installed")
        return self._ner_pipeline
    
    def analyze_sentiment_batch(self, texts: List[str]) -> List[SentimentResult]:
        """
        Analyze sentiment for multiple texts.

        Args:
            texts: List of texts to analyze

        Returns:
            List of SentimentResult objects
        """
        results = []

        if not TRANSFORMERS_AVAILABLE:
            # Fallback: simple keyword-based sentiment
            for text in texts:
                results.append(self._simple_sentiment(text))
            return results

        # Truncate texts to avoid model sequence length limits
        MAX_TOKENS = 510  # Leave room for special tokens
        AVG_CHARS_PER_TOKEN = 4
        MAX_CHARS = MAX_TOKENS * AVG_CHARS_PER_TOKEN
        
        truncated_texts = []
        for text in texts:
            if len(text) > MAX_CHARS:
                truncated_texts.append(text[:MAX_CHARS] + "...")
            else:
                truncated_texts.append(text)

        # Batch processing for efficiency
        try:
            pipeline_results = self.sentiment_pipeline(truncated_texts[:50])  # Limit batch size

            for text, result in zip(truncated_texts, pipeline_results):
                label = result['label'].lower()
                score = result['score']

                # Convert to detailed scores
                if label == 'positive':
                    pos_score = score
                    neg_score = 1 - score
                else:
                    pos_score = 1 - score
                    neg_score = score

                compound = pos_score - neg_score

                results.append(SentimentResult(
                    text=text[:500],
                    sentiment=label,
                    confidence=score,
                    positive_score=pos_score,
                    negative_score=neg_score,
                    neutral_score=0.0,
                    compound_score=compound
                ))
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            # Fallback for failed analyses
            for text in texts:
                results.append(self._simple_sentiment(text))

        return results
    
    def _simple_sentiment(self, text: str) -> SentimentResult:
        """Simple keyword-based sentiment (fallback)."""
        positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 
                         'best', 'love', 'happy', 'positive', 'success'}
        negative_words = {'bad', 'terrible', 'awful', 'worst', 'hate', 'sad',
                         'negative', 'fail', 'poor', 'horrible'}
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            compound = 0.0
            sentiment = 'neutral'
            confidence = 0.5
        else:
            compound = (pos_count - neg_count) / total
            sentiment = 'positive' if compound > 0 else 'negative' if compound < 0 else 'neutral'
            confidence = abs(compound)
        
        return SentimentResult(
            text=text[:500],
            sentiment=sentiment,
            confidence=confidence,
            positive_score=max(0, compound),
            negative_score=max(0, -compound),
            neutral_score=1 - abs(compound),
            compound_score=compound
        )
    
    def detect_emotions(self, texts: List[str]) -> List[EmotionResult]:
        """
        Detect emotions in texts using transformer-based model.

        Args:
            texts: List of texts to analyze

        Returns:
            List of EmotionResult objects
        """
        results = []

        # Truncate texts to avoid model sequence length limits
        # Roberta-based models have max 512 tokens, truncate to ~400 tokens to be safe
        MAX_TOKENS = 400
        AVG_CHARS_PER_TOKEN = 4  # Conservative estimate
        MAX_CHARS = MAX_TOKENS * AVG_CHARS_PER_TOKEN
        
        truncated_texts = []
        for text in texts:
            if len(text) > MAX_CHARS:
                # Truncate and add ellipsis
                truncated_texts.append(text[:MAX_CHARS] + "...")
            else:
                truncated_texts.append(text)

        # Try to use transformer-based emotion detection first
        if TRANSFORMERS_AVAILABLE and TORCH_AVAILABLE:
            try:
                # Use a pre-trained emotion detection model
                from transformers import pipeline

                # Load emotion detection model (only once, cache it)
                if not hasattr(self, '_emotion_pipeline') or self._emotion_pipeline is None:
                    try:
                        print("Loading emotion detection model...")
                        # Try to load a dedicated emotion model
                        self._emotion_pipeline = pipeline(
                            "text-classification",
                            model="j-hartmann/emotion-english-distilroberta-base",
                            top_k=None,  # Get all emotions
                            device=self.device if self.device >= 0 else -1,
                            truncation=True,  # Enable truncation
                            max_length=MAX_TOKENS
                        )
                        print("✓ Emotion model loaded successfully")
                    except Exception as e:
                        print(f"Emotion model load error: {e}, using sentiment fallback")
                        # Fallback to sentiment model with emotion mapping
                        self._emotion_pipeline = pipeline(
                            "sentiment-analysis",
                            model="distilbert-base-uncased-finetuned-sst-2-english",
                            device=self.device if self.device >= 0 else -1,
                            truncation=True,
                            max_length=MAX_TOKENS
                        )

                # Check if pipeline is callable
                if self._emotion_pipeline is None:
                    print("⚠ Emotion pipeline is None, using fallback")
                    return [self._simple_emotion(text) for text in truncated_texts]

                # Process texts in batches
                batch_size = 10
                for i in range(0, len(truncated_texts), batch_size):
                    batch = truncated_texts[i:i+batch_size]

                    try:
                        emotion_outputs = self._emotion_pipeline(batch)

                        for text, output in zip(batch, emotion_outputs):
                            # Handle different output formats
                            if isinstance(output, list):
                                # Emotion model returns list of emotions
                                emotions = {item['label']: item['score'] for item in output}
                            else:
                                # Sentiment model - map to emotions
                                label = output['label'].lower()
                                score = output['score']
                                if 'positive' in label:
                                    emotions = {'joy': score, 'neutral': 1-score}
                                else:
                                    emotions = {'sadness': score*0.6, 'anger': score*0.4, 'neutral': 1-score}

                            # Normalize emotions
                            total = sum(emotions.values())
                            if total > 0:
                                emotions = {k: v/total for k, v in emotions.items()}

                            # Find dominant emotion
                            dominant = max(emotions, key=emotions.get) if emotions else 'neutral'

                            results.append(EmotionResult(
                                text=text[:500],
                                emotions=emotions,
                                dominant_emotion=dominant
                            ))
                    except Exception as e:
                        print(f"Emotion batch error: {e}")
                        # Fallback for this batch
                        for text in batch:
                            results.append(self._simple_emotion(text))

                return results

            except Exception as e:
                print(f"Transformer emotion detection failed: {e}, using fallback")

        # Fallback: Simple keyword-based emotion detection
        return [self._simple_emotion(text) for text in truncated_texts]
    
    def _simple_emotion(self, text: str) -> EmotionResult:
        """Simple keyword-based emotion detection (fallback)."""
        # Extended keywords including Malay words
        emotion_keywords = {
            'joy': {'happy', 'joy', 'delighted', 'pleased', 'thrilled', 'excited', 'glad',
                   'gembira', 'seronok', 'best', 'bagus', 'hebat', 'mantap', 'terbaik',
                   'love', 'loved', 'loving', 'cinta', 'suka', 'syukur', 'alhamdulillah'},
            'anger': {'angry', 'anger', 'furious', 'mad', 'outraged', 'infuriated', 'hate',
                     'marah', 'geram', 'berang', 'benci', 'meluat', 'menyampah', 'sial',
                     'hell', 'damn', 'crap', 'stupid', 'idiot', 'bodoh', 'bangang'},
            'fear': {'fear', 'afraid', 'scared', 'terrified', 'worried', 'anxious', 'panic',
                    'takut', 'gerun', 'cemas', 'risau', 'bimbang', 'khawatir',
                    'worry', 'nervous', 'terrifying'},
            'sadness': {'sad', 'sadness', 'depressed', 'unhappy', 'miserable', 'grief', 'sorrow',
                       'sedih', 'duka', 'kecewa', 'hampa', 'sedey', 'nangis', 'cry',
                       'disappointed', 'hopeless', 'despair'},
            'surprise': {'surprised', 'shocked', 'astonished', 'amazed', 'stunned',
                        'terkejut', 'hairan', 'pelik', 'ajaib',
                        'wow', 'omg', 'what', 'really'},
            'disgust': {'disgusted', 'disgust', 'revulsed', 'repulsed', 'nauseated',
                       'jijik', 'muak', 'loya', 'muntah',
                       'gross', 'vile', 'nasty'}
        }
        
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            emotion_scores[emotion] = score / len(keywords)
        
        # If no emotions detected, check sentiment as fallback
        if sum(emotion_scores.values()) < 0.1:
            # Simple sentiment check
            positive_words = {'good', 'great', 'excellent', 'best', 'nice', 'baik', 'bagus'}
            negative_words = {'bad', 'terrible', 'worst', 'poor', 'buruk', 'teruk', 'sial'}
            
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            
            if pos_count > neg_count:
                emotion_scores['joy'] = 0.5
            elif neg_count > pos_count:
                emotion_scores['anger'] = 0.3
                emotion_scores['sadness'] = 0.2
        
        # Add neutral
        total = sum(emotion_scores.values())
        emotion_scores['neutral'] = max(0, 1 - total)
        
        # Normalize
        total = sum(emotion_scores.values())
        if total > 0:
            emotion_scores = {k: v/total for k, v in emotion_scores.items()}
        
        # Find dominant emotion
        dominant = max(emotion_scores, key=emotion_scores.get)
        
        return EmotionResult(
            text=text[:500],
            emotions=emotion_scores,
            dominant_emotion=dominant
        )
    
    def extract_entities(self, texts: List[str]) -> List[EntityResult]:
        """
        Extract named entities from texts.
        
        Args:
            texts: List of texts to analyze
        
        Returns:
            List of EntityResult objects
        """
        results = []
        
        if not TRANSFORMERS_AVAILABLE:
            # Fallback: simple pattern matching
            for text in texts:
                results.append(self._simple_ner(text))
            return results
        
        try:
            for text in texts[:20]:  # Limit for performance
                ner_results = self.ner_pipeline(text)
                
                entities = []
                entity_summary = {}
                
                for entity in ner_results:
                    ent_dict = {
                        'text': entity['word'],
                        'label': entity['entity_group'],
                        'confidence': float(entity['score'])
                    }
                    entities.append(ent_dict)
                    
                    label = entity['entity_group']
                    entity_summary[label] = entity_summary.get(label, 0) + 1
                
                results.append(EntityResult(
                    text=text[:500],
                    entities=entities,
                    entity_summary=entity_summary
                ))
        except Exception as e:
            print(f"NER error: {e}")
            for text in texts:
                results.append(self._simple_ner(text))
        
        return results
    
    def _simple_ner(self, text: str) -> EntityResult:
        """Simple pattern-based NER (fallback)."""
        import re
        
        entities = []
        entity_summary = {}
        
        # Simple patterns
        patterns = {
            'MONEY': r'\$[\d,]+(?:\.\d+)?',
            'PERCENT': r'\d+(?:\.\d+)?%',
            'DATE': r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
            'ORG': r'\b(?:Government|Congress|Senate|Federal|Department|Agency)\b'
        }
        
        for label, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({'text': match, 'label': label, 'confidence': 0.8})
                entity_summary[label] = entity_summary.get(label, 0) + 1
        
        return EntityResult(
            text=text[:500],
            entities=entities,
            entity_summary=entity_summary
        )
    
    def model_topics(self, texts: List[str], n_topics: int = 5) -> TopicResult:
        """
        Model topics from texts using BERTopic.
        
        Args:
            texts: List of texts to analyze
            n_topics: Number of topics to extract
        
        Returns:
            TopicResult object
        """
        # Lazy load BERTopic to avoid import conflicts
        if BERTOPIC_AVAILABLE:
            try:
                from bertopic import BERTopic
                ACTUAL_BERTOPIC_AVAILABLE = True
            except (ImportError, AttributeError):
                ACTUAL_BERTOPIC_AVAILABLE = False
        else:
            ACTUAL_BERTOPIC_AVAILABLE = False
        
        if not ACTUAL_BERTOPIC_AVAILABLE or len(texts) < 5:
            # Fallback: simple keyword-based topics
            return self._simple_topic_modeling(texts, n_topics)
        
        try:
            # Initialize BERTopic
            topic_model = BERTopic(
                nr_topics=n_topics,
                language="english",
                verbose=False
            )
            
            # Fit model
            topics, probs = topic_model.fit_transform(texts)
            
            # Get topic terms
            topic_terms = {}
            for topic_id in set(topics):
                if topic_id != -1:  # Skip outliers
                    terms = topic_model.get_topic(topic_id)[:10]
                    topic_terms[topic_id] = [term for term, _ in terms]
            
            # Get topic distribution
            topic_counts = {}
            for topic in topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            topic_distribution = {
                topic: count / len(topics)
                for topic, count in topic_counts.items()
            }
            
            return TopicResult(
                topics=topics,
                topic_terms=topic_terms,
                topic_distribution=topic_distribution
            )
            
        except Exception as e:
            print(f"Topic modeling error: {e}")
            return self._simple_topic_modeling(texts, n_topics)
    
    def _simple_topic_modeling(self, texts: List[str], n_topics: int = 5) -> TopicResult:
        """Simple keyword-based topic modeling (fallback)."""
        from collections import Counter
        
        # Define topic keywords
        topic_keywords = {
            0: ['economy', 'economic', 'jobs', 'unemployment', 'inflation', 'market'],
            1: ['healthcare', 'health', 'hospital', 'medical', 'insurance', 'policy'],
            2: ['education', 'school', 'students', 'teachers', 'university', 'college'],
            3: ['climate', 'environment', 'energy', 'renewable', 'carbon', 'green'],
            4: ['security', 'defense', 'military', 'border', 'immigration', 'safety']
        }
        
        topics = []
        topic_counts = Counter()
        
        for text in texts:
            text_lower = text.lower()
            best_topic = 0
            best_score = 0
            
            for topic_id, keywords in topic_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                if score > best_score:
                    best_score = score
                    best_topic = topic_id
            
            topics.append(best_topic)
            topic_counts[best_topic] += 1
        
        topic_terms = {topic_id: keywords for topic_id, keywords in topic_keywords.items()}
        
        topic_distribution = {
            topic: count / len(texts)
            for topic, count in topic_counts.items()
        }
        
        return TopicResult(
            topics=topics,
            topic_terms=topic_terms,
            topic_distribution=topic_distribution
        )
    
    def generate_insights(self, 
                         sentiment_results: List[SentimentResult],
                         emotion_results: List[EmotionResult],
                         entity_results: List[EntityResult]) -> Dict[str, Any]:
        """
        Generate actionable insights from NLP analysis.
        
        Args:
            sentiment_results: Sentiment analysis results
            emotion_results: Emotion detection results
            entity_results: NER results
        
        Returns:
            Dictionary of insights
        """
        insights = {
            'overall_sentiment': {},
            'emotion_breakdown': {},
            'key_entities': {},
            'alerts': [],
            'recommendations': []
        }
        
        # Overall sentiment
        if sentiment_results:
            avg_compound = np.mean([r.compound_score for r in sentiment_results])
            positive_pct = sum(1 for r in sentiment_results if r.sentiment == 'positive') / len(sentiment_results)
            negative_pct = sum(1 for r in sentiment_results if r.sentiment == 'negative') / len(sentiment_results)
            
            insights['overall_sentiment'] = {
                'average_score': float(avg_compound),
                'positive_percentage': float(positive_pct),
                'negative_percentage': float(negative_pct),
                'classification': 'positive' if avg_compound > 0.1 else 'negative' if avg_compound < -0.1 else 'neutral'
            }
            
            # Generate alerts
            if avg_compound < -0.3:
                insights['alerts'].append({
                    'type': 'CRITICAL',
                    'message': f"Strongly negative sentiment detected ({avg_compound:.2f})",
                    'action': 'Immediate review recommended'
                })
            elif avg_compound < -0.1:
                insights['alerts'].append({
                    'type': 'WARNING',
                    'message': f"Negative sentiment trend ({avg_compound:.2f})",
                    'action': 'Monitor closely'
                })
        
        # Emotion breakdown
        if emotion_results:
            emotion_totals = {}
            for result in emotion_results:
                for emotion, score in result.emotions.items():
                    emotion_totals[emotion] = emotion_totals.get(emotion, 0) + score
            
            # Normalize
            total = sum(emotion_totals.values())
            if total > 0:
                insights['emotion_breakdown'] = {
                    emotion: score / total
                    for emotion, score in emotion_totals.items()
                }
                
                # Check for concerning emotions
                if emotion_totals.get('anger', 0) / total > 0.3:
                    insights['alerts'].append({
                        'type': 'WARNING',
                        'message': 'High anger levels detected in public discourse',
                        'action': 'Consider proactive communication'
                    })
                
                if emotion_totals.get('fear', 0) / total > 0.3:
                    insights['alerts'].append({
                        'type': 'WARNING',
                        'message': 'High fear levels detected in public discourse',
                        'action': 'Address public concerns directly'
                    })
        
        # Key entities
        if entity_results:
            all_entities = {}
            for result in entity_results:
                for label, count in result.entity_summary.items():
                    all_entities[label] = all_entities.get(label, 0) + count
            
            insights['key_entities'] = all_entities
        
        # Generate recommendations
        if insights['overall_sentiment'].get('classification') == 'negative':
            insights['recommendations'].append(
                "Launch public communication campaign to address concerns"
            )
        
        if insights['emotion_breakdown'].get('anger', 0) > 0.25:
            insights['recommendations'].append(
                "Engage with community leaders to de-escalate tensions"
            )
        
        return insights


def analyze_texts(texts: List[str]) -> Dict[str, Any]:
    """
    Convenience function for complete NLP analysis.
    
    Args:
        texts: List of texts to analyze
    
    Returns:
        Complete analysis results dictionary
    """
    analyzer = AdvancedNLPAnalyzer()
    
    # Run all analyses
    sentiment_results = analyzer.analyze_sentiment_batch(texts)
    emotion_results = analyzer.detect_emotions(texts)
    entity_results = analyzer.extract_entities(texts)
    topic_results = analyzer.model_topics(texts)
    
    # Generate insights
    insights = analyzer.generate_insights(sentiment_results, emotion_results, entity_results)
    
    # Compile results
    return {
        'sentiment': [
            {
                'text': r.text[:100],
                'sentiment': r.sentiment,
                'confidence': r.confidence,
                'compound': r.compound_score
            }
            for r in sentiment_results
        ],
        'emotions': [
            {
                'text': r.text[:100],
                'dominant_emotion': r.dominant_emotion,
                'emotions': r.emotions
            }
            for r in emotion_results
        ],
        'entities': [
            {
                'text': r.text[:100],
                'entities': r.entities,
                'summary': r.entity_summary
            }
            for r in entity_results
        ],
        'topics': {
            'topic_ids': topic_results.topics,
            'topic_terms': topic_results.topic_terms,
            'distribution': topic_results.topic_distribution
        },
        'insights': insights
    }


if __name__ == "__main__":
    # Test the analyzer
    test_texts = [
        "The economy is doing great! Jobs are up and unemployment is down.",
        "I'm angry about the healthcare system. It's terrible and needs reform.",
        "The new education policy is amazing. Students will benefit greatly.",
        "I'm worried about climate change. We need immediate action.",
        "The government is failing us. Corruption everywhere."
    ]
    
    results = analyze_texts(test_texts)
    
    print("=" * 60)
    print("NLP Analysis Results")
    print("=" * 60)
    
    print(f"\nOverall Sentiment: {results['insights']['overall_sentiment']}")
    print(f"\nEmotion Breakdown: {results['insights']['emotion_breakdown']}")
    print(f"\nAlerts: {results['insights']['alerts']}")
    print(f"\nRecommendations: {results['insights']['recommendations']}")
