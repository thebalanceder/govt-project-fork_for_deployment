"""
Data Adapter for MiroFish Integration

Converts unified collector output to format expected by MiroFish agents
"""

from typing import Dict, List, Any
from datetime import datetime


class MiroFishDataAdapter:
    """Convert collected data to format expected by MiroFish agents."""
    
    @staticmethod
    def convert_to_agent_format(data: Dict[str, List]) -> Dict[str, Any]:
        """
        Convert unified collector output to MiroFish input format.
        
        Args:
            data: {'economic': [...], 'political': [...], 'cultural': [...]}
            
        Returns:
            Formatted data for agent analysis
        """
        agent_data = {
            'economic': [],
            'political': [],
            'cultural': [],
            'social_media': [],
            'news': []
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
        
        return agent_data
    
    @staticmethod
    def format_discussion_results(discussion_results: Dict) -> Dict[str, Any]:
        """
        Format MiroFish discussion results for API response.
        
        Args:
            discussion_results: Dict of {topic: DiscussionResult}
            
        Returns:
            Formatted results for JSON response
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
                        'confidence': float(forecast['confidence'])
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
                ]
            }
        
        return formatted
