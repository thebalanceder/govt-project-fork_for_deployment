"""
Malaysia-Specific Cause-Effect Graph Generator

Generates cause-effect relationships for Malaysian context:
- Malaysian economic indicators
- Local sentiment factors
- Government policies
- Regional events
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


def generate_malaysia_cause_effect_graph(ai_chatbot, dashboard_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Generate cause-effect graph with Malaysian context.
    
    Args:
        ai_chatbot: AI chatbot instance
        dashboard_data: Dashboard data including economic, news, sentiment data
    
    Returns:
        Graph data with nodes, edges, and insights
    """
    try:
        # Prepare Malaysian context
        context = prepare_malaysian_context(dashboard_data)
        
        # Build AI prompt for Malaysian context
        prompt = build_malaysia_prompt(context)
        
        # Get AI response
        response = ai_chatbot.chat(prompt)
        
        # Parse JSON from response
        graph_data = parse_graph_response(response)
        
        if not graph_data:
            # Fallback to rule-based Malaysian graph
            graph_data = generate_malaysia_rule_based_graph(dashboard_data)
        
        return graph_data
        
    except Exception as e:
        print(f"Malaysia graph generation error: {e}")
        return generate_malaysia_rule_based_graph(dashboard_data)


def prepare_malaysian_context(data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare data context with Malaysian specifics."""
    nlp = data.get('nlp_analysis', {})
    
    context = {
        'country': 'Malaysia',
        'economic': [],
        'sentiment': nlp.get('overall_sentiment', {}),
        'emotions': nlp.get('emotion_breakdown', {}),
        'news_count': len(data.get('news', [])),
        'social_count': len(data.get('social_media', [])),
        'government_count': len(data.get('government', []))
    }
    
    # Add Malaysian economic indicators
    economic = data.get('economic', [])
    for item in economic:
        context['economic'].append({
            'series_id': item.get('metadata', {}).get('series_id', item.get('id', 'unknown')),
            'value': item.get('value'),
            'source': item.get('source', 'unknown'),
            'date': item.get('metadata', {}).get('date', 'unknown')
        })
    
    return context


def build_malaysia_prompt(context: Dict[str, Any]) -> str:
    """Build AI prompt with Malaysian context."""
    return f"""Analyze this MALAYSIAN dashboard data and identify cause-effect relationships specific to Malaysia's economy and public sentiment.

Return a JSON object with this structure:
{{
  "nodes": [
    {{"id": "unique_id", "label": "Short label (max 20 chars)", "group": "economic|sentiment|emotion|crisis|service", "value": "current value"}}
  ],
  "edges": [
    {{"from": "node_id_1", "to": "node_id_2", "label": "relationship type", "strength": 0.5-1.0}}
  ],
  "insights": ["Malaysian-specific insight 1", "Malaysian-specific insight 2", "Policy recommendation for Malaysia"]
}}

**Groups:** economic, sentiment, emotion, crisis, service
**Relationship types:** causes, influences, triggers, correlates_with, leads_to, affects, drives

**Malaysian Data:**
{json.dumps(context, indent=2)}

**Requirements:**
1. Include ALL Malaysian economic indicators (OPR, GDP, CPI, Exchange Rate, KLCI)
2. Add public sentiment node
3. Add emotion nodes (all with >10%)
4. Create realistic edges showing:
   - How Bank Negara policies affect sentiment
   - How exchange rates affect cost of living
   - How economic indicators influence emotions
   - How government policies affect public mood
5. Include 10-15 nodes and 15-20 edges
6. Provide 3 Malaysian-specific insights

Return ONLY the JSON, no other text."""


def parse_graph_response(response: str) -> Optional[Dict[str, Any]]:
    """Parse JSON from AI response."""
    import re
    try:
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return None
    except:
        return None


def generate_malaysia_rule_based_graph(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate rule-based cause-effect graph for Malaysia when AI fails.
    
    Creates realistic Malaysian economic relationships.
    """
    economic = data.get('economic', [])
    nlp = data.get('nlp_analysis', {})
    
    nodes = []
    edges = []
    
    # Add Malaysian economic nodes
    economic_mapping = {
        'MY_OPR': {'label': 'OPR Rate', 'group': 'economic'},
        'MY_GDP': {'label': 'GDP Growth', 'group': 'economic'},
        'MY_CPI': {'label': 'Inflation (CPI)', 'group': 'economic'},
        'MY_UNEMPLOYMENT': {'label': 'Unemployment', 'group': 'economic'},
        'MY_MYR_USD': {'label': 'USD/MYR Rate', 'group': 'economic'},
        'MY_KLCI': {'label': 'Bursa KLCI', 'group': 'economic'},
        'MY_RETAIL_SALES': {'label': 'Retail Sales', 'group': 'economic'},
        'MY_IP': {'label': 'Industrial Prod', 'group': 'economic'}
    }
    
    # Add nodes from actual data
    added_indicators = set()
    for item in economic:
        series_id = item.get('metadata', {}).get('series_id', item.get('id', ''))
        if series_id and series_id not in added_indicators:
            config = economic_mapping.get(series_id, {'label': series_id, 'group': 'economic'})
            value = item.get('value')
            nodes.append({
                'id': series_id,
                'label': config['label'],
                'group': config['group'],
                'value': f"{value:.2f}" if value else 'N/A'
            })
            added_indicators.add(series_id)
    
    # Add sentiment node
    sentiment = nlp.get('overall_sentiment', {})
    sentiment_score = sentiment.get('average_score', 0)
    nodes.append({
        'id': 'MY_SENTIMENT',
        'label': 'Public Sentiment',
        'group': 'sentiment',
        'value': f"{sentiment_score:+.2f}"
    })
    
    # Add emotion nodes
    emotions = nlp.get('emotion_breakdown', {})
    for emotion, score in emotions.items():
        if score > 0.1:  # Only significant emotions
            nodes.append({
                'id': f'EMOTION_{emotion.upper()}',
                'label': emotion.title(),
                'group': 'emotion',
                'value': f"{score*100:.0f}%"
            })
    
    # Add government node
    if data.get('government'):
        nodes.append({
            'id': 'GOV_POLICY',
            'label': 'Govt Policies',
            'group': 'service',
            'value': f"{len(data['government'])} datasets"
        })
    
    # Create realistic Malaysian economic relationships
    # OPR influences everything
    if 'MY_OPR' in added_indicators:
        edges.extend([
            {'from': 'MY_OPR', 'to': 'MY_SENTIMENT', 'label': 'influences', 'strength': 0.8},
            {'from': 'MY_OPR', 'to': 'MY_KLCI', 'label': 'affects', 'strength': 0.7},
            {'from': 'MY_OPR', 'to': 'MY_GDP', 'label': 'drives', 'strength': 0.6}
        ])
    
    # Exchange rate affects sentiment
    if 'MY_MYR_USD' in added_indicators:
        edges.append({
            'from': 'MY_MYR_USD',
            'to': 'MY_SENTIMENT',
            'label': 'influences',
            'strength': 0.7
        })
    
    # Inflation affects sentiment strongly
    if 'MY_CPI' in added_indicators:
        edges.extend([
            {'from': 'MY_CPI', 'to': 'MY_SENTIMENT', 'label': 'influences', 'strength': 0.9},
            {'from': 'MY_CPI', 'to': 'MY_OPR', 'label': 'influences', 'strength': 0.8}
        ])
    
    # GDP affects everything
    if 'MY_GDP' in added_indicators:
        edges.extend([
            {'from': 'MY_GDP', 'to': 'MY_SENTIMENT', 'label': 'drives', 'strength': 0.8},
            {'from': 'MY_GDP', 'to': 'MY_UNEMPLOYMENT', 'label': 'correlates_with', 'strength': 0.7}
        ])
    
    # KLCI reflects sentiment
    if 'MY_KLCI' in added_indicators:
        edges.append({
            'from': 'MY_KLCI',
            'to': 'MY_SENTIMENT',
            'label': 'correlates_with',
            'strength': 0.6
        })
    
    # Sentiment triggers emotions
    edges.append({
        'from': 'MY_SENTIMENT',
        'to': 'EMOTION_JOY' if 'EMOTION_JOY' in [n['id'] for n in nodes] else 'MY_SENTIMENT',
        'label': 'triggers',
        'strength': 0.8
    })
    
    # Government policies affect economy
    if any(n['id'] == 'GOV_POLICY' for n in nodes):
        edges.extend([
            {'from': 'GOV_POLICY', 'to': 'MY_GDP', 'label': 'influences', 'strength': 0.7},
            {'from': 'GOV_POLICY', 'to': 'MY_SENTIMENT', 'label': 'affects', 'strength': 0.8}
        ])
    
    # Generate Malaysian-specific insights
    insights = generate_malaysian_insights(data, nodes, edges)
    
    return {
        'nodes': nodes,
        'edges': edges,
        'insights': insights
    }


def generate_malaysian_insights(data: Dict[str, Any], nodes: List[Dict], edges: List[Dict]) -> List[str]:
    """Generate Malaysian-specific insights."""
    insights = []
    
    economic = data.get('economic', [])
    nlp = data.get('nlp_analysis', {})
    
    # Check OPR
    opr = next((item for item in economic if item.get('metadata', {}).get('series_id') == 'MY_OPR'), None)
    if opr and opr.get('value'):
        if opr['value'] >= 3.5:
            insights.append("High OPR at {:.2f}% may slow economic growth but control inflation - monitor impact on consumer spending".format(opr['value']))
        elif opr['value'] <= 2.5:
            insights.append("Low OPR at {:.2f}% supports economic growth but may weaken Ringgit - watch for capital outflow".format(opr['value']))
        else:
            insights.append("OPR at {:.2f}% is balanced - current monetary policy stance is appropriate".format(opr['value']))
    
    # Check exchange rate
    usd_myr = next((item for item in economic if item.get('metadata', {}).get('series_id') == 'MY_MYR_USD'), None)
    if usd_myr and usd_myr.get('value'):
        if usd_myr['value'] > 4.5:
            insights.append("Weak Ringgit ({:.2f} vs USD) increases import costs - consider hedging strategies for essential imports".format(usd_myr['value']))
        else:
            insights.append("Ringgit at {:.2f} vs USD is competitive for exports - Malaysian exporters benefit".format(usd_myr['value']))
    
    # Check sentiment
    sentiment = nlp.get('overall_sentiment', {})
    if sentiment.get('average_score', 0) > 0.1:
        insights.append("Positive public sentiment ({:.2f}) indicates confidence in current government policies - good time for policy announcements".format(sentiment['average_score']))
    elif sentiment.get('average_score', 0) < -0.1:
        insights.append("Negative public sentiment ({:.2f}) suggests dissatisfaction - consider public engagement initiatives".format(sentiment['average_score']))
    else:
        insights.append("Neutral public sentiment indicates wait-and-see attitude - clear communication on policies needed")
    
    # Check emotions
    emotions = nlp.get('emotion_breakdown', {})
    if emotions.get('joy', 0) > 0.3:
        insights.append("High joy levels ({:.0f}%) reflect public satisfaction - leverage positive mood for national initiatives".format(emotions['joy'] * 100))
    if emotions.get('anger', 0) > 0.2:
        insights.append("Elevated anger ({:.0f}%) suggests public frustration - identify and address key pain points urgently".format(emotions['anger'] * 100))
    if emotions.get('fear', 0) > 0.2:
        insights.append("High fear levels ({:.0f}%) indicate economic anxiety - provide reassurance on job security and cost of living".format(emotions['fear'] * 100))
    
    # If no specific insights, add general ones
    if not insights:
        insights = [
            "Malaysian economic indicators show mixed signals - monitor closely",
            "Public sentiment stable - maintain current policy direction",
            "Consider targeted interventions for cost of living concerns"
        ]
    
    return insights[:3]  # Return top 3 insights
