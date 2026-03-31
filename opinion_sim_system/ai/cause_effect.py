"""
AI-Powered Cause-Effect Graph Generator

Uses AI to automatically discover and map relationships between:
- Economic indicators
- Sentiment data
- Emotions
- Crisis events
- Service delivery metrics
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional


class CauseEffectGenerator:
    """Generate cause-effect graphs using AI analysis."""
    
    def __init__(self, ai_chatbot):
        self.ai_chatbot = ai_chatbot
    
    def generate_graph(self, dashboard_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate cause-effect graph from dashboard data.
        
        Args:
            dashboard_data: Complete dashboard data including economic, sentiment, etc.
        
        Returns:
            Dictionary with nodes, edges, and insights
        """
        try:
            # Prepare comprehensive context
            context = self._prepare_context(dashboard_data)
            
            # Build AI prompt
            prompt = self._build_prompt(context)
            
            # Get AI response
            response = self.ai_chatbot.chat(prompt)
            
            # Parse JSON from response
            graph_data = self._parse_response(response)
            
            return graph_data
            
        except Exception as e:
            print(f"Cause-effect generation error: {e}")
            return None
    
    def _prepare_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data context for AI analysis."""
        nlp = data.get("nlp_analysis", {})
        
        context = {
            "economic": [],
            "sentiment": nlp.get("overall_sentiment", {}),
            "emotions": nlp.get("emotion_breakdown", {}),
            "alerts": nlp.get("insights", {}).get("alerts", []),
            "crisis_count": len(data.get("crisis", [])),
            "service_count": len(data.get("service_delivery", [])),
            "news_count": len(data.get("sentiment", []))
        }
        
        # Add economic indicators
        econ_data = data.get("economic", [])
        for item in econ_data[:10]:
            context["economic"].append({
                "series_id": item.metadata.get("series_id", item.id),
                "value": item.value,
                "date": item.metadata.get("date", ""),
                "trend": "latest"
            })
        
        return context
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """Build AI prompt for relationship discovery."""
        return f"""Analyze this government dashboard data and identify cause-effect relationships. Return a JSON object with nodes and edges representing the relationships.

{{
  "nodes": [
    {{"id": "unique_id", "label": "Short label (max 20 chars)", "group": "economic|sentiment|emotion|crisis|service", "value": "current value"}}
  ],
  "edges": [
    {{"from": "node_id_1", "to": "node_id_2", "label": "relationship type", "strength": 0.5-1.0}}
  ],
  "insights": ["Key insight about relationship 1", "Key insight about relationship 2", "Policy recommendation"]
}}

**Groups:** economic, sentiment, emotion, crisis, service
**Relationship types:** causes, influences, triggers, correlates_with, leads_to, affects, drives
**Strength:** 0.5 (weak) to 1.0 (strong)

**Data to analyze:**
{json.dumps(context, indent=2)}

**Requirements:**
1. Include ALL economic indicators as nodes (at least 7)
2. Add sentiment node
3. Add emotion nodes (all emotions with >10%)
4. Add crisis alerts if any exist
5. Create realistic edges showing how economic factors influence sentiment
6. Show how sentiment triggers emotions
7. Include at least 10-15 nodes and 15-20 edges
8. Provide 3 actionable insights

Return ONLY the JSON, no other text."""
    
    def _parse_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from AI response."""
        try:
            # Find JSON in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return None
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            return None


def generate_cause_effect_graph(ai_chatbot, dashboard_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Convenience function to generate cause-effect graph.
    
    Args:
        ai_chatbot: Initialized AI chatbot
        dashboard_data: Complete dashboard data
    
    Returns:
        Graph data with nodes, edges, and insights
    """
    generator = CauseEffectGenerator(ai_chatbot)
    return generator.generate_graph(dashboard_data)
