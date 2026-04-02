"""
AI Chatbot Module for CSPOPS

Uses DeepSeek API or OpenRouter API for:
- Answering user questions about data
- Explaining economic indicators
- Providing policy recommendations
- Generating summaries

Supports:
- DeepSeek API (https://platform.deepseek.com/)
- OpenRouter API (https://openrouter.ai/)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class ChatMessage:
    """Represents a chat message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ChatConfig:
    """Configuration for AI chatbot."""
    # DeepSeek API
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    
    # OpenRouter API (alternative)
    openrouter_api_key: str = ""
    openrouter_model: str = "deepseek/deepseek-chat"
    
    # Use OpenRouter instead of DeepSeek direct
    use_openrouter: bool = False
    
    # System prompt
    system_prompt: str = """You are CSPOPS AI Assistant, helping users understand public opinion data.

Your role:
1. Explain economic indicators in simple terms
2. Interpret sentiment analysis results
3. Provide policy recommendations based on data
4. Answer questions about the dashboard

Be concise, clear, and actionable. Use simple language suitable for government officials.

Current data context will be provided with each query."""
    
    @classmethod
    def from_env(cls) -> "ChatConfig":
        """Load configuration from environment variables."""
        return cls(
            deepseek_api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
            use_openrouter=os.getenv("USE_OPENROUTER", "false").lower() == "true"
        )


class AIChatbot:
    """
    AI Chatbot using DeepSeek or OpenRouter API.
    
    Usage:
        config = ChatConfig.from_env()
        chatbot = AIChatbot(config)
        response = chatbot.chat("What does DGS10 mean?")
    """
    
    def __init__(self, config: ChatConfig):
        self.config = config
        self.conversation_history: List[ChatMessage] = []
        self.context: str = None  # Optional context (e.g., 'malaysia')
        
        # API endpoints
        self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def _get_api_key(self) -> str:
        """Get appropriate API key."""
        if self.config.use_openrouter:
            return self.config.openrouter_api_key
        return self.config.deepseek_api_key
    
    def _get_api_url(self) -> str:
        """Get appropriate API endpoint."""
        if self.config.use_openrouter:
            return self.openrouter_url
        return self.deepseek_url
    
    def _get_model(self) -> str:
        """Get appropriate model name."""
        if self.config.use_openrouter:
            return self.config.openrouter_model
        return self.config.deepseek_model
    
    def chat(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Send a message and get AI response.
        
        Args:
            user_message: User's question
            context: Optional data context to include
        
        Returns:
            AI response text
        """
        if not self._get_api_key():
            return "⚠️ API key not configured. Please add DEEPSEEK_API_KEY or OPENROUTER_API_KEY to your .env file."
        
        # Build messages
        messages = [
            {"role": "system", "content": self.config.system_prompt}
        ]
        
        # Add context if provided
        if context:
            context_text = self._format_context(context)
            messages.append({
                "role": "system",
                "content": f"Current data context:\n{context_text}"
            })
        
        # Add conversation history (last 10 messages)
        for msg in self.conversation_history[-10:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Call API
        try:
            response = self._call_api(messages)
            
            # Save to history
            self.conversation_history.append(ChatMessage(role="user", content=user_message))
            self.conversation_history.append(ChatMessage(role="assistant", content=response))
            
            return response
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _call_api(self, messages: List[Dict[str, str]]) -> str:
        """Call the AI API."""
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required. Install: pip install requests")
        
        api_key = self._get_api_key()
        api_url = self._get_api_url()
        model = self._get_model()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        if self.config.use_openrouter:
            headers["HTTP-Referer"] = "https://cspops.gov"
            headers["X-Title"] = "CSPOPS AI Assistant"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format data context for AI."""
        parts = []
        
        if "sentiment" in context:
            sentiment = context["sentiment"]
            if isinstance(sentiment, dict):
                parts.append(f"Overall Sentiment: {sentiment.get('classification', 'N/A')} ({sentiment.get('average_score', 0):.2f})")
        
        if "emotions" in context:
            emotions = context["emotions"]
            if isinstance(emotions, dict) and emotions:
                dominant = max(emotions.items(), key=lambda x: x[1])[0] if emotions else "N/A"
                parts.append(f"Dominant Emotion: {dominant}")
        
        if "economic" in context:
            econ = context["economic"]
            if isinstance(econ, list):
                for item in econ[:5]:
                    # Handle both DataItem objects and dicts
                    if hasattr(item, 'metadata'):
                        # DataItem object
                        series_id = item.metadata.get('series_id', item.id)
                        value = f"{item.value:.2f}" if item.value else "N/A"
                    elif isinstance(item, dict):
                        # Dictionary
                        series_id = item.get('series_id', 'N/A')
                        value = item.get('value', 'N/A')
                    else:
                        continue
                    parts.append(f"{series_id}: {value}")
        
        if "alerts" in context:
            alerts = context["alerts"]
            if isinstance(alerts, list):
                parts.append(f"Active Alerts: {len(alerts)}")
        
        return "\n".join(parts)
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def explain_indicator(self, indicator_id: str) -> str:
        """Get explanation for an economic indicator."""
        explanations = {
            "DGS10": "10-Year Treasury Rate - The interest rate the US government pays to borrow money for 10 years. Higher rates can slow economic growth.",
            "DGS2": "2-Year Treasury Rate - Short-term government borrowing rate. Often reflects Federal Reserve policy expectations.",
            "UNRATE": "Unemployment Rate - Percentage of workforce without jobs but actively seeking employment. Below 4% is considered healthy.",
            "CPIAUCSL": "Consumer Price Index (CPI) - Measures inflation by tracking prices of everyday goods and services.",
            "PCE": "Personal Consumption Expenditures - Total spending by consumers. Major driver of economic growth.",
            "VIXCLS": "VIX Volatility Index - 'Fear gauge' measuring stock market uncertainty. Higher = more volatility.",
            "SP500": "S&P 500 - Stock market index of 500 largest US companies. Reflects overall market health.",
            "CES0000000001": "Total Nonfarm Employment - Number of paid workers in the US. Key jobs indicator.",
            "LNS14000000": "Unemployment Rate (BLS) - Alternative measure from Bureau of Labor Statistics.",
            "CUUR0000SA0": "CPI-U All Items - Consumer Price Index for All Urban Consumers. Primary inflation measure."
        }
        
        explanation = explanations.get(indicator_id, f"{indicator_id} - Economic indicator tracked by government agencies.")
        
        return f"**{indicator_id}**\n\n{explanation}"
    
    def generate_summary(self, data: Dict[str, Any]) -> str:
        """Generate overall summary of dashboard data."""
        prompt = """Based on this dashboard data, provide a 3-paragraph executive summary:

1. Current State: Overall sentiment and key economic indicators
2. Key Concerns: Any alerts or concerning trends
3. Recommendations: 2-3 actionable policy recommendations

Be concise and actionable."""
        
        context = {
            "sentiment": data.get("insights", {}).get("overall_sentiment", {}),
            "emotions": data.get("insights", {}).get("emotion_breakdown", {}),
            "economic": data.get("economic", []),
            "alerts": data.get("insights", {}).get("alerts", [])
        }
        
        return self.chat(prompt, context)


def create_ai_assistant(context: str = None):
    """Create and configure AI assistant.
    
    Args:
        context: Optional context string ('malaysia' or None)
    """
    config = ChatConfig.from_env()
    chatbot = AIChatbot(config)
    
    # Set context if provided (for future use)
    if context:
        chatbot.context = context
    
    return chatbot


if __name__ == "__main__":
    # Test the chatbot
    config = ChatConfig.from_env()
    
    if not config.deepseek_api_key and not config.openrouter_api_key:
        print("⚠️ No API key configured. Set DEEPSEEK_API_KEY or OPENROUTER_API_KEY in .env")
    else:
        chatbot = AIChatbot(config)
        
        # Test questions
        questions = [
            "What does DGS10 mean?",
            "What's the current sentiment?",
            "What policy do you recommend?"
        ]
        
        for q in questions:
            print(f"\nQ: {q}")
            response = chatbot.chat(q)
            print(f"A: {response}")
