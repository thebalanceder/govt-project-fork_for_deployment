"""
Data Adapter for MiroFish Integration

Converts unified collector output + NLP analysis to format expected by MiroFish agents
"""

from typing import Dict, List, Any
from datetime import datetime


class MiroFishDataAdapter:
    """Convert collected data and NLP analysis to format expected by MiroFish agents."""
    
    @staticmethod
    def convert_to_agent_format(data: Dict[str, List], nlp_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Convert unified collector output + NLP analysis to MiroFish input format.
        
        Args:
            data: {'economic': [...], 'political': [...], 'cultural': [...]}
            nlp_analysis: Sentiment and emotion analysis results
            
        Returns:
            Formatted data for agent analysis with sentiment trends
        """
        agent_data = {
            'economic': [],
            'political': [],
            'cultural': [],
            'social_media': [],
            'news': [],
            'sentiment_trends': {},
            'nlp_summary': nlp_analysis
        }
        
        # Convert each category
        for category in ['economic', 'political', 'cultural']:
            items = data.get(category, [])
            for item in items:
                # Convert DataItem to dict if needed
                if hasattr(item, '__dict__'):
                    item_dict = {
                        'text': getattr(item, 'text', '')[:2000],
                        'title': getattr(item, 'title', ''),
                        'source': getattr(item, 'source', ''),
                        'timestamp': getattr(item, 'timestamp', datetime.now()).isoformat() if hasattr(item, 'timestamp') else datetime.now().isoformat(),
                        'value': getattr(item, 'value', None),
                        'metadata': getattr(item, 'metadata', {})
                    }
                else:
                    item_dict = item
                
                agent_data[category].append(item_dict)
                agent_data['news'].append(item_dict)
        
        # Add sentiment trends from NLP analysis
        if nlp_analysis:
            agent_data['sentiment_trends'] = {
                'overall_sentiment': nlp_analysis.get('overall_sentiment', {}),
                'emotion_breakdown': nlp_analysis.get('emotion_breakdown', {}),
                'sentiment_results': nlp_analysis.get('sentiment_results', [])[:20],  # Sample for agents
                'insights': nlp_analysis.get('insights', {})
            }
        
        return agent_data
    
    @staticmethod
    def format_discussion_results(discussion_results: Dict) -> Dict[str, Any]:
        """
        Format MiroFish discussion results for API response.
        
        Args:
            discussion_results: Dict of {topic: DiscussionResult}
            
        Returns:
            Formatted results for JSON response with detailed explanations
        """
        formatted = {}
        
        for topic, result in discussion_results.items():
            formatted[topic] = {
                'final_consensus': float(result.final_consensus),
                'convergence_rate': float(result.convergence_rate),
                'num_rounds': len(result.rounds),
                'explanation': result.explanation,
                'agent_forecasts': {
                    name: {
                        'sentiment': float(forecast['sentiment']),
                        'forecast_7d': float(forecast['forecast_7d']),
                        'forecast_30d': float(forecast['forecast_30d']),
                        'confidence': float(forecast['confidence']),
                        'key_factors': forecast.get('key_factors', []),
                        'reasoning': forecast.get('reasoning', '')
                    }
                    for name, forecast in result.agent_forecasts.items()
                },
                'round_history': [
                    {
                        'round': r.round_number,
                        'average_sentiment': float(r.average_sentiment),
                        'convergence_score': float(r.convergence_score),
                        'timestamp': r.timestamp.isoformat()
                    }
                    for r in result.rounds
                ],
                'indicator_explanations': MiroFishDataAdapter._generate_indicator_explanations(result, topic)
            }
        
        return formatted
    
    @staticmethod
    def _generate_indicator_explanations(result, topic: str) -> Dict[str, str]:
        """
        Generate detailed explanations of key indicators for users.
        
        Args:
            result: DiscussionResult object
            topic: Topic being discussed
            
        Returns:
            Dictionary of indicator names to explanations
        """
        explanations = {
            'consensus': f"The overall sentiment consensus across all 6 AI agents for {topic} matters. A positive value (+0.1 to +1.0) indicates optimistic outlook, while negative (-1.0 to -0.1) suggests concerns.",
            'convergence': f"How much the 6 agents agree on their analysis. High convergence (>70%) means strong agreement among experts. Low convergence (<40%) indicates diverse perspectives.",
            'forecast_7d': "Predicted sentiment trend over the next 7 days based on current indicators and agent analysis.",
            'forecast_30d': "Long-term sentiment prediction for 30 days, considering broader economic/political/cultural factors.",
            'confidence': "How confident the agents are in their analysis, based on data quality and model certainty."
        }
        
        # Add topic-specific explanations
        if topic == 'economic':
            explanations.update({
                'gdp': "Gross Domestic Product - measures economic growth and performance",
                'inflation': "Rate of price increases - affects purchasing power and cost of living",
                'exchange_rate': "USD/MYR rate - impacts imports, exports, and currency value",
                'klci': "FTSE Bursa Malaysia KLCI - stock market index showing investor confidence",
                'oil_price': "Brent crude oil price - affects Malaysia's revenue and fuel costs"
            })
        elif topic == 'political':
            explanations.update({
                'policy_effectiveness': "How well government policies are perceived to be working",
                'governance': "Quality of government administration and decision-making",
                'public_welfare': "Impact of policies on citizen wellbeing and quality of life"
            })
        elif topic == 'cultural':
            explanations.update({
                'social_cohesion': "Level of unity and harmony among different communities",
                'cultural_identity': "Strength of cultural preservation and expression",
                'community_welfare': "Support and resources available to different communities"
            })
        
        return explanations
