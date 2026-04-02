"""
Base Agent Class for CSPOPS Multi-Agent System

All 6 expert agents inherit from this base class
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


@dataclass
class AgentState:
    """Represents an agent's current state and opinion."""
    topic: str  # economic, political, cultural
    sentiment: float  # -1.0 to 1.0
    confidence: float  # 0.0 to 1.0
    key_factors: List[str] = field(default_factory=list)
    reasoning: str = ""
    forecast_7d: float = 0.0
    forecast_30d: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AgentProfile:
    """Agent profile and configuration."""
    name: str
    title: str
    background: str
    perspective: str
    hf_model: str
    influence_weight: float  # 0.5 to 2.0
    expertise_topics: List[str]  # ['economic', 'political', 'cultural']


class BaseAgent(ABC):
    """
    Base class for all expert agents.
    
    Each agent:
    1. Analyzes data from their perspective
    2. Participates in MiroFish discussions
    3. Updates opinions based on other agents
    4. Generates forecasts
    """
    
    def __init__(self, profile: AgentProfile):
        self.profile = profile
        self.state: Optional[AgentState] = None
        self.discussion_history: List[Dict] = []
        
        # Load Hugging Face model
        if TRANSFORMERS_AVAILABLE:
            self.model = self._load_model(profile.hf_model)
        else:
            self.model = None
    
    def _load_model(self, model_name: str):
        """Load Hugging Face model for sentiment/analysis."""
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=model,
                tokenizer=tokenizer,
                truncation=True,
                max_length=512
            )
            
            return sentiment_pipeline
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            return None
    
    @abstractmethod
    def analyze(self, data: Dict[str, Any], topic: str) -> AgentState:
        """
        Analyze data from agent's perspective.
        
        Args:
            data: News, social media, economic data
            topic: 'economic', 'political', or 'cultural'
        
        Returns:
            AgentState with sentiment, reasoning, forecast
        """
        pass
    
    @abstractmethod
    def respond_to(self, other_agent: str, their_state: AgentState) -> str:
        """
        Respond to another agent's position.
        
        Args:
            other_agent: Name of the agent responding to
            their_state: Their current position
        
        Returns:
            Response text
        """
        pass
    
    def update_opinion(self, other_states: List[AgentState], influence_factor: float = 0.1):
        """
        Update opinion based on other agents' positions (MiroFish evolution).
        
        Args:
            other_states: States of other agents
            influence_factor: How much others influence this agent (0.0-1.0)
        """
        if not self.state or not other_states:
            return
        
        # Calculate weighted average of other agents
        weighted_sum = 0.0
        total_weight = 0.0
        
        for other in other_states:
            # Higher influence if topic matches expertise
            weight = 1.0
            if other.topic in self.profile.expertise_topics:
                weight *= 1.2
            
            weighted_sum += other.sentiment * weight
            total_weight += weight
        
        if total_weight > 0:
            others_average = weighted_sum / total_weight
            
            # Move towards others' average (MiroFish evolution)
            old_sentiment = self.state.sentiment
            new_sentiment = old_sentiment + (others_average - old_sentiment) * influence_factor
            
            # Clamp to [-1, 1]
            new_sentiment = max(-1.0, min(1.0, new_sentiment))
            
            self.state.sentiment = new_sentiment
            self.state.confidence *= 0.95  # Slightly reduce confidence after update
    
    def generate_forecast(self, horizon: int = 7) -> float:
        """
        Generate forecast for given horizon.
        
        Args:
            horizon: Days ahead (7 or 30)
        
        Returns:
            Forecasted sentiment (-1.0 to 1.0)
        """
        if not self.state:
            return 0.0
        
        # Simple linear projection (can be enhanced with ML models)
        base = self.state.sentiment
        
        # Adjust based on confidence and trend
        if horizon == 7:
            adjustment = (base * 0.1) * self.state.confidence
        elif horizon == 30:
            adjustment = (base * 0.2) * self.state.confidence
        else:
            adjustment = 0.0
        
        forecast = base + adjustment
        return max(-1.0, min(1.0, forecast))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent state to dictionary."""
        return {
            'name': self.profile.name,
            'title': self.profile.title,
            'topic': self.state.topic if self.state else None,
            'sentiment': self.state.sentiment if self.state else 0.0,
            'confidence': self.state.confidence if self.state else 0.0,
            'key_factors': self.state.key_factors if self.state else [],
            'reasoning': self.state.reasoning if self.state else "",
            'forecast_7d': self.state.forecast_7d if self.state else 0.0,
            'forecast_30d': self.state.forecast_30d if self.state else 0.0,
            'timestamp': self.state.timestamp.isoformat() if self.state else None
        }
    
    def __str__(self) -> str:
        """String representation."""
        if not self.state:
            return f"{self.profile.name} ({self.profile.title}) - No analysis yet"
        
        sentiment_label = "positive" if self.state.sentiment > 0.1 else "negative" if self.state.sentiment < -0.1 else "neutral"
        
        return (f"{self.profile.name} ({self.profile.title}): "
                f"Sentiment {self.state.sentiment:.2f} ({sentiment_label}), "
                f"Confidence {self.state.confidence:.0%}")
