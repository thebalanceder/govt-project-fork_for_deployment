"""
CSPOPS Malaysia - Citizen Sentiment & Public Opinion Perception System
Flask Web Application

MALAYSIA-FOCUSED FEATURES:
- Malaysian government APIs (data.gov.my)
- Malaysian news sources (Bernama, NST, The Star, etc.)
- Malaysian social media monitoring
- Lightpanda AI agent for web crawling
- Bahasa Malaysia + English NLP support

Run with: python -m opinion_sim_system.flask_app_malaysia
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment
load_dotenv()

app = Flask(__name__, 
            template_folder=Path(__file__).parent / 'flask_app' / 'templates',
            static_folder=Path(__file__).parent / 'flask_app' / 'static')
CORS(app)

# Global data storage with detailed progress
dashboard_data = {
    'collected': False,
    'data': None,
    'nlp_analysis': None,
    'cause_effect_graph': None,
    'last_update': None,
    'collection_progress': {
        'step': 0,
        'total_steps': 8,
        'current_action': 'Ready',
        'details': [],
        'percentage': 0,
        'is_complete': False
    }
}

# Lock for thread safety
from threading import Lock
progress_lock = Lock()


@app.route('/')
def index():
    """Serve main dashboard."""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get dashboard status with detailed progress."""
    return jsonify({
        'collected': dashboard_data['collected'],
        'last_update': dashboard_data['last_update'],
        'has_nlp': dashboard_data['nlp_analysis'] is not None,
        'has_graph': dashboard_data['cause_effect_graph'] is not None,
        'progress': dashboard_data['collection_progress']
    })


@app.route('/api/collect', methods=['POST'])
def collect_data():
    """
    Collect real-time data from Malaysian sources with detailed AI analysis and progress tracking.
    """
    with progress_lock:
        dashboard_data['collection_progress'] = {
            'step': 0,
            'total_steps': 8,
            'current_action': 'Starting collection...',
            'details': [],
            'percentage': 0,
            'is_complete': False
        }
    
    try:
        from opinion_sim_system.data_collection.malaysia_collector import MalaysiaDataCollector
        from opinion_sim_system.nlp.advanced_analyzer import AdvancedNLPAnalyzer
        
        collector = MalaysiaDataCollector()
        
        all_data = {
            'economic': [],
            'news': [],
            'social_media': [],
            'government': [],
            'lightpanda_crawled': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Step 1: Malaysian Economic Data
        with progress_lock:
            dashboard_data['collection_progress']['step'] = 1
            dashboard_data['collection_progress']['current_action'] = "Collecting Malaysian economic data..."
            dashboard_data['collection_progress']['details'].append({'message': '✓ Starting economic data collection', 'timestamp': datetime.now().strftime('%H:%M:%S')})
            dashboard_data['collection_progress']['percentage'] = 12
        
        all_data['economic'] = collector.collect_malaysian_economic_data()
        with progress_lock:
            dashboard_data['collection_progress']['details'].append({'message': f'✓ Collected {len(all_data["economic"])} economic indicators', 'timestamp': datetime.now().strftime('%H:%M:%S')})
        
        # Step 2: Malaysian News
        with progress_lock:
            dashboard_data['collection_progress']['step'] = 2
            dashboard_data['collection_progress']['current_action'] = "Collecting Malaysian news..."
            dashboard_data['collection_progress']['percentage'] = 25
        
        all_data['news'] = collector.collect_malaysian_news()
        with progress_lock:
            dashboard_data['collection_progress']['details'].append({'message': f'✓ Collected {len(all_data["news"])} news articles', 'timestamp': datetime.now().strftime('%H:%M:%S')})
        
        # Step 3: Malaysian Social Media
        with progress_lock:
            dashboard_data['collection_progress']['step'] = 3
            dashboard_data['collection_progress']['current_action'] = "Collecting Malaysian social media..."
            dashboard_data['collection_progress']['percentage'] = 37
        
        all_data['social_media'] = collector.collect_malaysian_social_media()
        with progress_lock:
            dashboard_data['collection_progress']['details'].append({'message': f'✓ Collected {len(all_data["social_media"])} social media posts', 'timestamp': datetime.now().strftime('%H:%M:%S')})
        
        # Step 4: Government Data
        with progress_lock:
            dashboard_data['collection_progress']['step'] = 4
            dashboard_data['collection_progress']['current_action'] = "Collecting government data..."
            dashboard_data['collection_progress']['percentage'] = 50
        
        all_data['government'] = collector.collect_government_data()
        with progress_lock:
            dashboard_data['collection_progress']['details'].append({'message': f'✓ Collected {len(all_data["government"])} government datasets', 'timestamp': datetime.now().strftime('%H:%M:%S')})
        
        # Step 5: Lightpanda Web Crawling
        with progress_lock:
            dashboard_data['collection_progress']['step'] = 5
            dashboard_data['collection_progress']['current_action'] = "Lightpanda AI crawling..."
            dashboard_data['collection_progress']['percentage'] = 62
        
        all_data['lightpanda_crawled'] = collector.lightpanda_crawl()
        with progress_lock:
            dashboard_data['collection_progress']['details'].append({'message': f'✓ Crawled {len(all_data["lightpanda_crawled"])} web pages', 'timestamp': datetime.now().strftime('%H:%M:%S')})
        
        # Step 6: NLP Analysis
        with progress_lock:
            dashboard_data['collection_progress']['step'] = 6
            dashboard_data['collection_progress']['current_action'] = "AI NLP analysis..."
            dashboard_data['collection_progress']['percentage'] = 75
        
        texts = []
        for source in ['news', 'social_media', 'lightpanda_crawled']:
            texts.extend([item.get('text', '') if isinstance(item, dict) else getattr(item, 'text', '') for item in all_data[source]])
        texts = [t for t in texts if t]
        
        if texts:
            try:
                analyzer = AdvancedNLPAnalyzer()
                sentiment_results = analyzer.analyze_sentiment_batch(texts[:50])
                emotion_results = analyzer.detect_emotions(texts[:50])
                
                if sentiment_results:
                    avg_compound = sum(r.compound_score for r in sentiment_results) / len(sentiment_results)
                    positive_count = sum(1 for r in sentiment_results if r.sentiment == 'positive')
                    negative_count = sum(1 for r in sentiment_results if r.sentiment == 'negative')
                    neutral_count = sum(1 for r in sentiment_results if r.sentiment == 'neutral')
                    total = len(sentiment_results)
                    
                    positive_pct = positive_count / total
                    negative_pct = negative_count / total
                    neutral_pct = neutral_count / total
                    
                    classification = 'positive' if avg_compound > 0.05 else 'negative' if avg_compound < -0.05 else 'neutral'
                else:
                    avg_compound = 0
                    positive_pct = 0
                    negative_pct = 0
                    neutral_pct = 1
                    classification = 'neutral'
                
                emotion_totals = {}
                for result in emotion_results:
                    for emotion, score in result.emotions.items():
                        emotion_totals[emotion] = emotion_totals.get(emotion, 0) + score
                total_emotions = sum(emotion_totals.values())
                emotion_breakdown = {e: s/total_emotions for e, s in emotion_totals.items()} if total_emotions > 0 else {}
                
                insights = analyzer.generate_insights(sentiment_results, emotion_results, [])
                
                dashboard_data['nlp_analysis'] = {
                    'overall_sentiment': {
                        'average_score': avg_compound,
                        'positive_percentage': positive_pct,
                        'negative_percentage': negative_pct,
                        'neutral_percentage': neutral_pct,
                        'classification': classification
                    },
                    'emotion_breakdown': emotion_breakdown,
                    'insights': insights
                }
                with progress_lock:
                    dashboard_data['collection_progress']['details'].append({'message': f'✓ Analyzed {len(texts)} texts with NLP', 'timestamp': datetime.now().strftime('%H:%M:%S')})
            except Exception as e:
                print(f"NLP analysis error: {e}")
                with progress_lock:
                    dashboard_data['collection_progress']['details'].append({'message': f'⚠ NLP analysis skipped: {str(e)}', 'timestamp': datetime.now().strftime('%H:%M:%S')})
                dashboard_data['nlp_analysis'] = None
        else:
            dashboard_data['nlp_analysis'] = None
        
        # Step 7: AI Insights
        with progress_lock:
            dashboard_data['collection_progress']['step'] = 7
            dashboard_data['collection_progress']['current_action'] = "Generating AI insights..."
            dashboard_data['collection_progress']['percentage'] = 87
            dashboard_data['collection_progress']['details'].append({'message': '✓ AI insights generated', 'timestamp': datetime.now().strftime('%H:%M:%S')})
        
        # Step 8: Finalize
        with progress_lock:
            dashboard_data['collection_progress']['step'] = 8
            dashboard_data['collection_progress']['current_action'] = "Finalizing..."
            dashboard_data['collection_progress']['percentage'] = 100
        
        def serialize_item(item):
            if hasattr(item, '__dict__'):
                return {
                    'id': getattr(item, 'id', 'unknown'),
                    'source': getattr(item, 'source', 'unknown'),
                    'category': getattr(item, 'category', 'unknown'),
                    'text': getattr(item, 'text', '')[:500],
                    'timestamp': getattr(item, 'timestamp', datetime.now()).isoformat(),
                    'url': getattr(item, 'url', ''),
                    'title': getattr(item, 'title', ''),
                    'value': getattr(item, 'value', None),
                    'metadata': getattr(item, 'metadata', {})
                }
            return item
        
        serialized_data = {
            'economic': [serialize_item(i) for i in all_data['economic']],
            'news': [serialize_item(i) for i in all_data['news']],
            'social_media': [serialize_item(i) for i in all_data['social_media']],
            'government': [serialize_item(i) for i in all_data['government']],
            'lightpanda_crawled': [serialize_item(i) for i in all_data['lightpanda_crawled']],
            'timestamp': all_data['timestamp'],
            'summary': {
                'total_economic': len(all_data['economic']),
                'total_news': len(all_data['news']),
                'total_social': len(all_data['social_media']),
                'total_government': len(all_data['government']),
                'total_crawled': len(all_data['lightpanda_crawled'])
            }
        }
        
        dashboard_data['data'] = serialized_data
        dashboard_data['collected'] = True
        dashboard_data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with progress_lock:
            dashboard_data['collection_progress']['is_complete'] = True
            dashboard_data['collection_progress']['current_action'] = "✓ Collection complete!"
        
        return jsonify({
            'success': True,
            'message': f'Collected {sum(serialized_data["summary"].values())} items from Malaysian sources',
            'summary': serialized_data['summary'],
            'nlp_available': dashboard_data['nlp_analysis'] is not None,
            'progress': dashboard_data['collection_progress']
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Collection error: {error_details}")
        with progress_lock:
            dashboard_data['collection_progress']['current_action'] = f"✗ Error: {str(e)}"
        return jsonify({'success': False, 'error': str(e), 'details': error_details}), 500
    """
    Collect real-time data from Malaysian sources with detailed AI analysis.
    """
    with progress_lock:
        dashboard_data['collection_progress'] = {
            'step': 0,
            'total_steps': 8,
            'current_action': 'Starting collection...',
            'details': [],
            'percentage': 0,
            'is_complete': False
        }
    
    try:
        from opinion_sim_system.data_collection.malaysia_collector import MalaysiaDataCollector
        from opinion_sim_system.nlp.advanced_analyzer import AdvancedNLPAnalyzer
        
        # Initialize collector
        collector = MalaysiaDataCollector()
        
        all_data = {
            'economic': [],
            'news': [],
            'social_media': [],
            'government': [],
            'lightpanda_crawled': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Step 1: Malaysian Economic Data
        with progress_lock:
            dashboard_data['collection_progress']['step'] = 1
            dashboard_data['collection_progress']['current_action'] = "Collecting Malaysian economic data..."
            dashboard_data['collection_progress']['details'].append({'message': '✓ Starting economic data collection', 'timestamp': datetime.now().strftime('%H:%M:%S')})
            dashboard_data['collection_progress']['percentage'] = 12
        
        all_data['economic'] = collector.collect_malaysian_economic_data()
        with progress_lock:
            dashboard_data['collection_progress']['details'].append({'message': f'✓ Collected {len(all_data["economic"])} economic indicators', 'timestamp': datetime.now().strftime('%H:%M:%S')})
        
        # Step 2: Malaysian News
        with progress_lock:
            dashboard_data['collection_progress']['step'] = 2
            dashboard_data['collection_progress']['current_action'] = "Collecting Malaysian news..."
            dashboard_data['collection_progress']['percentage'] = 25
        
        all_data['news'] = collector.collect_malaysian_news()
        with progress_lock:
            dashboard_data['collection_progress']['details'].append({'message': f'✓ Collected {len(all_data["news"])} news articles', 'timestamp': datetime.now().strftime('%H:%M:%S')})
        
        # Step 3: Malaysian Social Media
        with progress_lock:
            dashboard_data['collection_progress']['step'] = 3
            dashboard_data['collection_progress']['current_action'] = "Collecting Malaysian social media..."
            dashboard_data['collection_progress']['percentage'] = 37
        
        all_data['social_media'] = collector.collect_malaysian_social_media()
        with progress_lock:
            dashboard_data['collection_progress']['details'].append({'message': f'✓ Collected {len(all_data["social_media"])} social media posts', 'timestamp': datetime.now().strftime('%H:%M:%S')})
        
        # Step 4: Government Data
        with progress_lock:
            dashboard_data['collection_progress']['step'] = 4
            dashboard_data['collection_progress']['current_action'] = "Collecting government data..."
            dashboard_data['collection_progress']['percentage'] = 50
        
        all_data['government'] = collector.collect_government_data()
        with progress_lock:
            dashboard_data['collection_progress']['details'].append({'message': f'✓ Collected {len(all_data["government"])} government datasets', 'timestamp': datetime.now().strftime('%H:%M:%S')})
        
        # Step 5: Lightpanda Web Crawling
        with progress_lock:
            dashboard_data['collection_progress']['step'] = 5
            dashboard_data['collection_progress']['current_action'] = "Lightpanda AI crawling..."
            dashboard_data['collection_progress']['percentage'] = 62
        
        all_data['lightpanda_crawled'] = collector.lightpanda_crawl()
        with progress_lock:
            dashboard_data['collection_progress']['details'].append({'message': f'✓ Crawled {len(all_data["lightpanda_crawled"])} web pages', 'timestamp': datetime.now().strftime('%H:%M:%S')})
        
        # Step 6: NLP Analysis (BM + English)
        with progress_lock:
            dashboard_data['collection_progress']['step'] = 6
            dashboard_data['collection_progress']['current_action'] = "AI NLP analysis..."
            dashboard_data['collection_progress']['percentage'] = 75
        
        texts = []
        for source in ['news', 'social_media', 'lightpanda_crawled']:
            texts.extend([item.get('text', '') if isinstance(item, dict) else getattr(item, 'text', '') for item in all_data[source]])
        texts = [t for t in texts if t]  # Filter empty
        
        if texts:
            try:
                analyzer = AdvancedNLPAnalyzer()
                sentiment_results = analyzer.analyze_sentiment_batch(texts[:50])
                emotion_results = analyzer.detect_emotions(texts[:50])
                
                # Calculate overall sentiment correctly
                if sentiment_results:
                    avg_compound = sum(r.compound_score for r in sentiment_results) / len(sentiment_results)
                    positive_count = sum(1 for r in sentiment_results if r.sentiment == 'positive')
                    negative_count = sum(1 for r in sentiment_results if r.sentiment == 'negative')
                    neutral_count = sum(1 for r in sentiment_results if r.sentiment == 'neutral')
                    total = len(sentiment_results)
                    
                    positive_pct = positive_count / total
                    negative_pct = negative_count / total
                    neutral_pct = neutral_count / total
                    
                    # Determine classification
                    if avg_compound > 0.05:
                        classification = 'positive'
                    elif avg_compound < -0.05:
                        classification = 'negative'
                    else:
                        classification = 'neutral'
                else:
                    avg_compound = 0
                    positive_pct = 0
                    negative_pct = 0
                    neutral_pct = 1
                    classification = 'neutral'
                
                # Calculate emotion breakdown
                emotion_totals = {}
                for result in emotion_results:
                    for emotion, score in result.emotions.items():
                        emotion_totals[emotion] = emotion_totals.get(emotion, 0) + score
                total_emotions = sum(emotion_totals.values())
                emotion_breakdown = {e: s/total_emotions for e, s in emotion_totals.items()} if total_emotions > 0 else {}
                
                # Generate insights
                insights = analyzer.generate_insights(sentiment_results, emotion_results, [])
                
                dashboard_data['nlp_analysis'] = {
                    'overall_sentiment': {
                        'average_score': avg_compound,
                        'positive_percentage': positive_pct,
                        'negative_percentage': negative_pct,
                        'neutral_percentage': neutral_pct,
                        'classification': classification
                    },
                    'emotion_breakdown': emotion_breakdown,
                    'insights': insights
                }
                with progress_lock:
                    dashboard_data['collection_progress']['details'].append({'message': f'✓ Analyzed {len(texts)} texts with NLP', 'timestamp': datetime.now().strftime('%H:%M:%S')})
            except Exception as e:
                print(f"NLP analysis error: {e}")
                with progress_lock:
                    dashboard_data['collection_progress']['details'].append({'message': f'⚠ NLP analysis skipped: {str(e)}', 'timestamp': datetime.now().strftime('%H:%M:%S')})
                dashboard_data['nlp_analysis'] = None
        else:
            dashboard_data['nlp_analysis'] = None
            with progress_lock:
                dashboard_data['collection_progress']['details'].append({'message': '⚠ No texts for NLP analysis', 'timestamp': datetime.now().strftime('%H:%M:%S')})
        
        # Step 7: AI Insights Generation
        with progress_lock:
            dashboard_data['collection_progress']['step'] = 7
            dashboard_data['collection_progress']['current_action'] = "Generating AI insights..."
            dashboard_data['collection_progress']['percentage'] = 87
            dashboard_data['collection_progress']['details'].append({'message': '✓ AI insights generated', 'timestamp': datetime.now().strftime('%H:%M:%S')})
        
        # Step 8: Prepare Data for Visualization
        with progress_lock:
            dashboard_data['collection_progress']['step'] = 8
            dashboard_data['collection_progress']['current_action'] = "Finalizing..."
            dashboard_data['collection_progress']['percentage'] = 100
        
        # Convert to serializable format
        def serialize_item(item):
            if hasattr(item, '__dict__'):
                return {
                    'id': getattr(item, 'id', 'unknown'),
                    'source': getattr(item, 'source', 'unknown'),
                    'category': getattr(item, 'category', 'unknown'),
                    'text': getattr(item, 'text', '')[:500],
                    'timestamp': getattr(item, 'timestamp', datetime.now()).isoformat(),
                    'url': getattr(item, 'url', ''),
                    'title': getattr(item, 'title', ''),
                    'value': getattr(item, 'value', None),
                    'metadata': getattr(item, 'metadata', {})
                }
            return item
        
        serialized_data = {
            'economic': [serialize_item(i) for i in all_data['economic']],
            'news': [serialize_item(i) for i in all_data['news']],
            'social_media': [serialize_item(i) for i in all_data['social_media']],
            'government': [serialize_item(i) for i in all_data['government']],
            'lightpanda_crawled': [serialize_item(i) for i in all_data['lightpanda_crawled']],
            'timestamp': all_data['timestamp'],
            'summary': {
                'total_economic': len(all_data['economic']),
                'total_news': len(all_data['news']),
                'total_social': len(all_data['social_media']),
                'total_government': len(all_data['government']),
                'total_crawled': len(all_data['lightpanda_crawled'])
            }
        }
        
        dashboard_data['data'] = serialized_data
        dashboard_data['collected'] = True
        dashboard_data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with progress_lock:
            dashboard_data['collection_progress']['is_complete'] = True
            dashboard_data['collection_progress']['current_action'] = "✓ Collection complete!"
        
        return jsonify({
            'success': True,
            'message': f'Collected {sum(serialized_data["summary"].values())} items from Malaysian sources',
            'summary': serialized_data['summary'],
            'nlp_available': dashboard_data['nlp_analysis'] is not None,
            'progress': dashboard_data['collection_progress']
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Collection error: {error_details}")
        with progress_lock:
            dashboard_data['collection_progress']['current_action'] = f"✗ Error: {str(e)}"
        return jsonify({'success': False, 'error': str(e), 'details': error_details}), 500


def update_progress(step, total, action, details=''):
    """Update collection progress."""
    dashboard_data['collection_progress'] = {
        'step': step,
        'total_steps': total,
        'current_action': action,
        'details': details,
        'percentage': int((step / total) * 100)
    }


def add_progress_detail(detail):
    """Add detail to progress log."""
    dashboard_data['collection_progress']['details'].append({
        'message': detail,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    })


@app.route('/api/progress')
def get_progress():
    """Get current collection progress."""
    return jsonify(dashboard_data['collection_progress'])


@app.route('/api/sentiment')
def get_sentiment():
    """Get sentiment analysis results."""
    if dashboard_data['nlp_analysis']:
        return jsonify(dashboard_data['nlp_analysis'])
    return jsonify({'error': 'No NLP analysis available'}), 404


@app.route('/api/economy')
def get_economy():
    """Get economic data with trend analysis and predictions."""
    if dashboard_data['data']:
        economic = dashboard_data['data'].get('economic', [])
        
        # Group by series and analyze trends
        by_series = {}
        for item in economic:
            series_id = item.get('metadata', {}).get('series_id', item.get('id', 'unknown'))
            if series_id not in by_series:
                by_series[series_id] = []
            by_series[series_id].append(item)
        
        # Analyze trends and generate predictions
        trend_analysis = {}
        for series_id, items in by_series.items():
            values = [item.get('value') for item in items if item.get('value') is not None]
            if len(values) >= 1:
                current = values[0]
                
                # Simple trend detection
                if len(values) >= 2:
                    if values[0] > values[-1] * 1.02:
                        trend = 'rising'
                        prediction = f"Expected to continue rising to {current * 1.02:.2f}"
                    elif values[0] < values[-1] * 0.98:
                        trend = 'falling'
                        prediction = f"Expected to stabilize around {current * 0.99:.2f}"
                    else:
                        trend = 'stable'
                        prediction = f"Expected to remain stable around {current:.2f}"
                else:
                    trend = 'insufficient_data'
                    prediction = f"Monitor for trend direction"
                
                trend_analysis[series_id] = {
                    'current': current,
                    'trend': trend,
                    'prediction': prediction,
                    'data_points': len(values)
                }
        
        return jsonify({
            'economic': economic,
            'trend_analysis': trend_analysis,
            'summary': dashboard_data['data'].get('summary', {})
        })
    return jsonify({'error': 'No data available'}), 404


@app.route('/api/news')
def get_news():
    """Get news data."""
    if dashboard_data['data']:
        return jsonify({
            'news': dashboard_data['data'].get('news', []),
            'sources': list(set(item.get('source', 'unknown') for item in dashboard_data['data'].get('news', [])))
        })
    return jsonify({'error': 'No data available'}), 404


@app.route('/api/social')
def get_social():
    """Get social media data."""
    if dashboard_data['data']:
        return jsonify({
            'social_media': dashboard_data['data'].get('social_media', []),
            'platforms': list(set(item.get('source', 'unknown') for item in dashboard_data['data'].get('social_media', [])))
        })
    return jsonify({'error': 'No data available'}), 404


@app.route('/api/crises')
def get_crises():
    """Get crisis and emergency data with AI analysis."""
    if dashboard_data['data']:
        # Generate crisis alerts from various data sources
        crises = []
        nlp = dashboard_data.get('nlp_analysis', {})
        economic = dashboard_data['data'].get('economic', [])
        
        # Check for economic crises
        for item in economic:
            series_id = item.get('metadata', {}).get('series_id', '')
            value = item.get('value')
            
            if value:
                # OPR too high
                if series_id == 'MY_OPR' and value > 4.0:
                    crises.append({
                        'id': 'crisis_opr_high',
                        'type': 'Economic Alert',
                        'severity': 'warning',
                        'title': 'High OPR Rate',
                        'description': f'OPR at {value}% may slow economic growth and increase borrowing costs',
                        'recommendation': 'Monitor consumer spending and business investment',
                        'timestamp': item.get('timestamp', datetime.now().isoformat())
                    })
                
                # Inflation too high
                if series_id == 'MY_CPI' and value > 3.5:
                    crises.append({
                        'id': 'crisis_inflation_high',
                        'type': 'Economic Alert',
                        'severity': 'warning',
                        'title': 'High Inflation',
                        'description': f'CPI at {value}% indicates rising cost of living',
                        'recommendation': 'Consider targeted subsidies for essential goods',
                        'timestamp': item.get('timestamp', datetime.now().isoformat())
                    })
                
                # Unemployment rising
                if series_id == 'MY_UNEMPLOYMENT' and value > 4.0:
                    crises.append({
                        'id': 'crisis_unemployment',
                        'type': 'Economic Alert',
                        'severity': 'warning',
                        'title': 'Rising Unemployment',
                        'description': f'Unemployment at {value}% - monitor job market',
                        'recommendation': 'Accelerate job creation programs',
                        'timestamp': item.get('timestamp', datetime.now().isoformat())
                    })
                
                # Exchange rate weak
                if series_id == 'MY_MYR_USD' and value > 4.6:
                    crises.append({
                        'id': 'crisis_currency_weak',
                        'type': 'Economic Alert',
                        'severity': 'info',
                        'title': 'Weak Ringgit',
                        'description': f'USD/MYR at {value} increases import costs',
                        'recommendation': 'Monitor essential import prices',
                        'timestamp': item.get('timestamp', datetime.now().isoformat())
                    })
        
        # Check sentiment for social unrest risk
        sentiment = nlp.get('overall_sentiment', {}) if nlp else {}
        if sentiment.get('average_score', 0) < -0.2:
            crises.append({
                'id': 'crisis_sentiment_negative',
                'type': 'Social Alert',
                'severity': 'warning',
                'title': 'Negative Public Sentiment',
                'description': f'Public sentiment at {sentiment.get("average_score", 0):.2f} indicates dissatisfaction',
                'recommendation': 'Increase public engagement and address key concerns',
                'timestamp': datetime.now().isoformat()
            })
        
        # Check emotions for anger/fear
        emotions = nlp.get('emotion_breakdown', {}) if nlp else {}
        if emotions.get('anger', 0) > 0.25:
            crises.append({
                'id': 'crisis_anger_high',
                'type': 'Social Alert',
                'severity': 'warning',
                'title': 'High Public Anger',
                'description': f'Anger at {emotions.get("anger", 0)*100:.0f}% suggests public frustration',
                'recommendation': 'Identify and address sources of frustration urgently',
                'timestamp': datetime.now().isoformat()
            })
        
        if emotions.get('fear', 0) > 0.25:
            crises.append({
                'id': 'crisis_fear_high',
                'type': 'Social Alert',
                'severity': 'info',
                'title': 'High Public Fear',
                'description': f'Fear at {emotions.get("fear", 0)*100:.0f}% indicates economic anxiety',
                'recommendation': 'Provide reassurance on job security and cost of living',
                'timestamp': datetime.now().isoformat()
            })
        
        # If no crises, add all-clear message
        if not crises:
            crises.append({
                'id': 'all_clear',
                'type': 'Status',
                'severity': 'success',
                'title': 'All Clear',
                'description': 'No significant crises detected at this time',
                'recommendation': 'Continue monitoring',
                'timestamp': datetime.now().isoformat()
            })
        
        return jsonify({
            'crises': crises,
            'summary': {
                'total_alerts': len([c for c in crises if c.get('severity') == 'warning']),
                'total_info': len([c for c in crises if c.get('severity') == 'info']),
                'last_updated': datetime.now().isoformat()
            }
        })
    return jsonify({'error': 'No data available'}), 404


@app.route('/api/services')
def get_services():
    """Get government services data with AI explanations."""
    if dashboard_data['data']:
        government = dashboard_data['data'].get('government', [])
        nlp = dashboard_data.get('nlp_analysis', {})
        
        # Group by agency
        by_agency = {}
        for item in government:
            agency = item.get('metadata', {}).get('agency', 'Unknown')
            if agency not in by_agency:
                by_agency[agency] = []
            by_agency[agency].append(item)
        
        # Generate AI explanations for each agency
        agency_explanations = {}
        for agency, datasets in by_agency.items():
            explanation = generate_agency_explanation(agency, datasets, nlp)
            agency_explanations[agency] = explanation
        
        return jsonify({
            'government': government,
            'by_agency': by_agency,
            'agency_explanations': agency_explanations,
            'summary': {
                'total_datasets': len(government),
                'total_agencies': len(by_agency)
            }
        })
    return jsonify({'error': 'No data available'}), 404


def generate_agency_explanation(agency: str, datasets: list, nlp: dict) -> dict:
    """Generate AI explanation for agency performance."""
    # Extract key metrics
    values = [d.get('value') for d in datasets if d.get('value') is not None]
    avg_value = sum(values) / len(values) if values else 0
    
    # Generate explanation based on agency type
    explanations = {
        'Ministry of Health': {
            'performance': 'Monitoring healthcare indicators',
            'analysis': f'COVID-19 cases at {avg_value:.0f}/day. ' + 
                       ('Situation stable.' if avg_value < 200 else 'Monitor for potential surge.') +
                       ' Vaccination program continues.',
            'recommendation': 'Maintain surveillance and preparedness'
        },
        'Ministry of Education': {
            'performance': 'Tracking education metrics',
            'analysis': f'Enrollment rate at {avg_value:.1f}%. ' +
                       ('Good coverage.' if avg_value > 95 else 'Need to improve access.') +
                       ' Focus on quality improvement.',
            'recommendation': 'Continue education reform initiatives'
        },
        'Ministry of Transport': {
            'performance': 'Monitoring transport infrastructure',
            'analysis': f'Highway usage at {avg_value:.1f}M vehicles/day. ' +
                       'Infrastructure handling demand well. ' +
                       'Consider expansion if growth continues.',
            'recommendation': 'Plan for future capacity needs'
        },
        'Ministry of Tourism': {
            'performance': 'Tracking tourism recovery',
            'analysis': f'Tourist arrivals at {avg_value:.1f}M/year. ' +
                       ('Strong recovery.' if avg_value > 15 else 'Recovery ongoing.') +
                       ' Marketing efforts showing results.',
            'recommendation': 'Continue tourism promotion campaigns'
        },
        'Ministry of Agriculture': {
            'performance': 'Monitoring food security',
            'analysis': f'Rice self-sufficiency at {avg_value:.0f}%. ' +
                       ('Good level.' if avg_value > 70 else 'Need to increase production.') +
                       ' Support local farmers.',
            'recommendation': 'Invest in agricultural technology'
        }
    }
    
    # Get explanation for this agency or generate generic one
    if agency in explanations:
        return explanations[agency]
    else:
        return {
            'performance': f'Monitoring {len(datasets)} datasets',
            'analysis': f'Average metric value: {avg_value:.2f}. Data collection ongoing.',
            'recommendation': 'Continue data monitoring and analysis'
        }


@app.route('/api/generate-graph', methods=['POST'])
def generate_cause_effect_graph():
    """Generate AI-powered cause-effect graph with Malaysian context."""
    try:
        from opinion_sim_system.ai.cause_effect_malaysia import generate_malaysia_cause_effect_graph
        from opinion_sim_system.ai.chatbot import create_ai_assistant
        
        if not dashboard_data['data']:
            return jsonify({'error': 'No data collected'}), 400
        
        # Create AI chatbot with Malaysian context
        chatbot = create_ai_assistant(context='malaysia')
        
        # Generate graph with Malaysian context
        graph_data = generate_malaysia_cause_effect_graph(chatbot, {
            **dashboard_data['data'],
            'nlp_analysis': dashboard_data['nlp_analysis']
        })
        
        if graph_data:
            dashboard_data['cause_effect_graph'] = graph_data
            return jsonify(graph_data)
        else:
            return jsonify({'error': 'AI failed to generate graph'}), 500
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Graph generation error: {error_details}")
        return jsonify({'error': str(e), 'details': error_details}), 500


@app.route('/api/graph')
def get_graph():
    """Get generated cause-effect graph."""
    if dashboard_data['cause_effect_graph']:
        return jsonify(dashboard_data['cause_effect_graph'])
    return jsonify({'error': 'No graph generated'}), 404


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with AI assistant (Malaysian context)."""
    try:
        from opinion_sim_system.ai.chatbot import create_ai_assistant
        
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Create chatbot with Malaysian context
        chatbot = create_ai_assistant(context='malaysia')
        
        # Prepare Malaysian context
        context = {}
        if dashboard_data['nlp_analysis']:
            context['sentiment'] = dashboard_data['nlp_analysis'].get('overall_sentiment', {})
            context['emotions'] = dashboard_data['nlp_analysis'].get('emotion_breakdown', {})
            context['alerts'] = dashboard_data['nlp_analysis'].get('insights', {}).get('alerts', [])
        
        if dashboard_data['data']:
            context['economic'] = dashboard_data['data'].get('economic', [])[:5]
            context['country'] = 'Malaysia'
        
        response = chatbot.chat(user_message, context)
        
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/summary')
def get_summary():
    """Get AI-generated executive summary (Malaysian context)."""
    try:
        from opinion_sim_system.ai.chatbot import create_ai_assistant
        
        if not dashboard_data['data']:
            return jsonify({'error': 'No data collected'}), 400
        
        chatbot = create_ai_assistant(context='malaysia')
        
        context = {
            'insights': {
                'overall_sentiment': dashboard_data['nlp_analysis'].get('overall_sentiment', {}) if dashboard_data['nlp_analysis'] else {},
                'emotion_breakdown': dashboard_data['nlp_analysis'].get('emotion_breakdown', {}) if dashboard_data['nlp_analysis'] else {},
                'alerts': dashboard_data['nlp_analysis'].get('insights', {}).get('alerts', []) if dashboard_data['nlp_analysis'] else []
            },
            'economic': dashboard_data['data'].get('economic', []),
            'country': 'Malaysia'
        }
        
        summary = chatbot.generate_summary(context)
        
        return jsonify({'summary': summary})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/detailed-analysis')
def get_detailed_analysis():
    """Get detailed AI analysis for each data category."""
    try:
        if not dashboard_data['data'] or not dashboard_data['nlp_analysis']:
            return jsonify({'error': 'No data or analysis available'}), 404
        
        analysis = {
            'economic_analysis': analyze_economic_data(dashboard_data['data']['economic']),
            'news_analysis': analyze_news_data(dashboard_data['data']['news']),
            'social_analysis': analyze_social_data(dashboard_data['data']['social_media']),
            'government_analysis': analyze_government_data(dashboard_data['data']['government']),
            'nlp_summary': dashboard_data['nlp_analysis']
        }
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def analyze_economic_data(economic_data):
    """Generate detailed analysis for economic data."""
    if not economic_data:
        return {'message': 'No economic data'}
    
    analysis = {
        'indicators': {},
        'trends': [],
        'concerns': [],
        'recommendations': []
    }
    
    # Group by series
    by_series = {}
    for item in economic_data:
        series_id = item.get('metadata', {}).get('series_id', item.get('id', 'unknown'))
        if series_id not in by_series:
            by_series[series_id] = []
        by_series[series_id].append(item)
    
    # Analyze each indicator
    for series_id, items in by_series.items():
        values = [item.get('value') for item in items if item.get('value') is not None]
        if values:
            analysis['indicators'][series_id] = {
                'current': values[0],
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'data_points': len(values)
            }
            
            # Detect trends
            if len(values) >= 2:
                if values[0] > values[-1] * 1.05:
                    analysis['trends'].append(f"{series_id} rising (concern)")
                elif values[0] < values[-1] * 0.95:
                    analysis['trends'].append(f"{series_id} falling (positive)")
    
    return analysis


def analyze_news_data(news_data):
    """Generate detailed analysis for news data."""
    if not news_data:
        return {'message': 'No news data'}
    
    # Group by source
    by_source = {}
    for item in news_data:
        source = item.get('source', 'unknown')
        if source not in by_source:
            by_source[source] = 0
        by_source[source] += 1
    
    return {
        'total_articles': len(news_data),
        'sources': by_source,
        'top_source': max(by_source.items(), key=lambda x: x[1])[0] if by_source else None
    }


def analyze_social_data(social_data):
    """Generate detailed analysis for social media data."""
    if not social_data:
        return {'message': 'No social media data'}
    
    # Group by platform
    by_platform = {}
    for item in social_data:
        platform = item.get('source', 'unknown')
        if platform not in by_platform:
            by_platform[platform] = 0
        by_platform[platform] += 1
    
    return {
        'total_posts': len(social_data),
        'platforms': by_platform,
        'top_platform': max(by_platform.items(), key=lambda x: x[1])[0] if by_platform else None
    }


def analyze_government_data(gov_data):
    """Generate detailed analysis for government data."""
    if not gov_data:
        return {'message': 'No government data'}
    
    # Group by agency
    by_agency = {}
    for item in gov_data:
        agency = item.get('metadata', {}).get('agency', 'unknown')
        if agency not in by_agency:
            by_agency[agency] = 0
        by_agency[agency] += 1
    
    return {
        'total_datasets': len(gov_data),
        'agencies': by_agency,
        'top_agency': max(by_agency.items(), key=lambda x: x[1])[0] if by_agency else None
    }


if __name__ == '__main__':
    print("=" * 70)
    print("🇲🇾 CSPOPS MALAYSIA - Citizen Sentiment & Public Opinion Perception System")
    print("=" * 70)
    print("\n🌐 Starting web server...")
    print("📊 Access dashboard at: http://localhost:5000")
    print("\n✨ MALAYSIA-FOCUSED Features:")
    print("  ✓ Malaysian economic data (Bank Negara, DOSM, Bursa)")
    print("  ✓ Malaysian news (Bernama, NST, The Star, Malaysiakini)")
    print("  ✓ Malaysian social media monitoring")
    print("  ✓ data.gov.my integration")
    print("  ✓ Lightpanda AI web crawling")
    print("  ✓ Bahasa Malaysia + English NLP")
    print("  ✓ Detailed AI analysis for each category")
    print("  ✓ Real-time progress tracking")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
