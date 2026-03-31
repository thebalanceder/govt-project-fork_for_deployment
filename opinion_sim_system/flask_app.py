"""
CSPOPS - Citizen Sentiment & Public Opinion Perception System
Flask Web Application

A beautiful, professional web dashboard with:
- Interactive D3.js cause-effect graphs
- Real-time data visualization
- AI-powered insights
- Professional government-grade UI

Run with: python -m opinion_sim_system.flask_app
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

# Global data storage
dashboard_data = {
    'collected': False,
    'data': None,
    'nlp_analysis': None,
    'cause_effect_graph': None,
    'last_update': None
}


@app.route('/')
def index():
    """Serve main dashboard."""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get dashboard status."""
    return jsonify({
        'collected': dashboard_data['collected'],
        'last_update': dashboard_data['last_update'],
        'has_nlp': dashboard_data['nlp_analysis'] is not None,
        'has_graph': dashboard_data['cause_effect_graph'] is not None
    })


@app.route('/api/collect', methods=['POST'])
def collect_data():
    """Collect real-time data from ALL sources (unified collection)."""
    try:
        from opinion_sim_system.data_collection.unified_collector import UnifiedDataCollector
        from opinion_sim_system.nlp.advanced_analyzer import AdvancedNLPAnalyzer
        from opinion_sim_system.integration.data_adapter import MiroFishDataAdapter
        from opinion_sim_system.mirofish.discussion import run_all_topics_discussion

        print("\n" + "=" * 70)
        print("🇲🇾 CSPOPS - Complete Data Collection & AI Analysis")
        print("=" * 70)

        # Run unified collection
        collector = UnifiedDataCollector(max_items_per_category=100)
        collection_result = collector.collect_all()

        # Extract data by category
        all_data = {
            'economic': collection_result.get('economic', []),
            'political': collection_result.get('political', []),
            'cultural': collection_result.get('cultural', []),
            'stats': collection_result.get('stats', {}),
            'timestamp': collection_result.get('timestamp', datetime.now().isoformat())
        }

        # Auto-run NLP analysis on all text data
        all_texts = []
        for category in ['economic', 'political', 'cultural']:
            for item in all_data[category][:30]:  # Limit for NLP
                if hasattr(item, 'text') and item.text:
                    all_texts.append(item.text)

        if all_texts:
            print(f"\n🤖 Running NLP Analysis on {len(all_texts)} texts...")
            analyzer = AdvancedNLPAnalyzer()
            sentiment_results = analyzer.analyze_sentiment_batch(all_texts[:50])
            emotion_results = analyzer.detect_emotions(all_texts[:50])
            insights = analyzer.generate_insights(sentiment_results, emotion_results, [])

            # Calculate overall sentiment
            avg_compound = sum(r.compound_score for r in sentiment_results) / len(sentiment_results) if sentiment_results else 0
            positive_pct = sum(1 for r in sentiment_results if r.sentiment == 'positive') / len(sentiment_results) if sentiment_results else 0
            negative_pct = sum(1 for r in sentiment_results if r.sentiment == 'negative') / len(sentiment_results) if sentiment_results else 0

            # Calculate emotion breakdown
            emotion_totals = {}
            for result in emotion_results:
                for emotion, score in result.emotions.items():
                    emotion_totals[emotion] = emotion_totals.get(emotion, 0) + score
            total = sum(emotion_totals.values())
            emotion_breakdown = {e: s/total for e, s in emotion_totals.items()} if total > 0 else {}

            dashboard_data['nlp_analysis'] = {
                'overall_sentiment': {
                    'average_score': avg_compound,
                    'positive_percentage': positive_pct,
                    'negative_percentage': negative_pct,
                    'classification': 'positive' if avg_compound > 0.1 else 'negative' if avg_compound < -0.1 else 'neutral'
                },
                'emotion_breakdown': emotion_breakdown,
                'insights': insights,
                'sentiment_results': [
                    {'sentiment': r.sentiment, 'confidence': r.confidence, 'compound': r.compound_score}
                    for r in sentiment_results
                ]
            }
            print(f"✓ NLP Analysis Complete")

        # NEW: Run MiroFish Multi-Agent Discussions
        print("\n" + "=" * 70)
        print("🤖 Starting Multi-Agent AI Discussions...")
        print("=" * 70)
        
        try:
            # Convert data to agent format
            adapter = MiroFishDataAdapter()
            agent_data = adapter.convert_to_agent_format(all_data)
            
            # Run discussions for all topics
            discussion_results = run_all_topics_discussion(agent_data)
            
            # Format and store results
            dashboard_data['agent_discussions'] = adapter.format_discussion_results(discussion_results)
            
            print(f"\n✓ Multi-Agent Discussions Complete")
            for topic, result in discussion_results.items():
                consensus_label = "positive" if result.final_consensus > 0.1 else "negative" if result.final_consensus < -0.1 else "neutral"
                print(f"  {topic.capitalize()}: {result.final_consensus:.2f} ({consensus_label}), Convergence: {result.convergence_rate:.0%}")
            
        except Exception as e:
            import traceback
            print(f"⚠ Agent discussion error: {e}")
            print(traceback.format_exc())
            dashboard_data['agent_discussions'] = None

        # Convert DataItem objects to dicts for JSON serialization
        def serialize_item(item):
            if hasattr(item, '__dict__'):
                return {
                    'id': item.id,
                    'source': item.source,
                    'category': item.category,
                    'text': item.text[:2000] if hasattr(item, 'text') else '',
                    'timestamp': item.timestamp.isoformat() if hasattr(item, 'timestamp') else datetime.now().isoformat(),
                    'url': item.url if hasattr(item, 'url') else '',
                    'title': item.title if hasattr(item, 'title') else '',
                    'value': item.value if hasattr(item, 'value') else None,
                    'metadata': item.metadata if hasattr(item, 'metadata') else {}
                }
            return item

        serialized_data = {
            'economic': [serialize_item(i) for i in all_data['economic']],
            'political': [serialize_item(i) for i in all_data['political']],
            'cultural': [serialize_item(i) for i in all_data['cultural']],
            'timestamp': all_data['timestamp']
        }

        dashboard_data['data'] = serialized_data
        dashboard_data['collected'] = True
        dashboard_data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Build summary object for frontend
        stats = all_data.get('stats', {})
        summary = {
            'total_economic': stats.get('economic', len(all_data['economic'])),
            'total_political': stats.get('political', len(all_data['political'])),
            'total_cultural': stats.get('cultural', len(all_data['cultural'])),
            'total_all': sum(stats.get(cat, len(all_data[cat])) for cat in ['economic', 'political', 'cultural']),
            'sources_used': stats.get('sources_used', [])
        }

        return jsonify({
            'success': True,
            'message': f'Collected {summary["total_all"]} items from {len(summary["sources_used"])} sources',
            'nlp_available': dashboard_data['nlp_analysis'] is not None,
            'agent_discussions_available': dashboard_data['agent_discussions'] is not None,
            'summary': summary
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/sentiment')
def get_sentiment():
    """Get sentiment analysis results."""
    if dashboard_data['nlp_analysis']:
        return jsonify(dashboard_data['nlp_analysis'])
    return jsonify({'error': 'No NLP analysis available'}), 404


@app.route('/api/data')
def get_all_data():
    """Get all collected data (economic, political, cultural)."""
    if dashboard_data['data']:
        return jsonify(dashboard_data['data'])
    return jsonify({'error': 'No data collected'}), 404


@app.route('/api/agents')
def get_agent_results():
    """Get multi-agent discussion results."""
    if dashboard_data.get('agent_discussions'):
        return jsonify(dashboard_data['agent_discussions'])
    return jsonify({'error': 'No agent discussions available'}), 404


@app.route('/api/generate-graph', methods=['POST'])
def generate_cause_effect_graph():
    """Generate AI-powered cause-effect graph."""
    try:
        from opinion_sim_system.ai.cause_effect import generate_cause_effect_graph
        from opinion_sim_system.ai.chatbot import create_ai_assistant
        
        if not dashboard_data['data']:
            return jsonify({'error': 'No data collected'}), 400
        
        # Create AI chatbot
        chatbot = create_ai_assistant()
        
        # Generate graph
        graph_data = generate_cause_effect_graph(chatbot, {
            **dashboard_data['data'],
            'nlp_analysis': dashboard_data['nlp_analysis']
        })
        
        if graph_data:
            dashboard_data['cause_effect_graph'] = graph_data
            return jsonify(graph_data)
        else:
            return jsonify({'error': 'AI failed to generate graph'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/graph')
def get_graph():
    """Get generated cause-effect graph."""
    if dashboard_data['cause_effect_graph']:
        return jsonify(dashboard_data['cause_effect_graph'])
    return jsonify({'error': 'No graph generated'}), 404


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with AI assistant."""
    try:
        from opinion_sim_system.ai.chatbot import create_ai_assistant
        
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        chatbot = create_ai_assistant()
        
        # Prepare context
        context = {}
        if dashboard_data['nlp_analysis']:
            context['sentiment'] = dashboard_data['nlp_analysis'].get('overall_sentiment', {})
            context['emotions'] = dashboard_data['nlp_analysis'].get('emotion_breakdown', {})
            context['alerts'] = dashboard_data['nlp_analysis'].get('insights', {}).get('alerts', [])
        
        if dashboard_data['data']:
            context['economic'] = dashboard_data['data'].get('economic', [])[:5]
        
        response = chatbot.chat(user_message, context)
        
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/summary')
def get_summary():
    """Get AI-generated executive summary."""
    try:
        from opinion_sim_system.ai.chatbot import create_ai_assistant
        
        if not dashboard_data['data']:
            return jsonify({'error': 'No data collected'}), 400
        
        chatbot = create_ai_assistant()
        
        context = {
            'insights': {
                'overall_sentiment': dashboard_data['nlp_analysis'].get('overall_sentiment', {}) if dashboard_data['nlp_analysis'] else {},
                'emotion_breakdown': dashboard_data['nlp_analysis'].get('emotion_breakdown', {}) if dashboard_data['nlp_analysis'] else {},
                'alerts': dashboard_data['nlp_analysis'].get('insights', {}).get('alerts', []) if dashboard_data['nlp_analysis'] else []
            },
            'economic': dashboard_data['data'].get('economic', [])
        }
        
        summary = chatbot.generate_summary(context)
        
        return jsonify({'summary': summary})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🏛️  CSPOPS - Citizen Sentiment & Public Opinion Perception System")
    print("=" * 60)
    print("\n🌐 Starting web server...")
    print("📊 Access dashboard at: http://localhost:5000")
    print("\n✨ Features:")
    print("  - Real-time data collection from 10+ APIs")
    print("  - Auto NLP sentiment analysis")
    print("  - AI-powered cause-effect graph generation")
    print("  - Interactive D3.js visualizations")
    print("  - AI chatbot for Q&A")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
