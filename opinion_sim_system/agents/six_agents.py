"""
The 6 Expert Agents for CSPOPS Malaysia

Each agent represents a different expert perspective
"""

from .base_agent import BaseAgent, AgentProfile, AgentState
from typing import Any, Dict, List


# ============================================================================
# Agent 1: Dr. Lim Wei Chen - Chief Economist
# ============================================================================

class EconomistAgent(BaseAgent):
    """
    Dr. Lim Wei Chen - Chief Economist
    
    Background: Former Bank Negara economist, 20+ years experience
    Perspective: Economic growth, stability, inflation control
    Model: FinBERT (financial sentiment analysis)
    """
    
    def __init__(self):
        profile = AgentProfile(
            name="Dr. Lim Wei Chen",
            title="Chief Economist",
            background="Former Bank Negara economist, 20+ years experience",
            perspective="Economic growth, stability, inflation control",
            hf_model="prosusai/finbert",
            influence_weight=1.2,
            expertise_topics=['economic']
        )
        super().__init__(profile)
    
    def analyze(self, data: Dict[str, Any], topic: str) -> AgentState:
        """Analyze economic data from economist perspective."""

        if topic != 'economic':
            # Lower confidence for non-economic topics
            base_confidence = 0.6
        else:
            base_confidence = 0.85

        # Extract economic indicators (data is a flat list of items)
        economic_data = data.get('economic', [])
        
        # Categorize items by keywords in text/title
        gdp_data = []
        inflation_data = []
        employment_data = []
        
        for item in economic_data:
            if isinstance(item, dict):
                text = (item.get('text', '') + ' ' + item.get('title', '')).lower()
                if any(kw in text for kw in ['gdp', 'growth', 'economic growth']):
                    gdp_data.append(item)
                elif any(kw in text for kw in ['inflation', 'cpi', 'price']):
                    inflation_data.append(item)
                elif any(kw in text for kw in ['employment', 'job', 'unemployment', 'labor']):
                    employment_data.append(item)
                else:
                    # Default to gdp_data for general economic indicators
                    gdp_data.append(item)

        # Analyze sentiment using model if available
        economic_texts = []
        for item in economic_data[:5]:
            if isinstance(item, dict):
                economic_texts.append(item.get('text', ''))
        
        sentiment_score = 0.0
        key_factors = []
        reasoning = []
        
        if self.model and economic_texts:
            try:
                results = self.model(economic_texts[:10])
                for result in results:
                    label = result['label']
                    score = result['score']
                    if label in ['POSITIVE', 'pos']:
                        sentiment_score += score
                    else:
                        sentiment_score -= score
                
                sentiment_score /= len(results)
            except:
                sentiment_score = 0.0
        
        # Key factors based on data
        if gdp_data:
            key_factors.append("GDP growth")
            reasoning.append(f"GDP indicators: {len(gdp_data)} data points")
        
        if inflation_data:
            key_factors.append("Inflation control")
            reasoning.append(f"Inflation data: {len(inflation_data)} indicators")
        
        if employment_data:
            key_factors.append("Employment")
            reasoning.append(f"Employment metrics: {len(employment_data)} indicators")
        
        # Generate forecasts
        forecast_7d = sentiment_score + (sentiment_score * 0.1)
        forecast_30d = sentiment_score + (sentiment_score * 0.2)
        
        self.state = AgentState(
            topic=topic,
            sentiment=sentiment_score,
            confidence=base_confidence,
            key_factors=key_factors,
            reasoning="; ".join(reasoning) if reasoning else "Economic analysis based on available indicators",
            forecast_7d=max(-1.0, min(1.0, forecast_7d)),
            forecast_30d=max(-1.0, min(1.0, forecast_30d))
        )
        
        return self.state
    
    def respond_to(self, other_agent: str, their_state: AgentState) -> str:
        """Respond to another agent from economist perspective."""
        
        if their_state.topic == 'economic':
            return (f"From an economic perspective, I see {their_state.sentiment:.2f} sentiment. "
                    f"Key considerations: GDP growth, inflation expectations, and employment trends. "
                    f"My analysis suggests {'optimism' if their_state.sentiment > 0 else 'caution'}.")
        else:
            return (f"While {other_agent}'s focus is on {their_state.topic} matters, "
                    f"the economic implications are significant. "
                    f"Economic stability underpins all policy decisions.")


# ============================================================================
# Agent 2: Datin Sri Aisha - Policy Advisor
# ============================================================================

class PolicyAgent(BaseAgent):
    """
    Datin Sri Aisha binti Abdullah - Policy Advisor
    
    Background: Former minister, policy think tank director
    Perspective: Governance, public welfare, policy effectiveness
    Model: BERT Go Emotions
    """
    
    def __init__(self):
        profile = AgentProfile(
            name="Datin Sri Aisha binti Abdullah",
            title="Policy Advisor",
            background="Former minister, policy think tank director",
            perspective="Governance, public welfare, policy effectiveness",
            hf_model="joeddav/distilbert-base-uncased-go-emotions-student",
            influence_weight=1.1,
            expertise_topics=['political', 'cultural']
        )
        super().__init__(profile)
    
    def analyze(self, data: Dict[str, Any], topic: str) -> AgentState:
        """Analyze from policy and governance perspective."""

        if topic == 'political':
            base_confidence = 0.85
        elif topic == 'cultural':
            base_confidence = 0.75
        else:
            base_confidence = 0.65

        # Extract policy-related data (data is a flat list of items)
        policy_news = data.get('political', [])
        social_data = data.get('cultural', [])

        sentiment_score = 0.0
        key_factors = []
        reasoning = []

        # Analyze policy news
        policy_texts = [item.get('text', '') for item in policy_news[:10] if isinstance(item, dict)]
        
        if self.model and policy_texts:
            try:
                results = self.model(policy_texts[:10])
                for result in results:
                    label = result['label']
                    score = result['score']
                    sentiment_score += score if 'positive' in label.lower() else -score
                
                sentiment_score /= max(len(results), 1)
            except:
                sentiment_score = 0.0
        
        key_factors = ["Policy effectiveness", "Public welfare", "Governance"]
        reasoning.append(f"Analyzed {len(policy_news)} policy-related items")
        
        forecast_7d = sentiment_score + (sentiment_score * 0.08)
        forecast_30d = sentiment_score + (sentiment_score * 0.15)
        
        self.state = AgentState(
            topic=topic,
            sentiment=sentiment_score,
            confidence=base_confidence,
            key_factors=key_factors,
            reasoning="; ".join(reasoning),
            forecast_7d=max(-1.0, min(1.0, forecast_7d)),
            forecast_30d=max(-1.0, min(1.0, forecast_30d))
        )
        
        return self.state
    
    def respond_to(self, other_agent: str, their_state: AgentState) -> str:
        """Respond from policy perspective."""
        return (f"Considering {other_agent}'s analysis on {their_state.topic} matters, "
                f"we must ensure policy frameworks support positive outcomes. "
                f"Public welfare remains the paramount consideration.")


# ============================================================================
# Agent 3: Encik Razak - Business Leader
# ============================================================================

class BusinessAgent(BaseAgent):
    """
    Encik Razak bin Ibrahim - Business Leader
    
    Background: CEO of multinational corporation, FMM council member
    Perspective: Industry growth, investment climate, competitiveness
    Model: FinBERT
    """
    
    def __init__(self):
        profile = AgentProfile(
            name="Encik Razak bin Ibrahim",
            title="Business Leader",
            background="CEO of multinational corporation, FMM council member",
            perspective="Industry growth, investment climate, competitiveness",
            hf_model="prosusai/finbert",
            influence_weight=1.1,
            expertise_topics=['economic']
        )
        super().__init__(profile)
    
    def analyze(self, data: Dict[str, Any], topic: str) -> AgentState:
        """Analyze from business and investment perspective."""
        
        base_confidence = 0.80 if topic == 'economic' else 0.60
        
        business_news = data.get('economic', [])
        
        sentiment_score = 0.0
        key_factors = ["Investment climate", "Business confidence", "Competitiveness"]
        reasoning = []
        
        business_texts = [item.get('text', '') for item in business_news[:10] if isinstance(item, dict)]
        
        if self.model and business_texts:
            try:
                results = self.model(business_texts[:10])
                for result in results:
                    label = result['label']
                    score = result['score']
                    sentiment_score += score if 'POSITIVE' in label else -score
                
                sentiment_score /= max(len(results), 1)
            except:
                sentiment_score = 0.0
        
        reasoning.append(f"Business indicators from {len(business_news)} sources")
        
        forecast_7d = sentiment_score + (sentiment_score * 0.12)
        forecast_30d = sentiment_score + (sentiment_score * 0.18)
        
        self.state = AgentState(
            topic=topic,
            sentiment=sentiment_score,
            confidence=base_confidence,
            key_factors=key_factors,
            reasoning="; ".join(reasoning),
            forecast_7d=max(-1.0, min(1.0, forecast_7d)),
            forecast_30d=max(-1.0, min(1.0, forecast_30d))
        )
        
        return self.state
    
    def respond_to(self, other_agent: str, their_state: AgentState) -> str:
        """Respond from business perspective."""
        return (f"From the business community's viewpoint, {other_agent}'s analysis on "
                f"{their_state.topic} issues affects investment decisions. "
                f"Business confidence is key to economic growth.")


# ============================================================================
# Agent 4: Dr. Muthu - Sociologist
# ============================================================================

class SociologistAgent(BaseAgent):
    """
    Dr. Muthu a/l Krishnan - Sociologist
    
    Background: UM sociology professor, social researcher
    Perspective: Social cohesion, cultural identity, inequality
    Model: RoBERTa Sentiment
    """
    
    def __init__(self):
        profile = AgentProfile(
            name="Dr. Muthu a/l Krishnan",
            title="Sociologist",
            background="UM sociology professor, social researcher",
            perspective="Social cohesion, cultural identity, inequality",
            hf_model="cardiffnlp/twitter-roberta-base-sentiment",
            influence_weight=1.2,
            expertise_topics=['cultural', 'political']
        )
        super().__init__(profile)
    
    def analyze(self, data: Dict[str, Any], topic: str) -> AgentState:
        """Analyze from sociological perspective."""
        
        base_confidence = 0.82 if topic == 'cultural' else 0.70
        
        social_data = data.get('cultural', [])
        social_media = data.get('social_media', [])
        
        sentiment_score = 0.0
        key_factors = ["Social cohesion", "Cultural identity", "Community welfare"]
        reasoning = []
        
        social_texts = [item.get('text', '') for item in social_data[:10] if isinstance(item, dict)]
        
        if self.model and social_texts:
            try:
                results = self.model(social_texts[:10])
                for result in results:
                    label = result['label'].lower()
                    score = result['score']
                    if 'positive' in label:
                        sentiment_score += score
                    elif 'negative' in label:
                        sentiment_score -= score
                
                sentiment_score /= max(len(results), 1)
            except:
                sentiment_score = 0.0
        
        reasoning.append(f"Social analysis from {len(social_data)} cultural indicators")
        
        forecast_7d = sentiment_score + (sentiment_score * 0.09)
        forecast_30d = sentiment_score + (sentiment_score * 0.16)
        
        self.state = AgentState(
            topic=topic,
            sentiment=sentiment_score,
            confidence=base_confidence,
            key_factors=key_factors,
            reasoning="; ".join(reasoning),
            forecast_7d=max(-1.0, min(1.0, forecast_7d)),
            forecast_30d=max(-1.0, min(1.0, forecast_30d))
        )
        
        return self.state
    
    def respond_to(self, other_agent: str, their_state: AgentState) -> str:
        """Respond from sociological perspective."""
        return (f"From a sociological lens, {other_agent}'s {their_state.topic} analysis "
                f"must consider social cohesion and community impact. "
                f"Cultural factors significantly influence public sentiment.")


# ============================================================================
# Agent 5: Ms. Wong - International Relations Expert
# ============================================================================

class IRAgent(BaseAgent):
    """
    Ms. Wong Li Ming - International Relations Expert
    
    Background: Former diplomat, ASEAN specialist
    Perspective: Geopolitics, trade relations, regional stability
    Model: XLM-RoBERTa (multilingual)
    """
    
    def __init__(self):
        profile = AgentProfile(
            name="Ms. Wong Li Ming",
            title="International Relations Expert",
            background="Former diplomat, ASEAN specialist",
            perspective="Geopolitics, trade relations, regional stability",
            hf_model="xlm-roberta-base",
            influence_weight=1.0,
            expertise_topics=['political', 'economic']
        )
        super().__init__(profile)
    
    def analyze(self, data: Dict[str, Any], topic: str) -> AgentState:
        """Analyze from international relations perspective."""
        
        base_confidence = 0.78 if topic in ['political', 'economic'] else 0.65
        
        political_news = data.get('political', [])
        
        sentiment_score = 0.05  # Slight positive bias for stability
        key_factors = ["Regional stability", "Trade relations", "Diplomatic ties"]
        reasoning = []
        
        ir_texts = [item.get('text', '') for item in political_news[:10] if isinstance(item, dict)]
        
        if self.model and ir_texts:
            try:
                results = self.model(ir_texts[:10])
                for result in results:
                    label = result['label']
                    score = result['score']
                    sentiment_score += score if 'positive' in label.lower() else -score
                
                sentiment_score /= max(len(results), 1)
            except:
                pass
        
        reasoning.append(f"IR analysis from {len(political_news)} geopolitical sources")
        
        forecast_7d = sentiment_score + (sentiment_score * 0.07)
        forecast_30d = sentiment_score + (sentiment_score * 0.14)
        
        self.state = AgentState(
            topic=topic,
            sentiment=sentiment_score,
            confidence=base_confidence,
            key_factors=key_factors,
            reasoning="; ".join(reasoning),
            forecast_7d=max(-1.0, min(1.0, forecast_7d)),
            forecast_30d=max(-1.0, min(1.0, forecast_30d))
        )
        
        return self.state
    
    def respond_to(self, other_agent: str, their_state: AgentState) -> str:
        """Respond from IR perspective."""
        return (f"From an international perspective, {other_agent}'s analysis on "
                f"{their_state.topic} matters affects Malaysia's regional standing. "
                f"Regional stability and trade relations are interconnected.")


# ============================================================================
# Agent 6: Ahmad - Public Representative
# ============================================================================

class PublicAgent(BaseAgent):
    """
    Ahmad bin Hassan - Public Representative
    
    Background: Community leader, grassroots organizer
    Perspective: Citizen concerns, cost of living, quality of life
    Model: DistilBERT Sentiment
    """
    
    def __init__(self):
        profile = AgentProfile(
            name="Ahmad bin Hassan",
            title="Public Representative",
            background="Community leader, grassroots organizer",
            perspective="Citizen concerns, cost of living, quality of life",
            hf_model="distilbert-base-uncased-finetuned-sst-2-english",
            influence_weight=1.1,
            expertise_topics=['cultural', 'economic', 'political']
        )
        super().__init__(profile)
    
    def analyze(self, data: Dict[str, Any], topic: str) -> AgentState:
        """Analyze from public/citizen perspective."""
        
        base_confidence = 0.75  # Moderate confidence
        
        social_media = data.get('social_media', [])
        news = data.get('news', [])
        
        sentiment_score = 0.0
        key_factors = ["Cost of living", "Quality of life", "Public services"]
        reasoning = []
        
        public_texts = []
        for item in social_media[:20]:
            if isinstance(item, dict):
                public_texts.append(item.get('text', ''))
        
        if self.model and public_texts:
            try:
                results = self.model(public_texts[:20])
                for result in results:
                    label = result['label']
                    score = result['score']
                    sentiment_score += score if label == 'POSITIVE' else -score
                
                sentiment_score /= max(len(results), 1)
            except:
                sentiment_score = 0.0
        
        reasoning.append(f"Public sentiment from {len(social_media)} social media posts")
        
        forecast_7d = sentiment_score + (sentiment_score * 0.06)
        forecast_30d = sentiment_score + (sentiment_score * 0.12)
        
        self.state = AgentState(
            topic=topic,
            sentiment=sentiment_score,
            confidence=base_confidence,
            key_factors=key_factors,
            reasoning="; ".join(reasoning),
            forecast_7d=max(-1.0, min(1.0, forecast_7d)),
            forecast_30d=max(-1.0, min(1.0, forecast_30d))
        )
        
        return self.state
    
    def respond_to(self, other_agent: str, their_state: AgentState) -> str:
        """Respond from public perspective."""
        return (f"Speaking for the rakyat, {other_agent}'s {their_state.topic} analysis "
                f"must reflect ground-level concerns. "
                f"Cost of living and quality of life are top priorities for citizens.")


# ============================================================================
# Factory Function
# ============================================================================

def create_all_agents() -> List[BaseAgent]:
    """Create all 6 expert agents."""
    return [
        EconomistAgent(),
        PolicyAgent(),
        BusinessAgent(),
        SociologistAgent(),
        IRAgent(),
        PublicAgent()
    ]
