"""
Enhanced AI Agent for Deep Data Analysis

Provides:
- Deep trend analysis with explanations
- Multi-factor correlation analysis
- Predictive modeling with confidence scores
- Detailed "why" and "what" explanations
- Malaysian economic context awareness
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta


class MalaysiaEconomicAI:
    """
    AI Agent specialized in Malaysian economic analysis.
    
    Provides deep analysis with detailed explanations of:
    - WHY trends are happening
    - WHAT to expect
    - HOW factors are correlated
    - WHICH actions to take
    """
    
    def __init__(self):
        self.malaysian_context = {
            'major_exports': ['palm oil', 'petroleum', 'electronics', 'rubber'],
            'major_imports': ['machinery', 'chemicals', 'food', 'manufactured goods'],
            'key_trading_partners': ['Singapore', 'China', 'USA', 'Japan', 'Thailand'],
            'economic_sectors': {
                'services': 54,  # % of GDP
                'manufacturing': 23,
                'agriculture': 8,
                'construction': 4,
                'mining': 6,
                'others': 5
            },
            'population': 33.0,  # million
            'currency': 'MYR'
        }
    
    def analyze_economic_trends(self, economic_data: List[Dict]) -> Dict[str, Any]:
        """
        Deep analysis of economic trends with detailed explanations.
        
        Returns:
            Comprehensive analysis with WHY, WHAT, HOW explanations
        """
        analysis = {
            'overview': {},
            'indicators': {},
            'correlations': {},
            'predictions': {},
            'recommendations': [],
            'detailed_explanations': []
        }
        
        # Group data by series
        by_series = {}
        for item in economic_data:
            series_id = item.get('metadata', {}).get('series_id', item.get('id', 'unknown'))
            if series_id not in by_series:
                by_series[series_id] = []
            by_series[series_id].append(item)
        
        # Analyze each indicator
        for series_id, items in by_series.items():
            indicator_analysis = self._analyze_single_indicator(series_id, items)
            analysis['indicators'][series_id] = indicator_analysis
            analysis['detailed_explanations'].extend(indicator_analysis['explanations'])
        
        # Cross-indicator correlation analysis
        analysis['correlations'] = self._analyze_correlations(by_series)
        
        # Generate predictions
        analysis['predictions'] = self._generate_predictions(by_series)
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        # Overall overview
        analysis['overview'] = self._generate_overview(analysis)
        
        return analysis
    
    def _analyze_single_indicator(self, series_id: str, items: List[Dict]) -> Dict[str, Any]:
        """Analyze a single economic indicator with deep explanations."""
        
        # Sort by date
        sorted_items = sorted(items, key=lambda x: x.get('timestamp', ''))
        values = [item.get('value') for item in sorted_items if item.get('value') is not None]
        
        if not values or len(values) < 2:
            return {'error': 'Insufficient data'}
        
        current = values[-1]
        previous = values[-2] if len(values) >= 2 else values[0]
        oldest = values[0]
        
        # Calculate changes
        change_1d = ((current - previous) / previous * 100) if previous else 0
        change_period = ((current - oldest) / oldest * 100) if oldest else 0
        
        # Determine trend
        if change_period > 5:
            trend = 'strong_uptrend'
        elif change_period > 2:
            trend = 'uptrend'
        elif change_period < -5:
            trend = 'strong_downtrend'
        elif change_period < -2:
            trend = 'downtrend'
        else:
            trend = 'stable'
        
        # Calculate volatility
        avg = sum(values) / len(values)
        variance = sum((x - avg) ** 2 for x in values) / len(values)
        volatility = variance ** 0.5
        volatility_level = 'high' if volatility > avg * 0.05 else 'moderate' if volatility > avg * 0.02 else 'low'
        
        # Generate detailed explanations
        explanations = self._generate_indicator_explanations(series_id, current, change_1d, change_period, trend, volatility_level)
        
        return {
            'current': current,
            'previous': previous,
            'change_1d': change_1d,
            'change_period': change_period,
            'trend': trend,
            'volatility': volatility,
            'volatility_level': volatility_level,
            'data_points': len(values),
            'min': min(values),
            'max': max(values),
            'average': avg,
            'explanations': explanations
        }
    
    def _generate_indicator_explanations(self, series_id: str, current: float, 
                                        change_1d: float, change_period: float,
                                        trend: str, volatility_level: str) -> List[Dict[str, str]]:
        """Generate detailed WHY and WHAT explanations for an indicator."""
        
        explanations = []
        
        # USD/MYR explanations
        if series_id == 'MY_MYR_USD':
            explanations.append({
                'type': 'WHAT',
                'title': 'Current Exchange Rate Status',
                'content': f'USD/MYR is currently at {current:.2f}, representing a {change_1d:+.2f}% change from yesterday '
                          f'and {change_period:+.2f}% over the analysis period. This indicates the Ringgit is '
                          f'{"strengthening" if change_period < 0 else "weakening"} against the US Dollar.'
            })
            
            explanations.append({
                'type': 'WHY',
                'title': 'Factors Driving Exchange Rate',
                'content': f'The {"strengthening" if change_period < 0 else "weakening"} trend in USD/MYR is influenced by: '
                          f'1) Oil prices (Malaysia is a net oil exporter, higher oil prices strengthen Ringgit), '
                          f'2) US Federal Reserve policy (higher US rates strengthen Dollar), '
                          f'3) Malaysia\'s trade balance (surplus strengthens Ringgit), '
                          f'4) Foreign investment flows into Malaysian markets.'
            })
            
            explanations.append({
                'type': 'IMPACT',
                'title': 'Economic Impact',
                'content': f'A {"stronger" if change_period < 0 else "weaker"} Ringgit affects Malaysia by: '
                          f'{"Making imports cheaper and reducing inflation pressure, but making exports less competitive." if change_period < 0 else "Making exports more competitive and boosting export-oriented sectors, but increasing import costs and inflation pressure."}'
            })
        
        # KLCI explanations
        elif series_id == 'MY_KLCI':
            explanations.append({
                'type': 'WHAT',
                'title': 'Stock Market Performance',
                'content': f'FTSE Bursa Malaysia KLCI is at {current:.2f}, {"up" if change_period > 0 else "down"} {abs(change_period):.2f}% '
                          f'over the period. This {"positive" if change_period > 0 else "negative"} performance reflects '
                          f'{"investor confidence in Malaysian equities" if change_period > 0 else "investor concerns about market conditions"}.'
            })
            
            explanations.append({
                'type': 'WHY',
                'title': 'Market Drivers',
                'content': f'KLCI performance is driven by: '
                          f'1) Corporate earnings of constituent companies (banks, plantations, utilities), '
                          f'2) Foreign fund flows (net buying supports KLCI), '
                          f'3) Regional market sentiment (especially ASEAN markets), '
                          f'4) Commodity prices (palm oil, petroleum affect related stocks), '
                          f'5) Government policy announcements affecting specific sectors.'
            })
            
            explanations.append({
                'type': 'IMPACT',
                'title': 'Wealth Effect',
                'content': f'A {"rising" if change_period > 0 else "falling"} KLCI creates {"a positive wealth effect, boosting consumer confidence and spending" if change_period > 0 else "a negative wealth effect, potentially reducing consumer confidence and spending"}. '
                          f'This affects the broader Malaysian economy through consumer spending channels.'
            })
        
        # Oil price explanations
        elif series_id == 'MY_OIL':
            explanations.append({
                'type': 'WHAT',
                'title': 'Oil Price Status',
                'content': f'Brent Crude Oil is at ${current:.2f}/barrel, {"up" if change_period > 0 else "down"} {abs(change_period):.2f}% '
                          f'over the period. As a net oil exporter, Malaysia {"benefits" if change_period > 0 else "faces challenges"} '
                          f'from {"higher" if change_period > 0 else "lower"} oil prices.'
            })
            
            explanations.append({
                'type': 'WHY',
                'title': 'Oil Price Drivers',
                'content': f'Oil prices are influenced by: '
                          f'1) OPEC+ production decisions (supply management), '
                          f'2) Global economic growth expectations (demand outlook), '
                          f'3) Geopolitical tensions (supply disruption risks), '
                          f'4) US inventory levels and shale production, '
                          f'5) Currency movements (oil priced in USD).'
            })
            
            explanations.append({
                'type': 'IMPACT',
                'title': 'Impact on Malaysian Economy',
                'content': f'{"Higher oil prices benefit Malaysia through:" if change_period > 0 else "Lower oil prices challenge Malaysia through:"} '
                          f'1) {"Increased" if change_period > 0 else "Reduced"} government revenue (Petronas dividends, petroleum tax), '
                          f'2) {"Improved" if change_period > 0 else "Worsened"} trade balance, '
                          f'3) {"Stronger" if change_period > 0 else "Weaker"} Ringgit exchange rate, '
                          f'4) {"Higher" if change_period > 0 else "Lower"} inflation pressure (fuel prices).'
            })
        
        # Add volatility explanation
        explanations.append({
            'type': 'RISK',
            'title': 'Volatility Assessment',
            'content': f'Volatility is {volatility_level}, indicating {"significant price swings and higher uncertainty" if volatility_level == "high" else "moderate price movements" if volatility_level == "moderate" else "stable price movements with low uncertainty"}. '
                      f'This affects {"risk management strategies and hedging decisions" if volatility_level == "high" else "planning and forecasting accuracy"}.'
        })
        
        return explanations
    
    def _analyze_correlations(self, by_series: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Analyze correlations between different economic indicators."""
        
        correlations = {
            'pairs': [],
            'insights': []
        }
        
        # Get time series for each indicator
        series_data = {}
        for series_id, items in by_series.items():
            sorted_items = sorted(items, key=lambda x: x.get('timestamp', ''))
            values = [item.get('value') for item in sorted_items if item.get('value') is not None]
            if len(values) >= 10:  # Need minimum data points
                series_data[series_id] = values
        
        # Calculate pairwise correlations (simplified)
        series_ids = list(series_data.keys())
        for i in range(len(series_ids)):
            for j in range(i + 1, len(series_ids)):
                id1, id2 = series_ids[i], series_ids[j]
                values1, values2 = series_data[id1], series_data[id2]
                
                # Use minimum length
                min_len = min(len(values1), len(values2))
                if min_len >= 10:
                    # Calculate correlation coefficient
                    avg1 = sum(values1[:min_len]) / min_len
                    avg2 = sum(values2[:min_len]) / min_len
                    
                    numerator = sum((values1[k] - avg1) * (values2[k] - avg2) for k in range(min_len))
                    denom1 = sum((values1[k] - avg1) ** 2 for k in range(min_len)) ** 0.5
                    denom2 = sum((values2[k] - avg2) ** 2 for k in range(min_len)) ** 0.5
                    
                    if denom1 > 0 and denom2 > 0:
                        correlation = numerator / (denom1 * denom2)
                        
                        correlations['pairs'].append({
                            'pair': f'{id1} ↔ {id2}',
                            'correlation': correlation,
                            'strength': 'strong' if abs(correlation) > 0.7 else 'moderate' if abs(correlation) > 0.4 else 'weak'
                        })
                        
                        # Add insight
                        if abs(correlation) > 0.6:
                            correlations['insights'].append({
                                'type': 'CORRELATION',
                                'content': f'{id1} and {id2} show {"positive" if correlation > 0 else "negative"} correlation ({correlation:.2f}). '
                                          f'This suggests {"they tend to move in the same direction" if correlation > 0 else "they tend to move in opposite directions"}.'
                            })
        
        return correlations
    
    def _generate_predictions(self, by_series: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Generate predictions with confidence scores and explanations."""
        
        predictions = {
            'short_term': {},  # 1-7 days
            'medium_term': {},  # 1-4 weeks
            'indicators': []
        }
        
        for series_id, items in by_series.items():
            sorted_items = sorted(items, key=lambda x: x.get('timestamp', ''))
            values = [item.get('value') for item in sorted_items if item.get('value') is not None]
            
            if len(values) < 5:
                continue
            
            # Simple trend extrapolation (in production, use ML models)
            current = values[-1]
            
            # Calculate recent trend
            recent_avg = sum(values[-5:]) / 5
            older_avg = sum(values[-10:-5]) / 5 if len(values) >= 10 else values[0]
            
            trend_rate = (recent_avg - older_avg) / older_avg if older_avg else 0
            
            # Generate predictions
            short_term_pred = current * (1 + trend_rate * 0.5)  # Conservative
            medium_term_pred = current * (1 + trend_rate * 2)  # Extended
            
            # Determine confidence based on volatility
            avg = sum(values) / len(values)
            volatility = sum((x - avg) ** 2 for x in values) / len(values) ** 0.5
            confidence = 'high' if volatility < avg * 0.02 else 'moderate' if volatility < avg * 0.05 else 'low'
            
            predictions['indicators'].append({
                'series_id': series_id,
                'current': current,
                'short_term': {
                    'prediction': short_term_pred,
                    'change_pct': ((short_term_pred - current) / current * 100),
                    'confidence': confidence,
                    'timeframe': '1-7 days'
                },
                'medium_term': {
                    'prediction': medium_term_pred,
                    'change_pct': ((medium_term_pred - current) / current * 100),
                    'confidence': 'moderate' if confidence == 'high' else 'low',
                    'timeframe': '1-4 weeks'
                }
            })
        
        return predictions
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on analysis."""
        
        recommendations = []
        
        # Check each indicator
        for series_id, indicator in analysis.get('indicators', {}).items():
            if 'error' in indicator:
                continue
            
            trend = indicator.get('trend', 'stable')
            volatility = indicator.get('volatility_level', 'moderate')
            
            # USD/MYR recommendations
            if series_id == 'MY_MYR_USD':
                if trend == 'strong_downtrend':
                    recommendations.append({
                        'priority': 'HIGH',
                        'category': 'Currency',
                        'recommendation': 'Consider hedging USD exposure',
                        'rationale': f'Ringgit showing strong strengthening trend ({trend}). Importers should hedge USD payables to lock in favorable rates.',
                        'timeframe': 'Immediate (1-2 weeks)'
                    })
                elif trend == 'strong_uptrend':
                    recommendations.append({
                        'priority': 'HIGH',
                        'category': 'Currency',
                        'recommendation': 'Accelerate USD conversions',
                        'rationale': f'Ringgit weakening significantly ({trend}). Exporters should convert USD earnings promptly.',
                        'timeframe': 'Immediate (1-2 weeks)'
                    })
            
            # KLCI recommendations
            elif series_id == 'MY_KLCI':
                if trend == 'strong_uptrend' and volatility == 'low':
                    recommendations.append({
                        'priority': 'MEDIUM',
                        'category': 'Investment',
                        'recommendation': 'Consider increasing equity exposure',
                        'rationale': f'KLCI in strong uptrend with low volatility. Favorable risk-reward for equity investments.',
                        'timeframe': '1-3 months'
                    })
                elif trend == 'strong_downtrend':
                    recommendations.append({
                        'priority': 'MEDIUM',
                        'category': 'Investment',
                        'recommendation': 'Review portfolio risk exposure',
                        'rationale': f'KLCI showing strong downtrend. Consider defensive positioning and stop-losses.',
                        'timeframe': 'Immediate'
                    })
        
        # Overall recommendations
        if analysis.get('overview', {}).get('sentiment') == 'negative':
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Risk Management',
                'recommendation': 'Enhance monitoring and contingency planning',
                'rationale': 'Multiple indicators showing negative trends. Prepare contingency plans for various scenarios.',
                'timeframe': 'Ongoing'
            })
        
        return recommendations
    
    def _generate_overview(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall economic overview."""
        
        # Count positive/negative indicators
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for indicator in analysis.get('indicators', {}).values():
            if 'error' in indicator:
                continue
            
            trend = indicator.get('trend', 'stable')
            if 'up' in trend:
                positive_count += 1
            elif 'down' in trend:
                negative_count += 1
            else:
                neutral_count += 1
        
        total = positive_count + negative_count + neutral_count
        
        if positive_count > negative_count * 1.5:
            sentiment = 'positive'
            confidence = 'high' if positive_count > 3 else 'moderate'
        elif negative_count > positive_count * 1.5:
            sentiment = 'negative'
            confidence = 'high' if negative_count > 3 else 'moderate'
        else:
            sentiment = 'neutral'
            confidence = 'moderate'
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_indicators': positive_count,
            'negative_indicators': negative_count,
            'neutral_indicators': neutral_count,
            'total_analyzed': total,
            'summary': f'Malaysian economic indicators show {sentiment} sentiment with {confidence} confidence. '
                      f'{positive_count} indicators positive, {negative_count} negative, {neutral_count} neutral.'
        }


def generate_deep_analysis(economic_data: List[Dict], sentiment_data: Dict = None) -> Dict[str, Any]:
    """
    Generate comprehensive deep analysis with AI agent.
    
    Args:
        economic_data: List of economic data items
        sentiment_data: Optional sentiment analysis results
    
    Returns:
        Comprehensive analysis with detailed explanations
    """
    ai_agent = MalaysiaEconomicAI()
    
    # Generate economic analysis
    economic_analysis = ai_agent.analyze_economic_trends(economic_data)
    
    # Add sentiment context if available
    if sentiment_data:
        economic_analysis['sentiment_context'] = {
            'overall_sentiment': sentiment_data.get('overall_sentiment', {}),
            'emotion_breakdown': sentiment_data.get('emotion_breakdown', {}),
            'impact': 'Public sentiment affects consumer spending and investment confidence'
        }
    
    return economic_analysis
