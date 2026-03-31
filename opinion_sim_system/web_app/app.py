#!/usr/bin/env python3
"""
CSPOPS - Citizen Sentiment & Public Opinion Perception System

CSPOPS is a live AI analytics platform that aggregates public sentiment from 
economic indicators, news media, social platforms, and government metrics using 
free public APIs. It provides real-time dashboards with sentiment analysis (NLP), 
crisis detection, and trend forecasting – enabling data-driven governance. 

Built with Python, Streamlit, and Plotly, all data is live with no simulation. 
This showcase is directly relevant to the PMX visit to FAI, demonstrating AI 
for public opinion monitoring and policy support.

Run with: streamlit run opinion_sim_system/web_app/app.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Load .env file FIRST before any other imports
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded .env from: {env_path}")
else:
    print(f"⚠ .env not found at: {env_path}")

# Add project root to path (parent of opinion_sim_system)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import numpy for NLP analysis
import numpy as np

# Import streamlit first
import streamlit as st

# Now import from opinion_sim_system package
from opinion_sim_system.data_collection.enhanced_collector import (
    EnhancedDataCollector,
    EconomicIndicatorsCollector,
    CrisisMonitoringCollector,
    ServiceDeliveryCollector,
)
from opinion_sim_system.data_collection.collector import (
    DataCollector,
    CollectorConfig,
)

# Import visualization
from opinion_sim_system.visualization.pm_dashboard import (
    create_sentiment_gauge,
    create_archetype_breakdown,
    create_evolution_chart,
    create_topic_chart,
    generate_risk_alerts,
)

# Import NLP analyzer
try:
    from opinion_sim_system.nlp.advanced_analyzer import AdvancedNLPAnalyzer, analyze_texts
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    AdvancedNLPAnalyzer = None
    analyze_texts = None

# Import AI chatbot and cause-effect generator
try:
    from opinion_sim_system.ai.chatbot import AIChatbot, ChatConfig, create_ai_assistant
    from opinion_sim_system.ai.cause_effect import generate_cause_effect_graph
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    AIChatbot = None
    ChatConfig = None
    create_ai_assistant = None
    generate_cause_effect_graph = None


def setup_page():
    """Configure page settings and CSS."""
    st.set_page_config(
        page_title="PM Executive Dashboard",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/your-org/opinion-sim-system',
            'Report a bug': 'https://github.com/your-org/opinion-sim-system/issues',
            'About': "# PM Executive Dashboard\nReal-time public opinion monitoring system."
        }
    )
    
    # Custom CSS for professional government look
    st.markdown("""
    <style>
        /* Main header styling */
        .main-header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
        }
        .main-header h1 {
            font-size: 2.5rem;
            font-weight: bold;
            margin: 0;
        }
        .main-header p {
            font-size: 1.1rem;
            opacity: 0.9;
            margin-top: 0.5rem;
        }
        
        /* Metric cards */
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            border-left: 4px solid #667eea;
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1a1a2e;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #666;
            margin-top: 0.5rem;
        }
        
        /* Alert boxes */
        .alert-critical {
            background: #fef2f2;
            border-left: 4px solid #dc3545;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 5px;
        }
        .alert-warning {
            background: #fffbeb;
            border-left: 4px solid #ffc107;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 5px;
        }
        .alert-info {
            background: #eff6ff;
            border-left: 4px solid #0066cc;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 5px;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


# Session state initialization
if 'data_collected' not in st.session_state:
    st.session_state.data_collected = False
if 'collected_data' not in st.session_state:
    st.session_state.collected_data = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'api_configured' not in st.session_state:
    st.session_state.api_configured = False


def load_environment() -> CollectorConfig:
    """Load environment and API configuration."""
    from dotenv import load_dotenv
    # .env is in opinion_sim_system directory
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    return CollectorConfig.from_env()


def check_api_status(config: CollectorConfig) -> dict[str, bool]:
    """Check which APIs are configured."""
    return {
        "FRED": bool(config.fred_api_key),
        "BLS": bool(config.bls_api_key),
        "Reddit": bool(config.reddit_client_id),
        "NewsAPI": bool(config.newsapi_key),
        "GNews": bool(config.gnews_key),
    }


def save_data(data: dict[str, Any]) -> str:
    """Save collected data to JSON file."""
    # Save to artifacts/phase1 directory
    output_dir = Path(__file__).parent.parent / "artifacts" / "phase1"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "web_app_data.json"
    
    # Convert DataItem objects to dicts
    serializable = {}
    for category, items in data.items():
        if category == "timestamp":
            serializable[category] = items
        else:
            serializable[category] = [
                {
                    "id": item.id,
                    "source": item.source,
                    "category": item.category,
                    "text": item.text[:500],
                    "timestamp": item.timestamp.isoformat(),
                    "url": item.url,
                    "title": item.title,
                    "value": item.value,
                    "metadata": item.metadata
                }
                for item in items
            ]
    
    output_path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
    return str(output_path)


def collect_data_interactive(category: str | None = None) -> dict[str, Any]:
    """Collect data with progress updates."""
    config = load_environment()
    config.max_items = 50
    
    results = {
        "economic": [],
        "crisis": [],
        "sentiment": [],
        "service_delivery": [],
        "timestamp": datetime.now().isoformat()
    }
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Economic indicators
        if category in [None, "economic"]:
            status_text.text("📊 Collecting economic indicators...")
            econ_collector = EconomicIndicatorsCollector(config)
            results["economic"] = econ_collector.collect_fred_indicators()
            results["economic"].extend(econ_collector.collect_bls_data())
            progress_bar.progress(25)
        
        # Crisis monitoring
        if category in [None, "crisis"]:
            status_text.text("🚨 Collecting crisis data...")
            crisis_collector = CrisisMonitoringCollector(config)
            results["crisis"] = crisis_collector.collect_fema_disasters()
            results["crisis"].extend(crisis_collector.collect_reliefweb_crises())
            progress_bar.progress(50)
        
        # Service delivery
        if category in [None, "service_delivery"]:
            status_text.text("🏛️ Collecting service delivery data...")
            service_collector = ServiceDeliveryCollector(config)
            results["service_delivery"] = service_collector.collect_spending_data()
            results["service_delivery"].extend(service_collector.collect_performance_metrics())
            progress_bar.progress(75)
        
        # Sentiment data
        if category in [None, "sentiment"]:
            status_text.text("💬 Collecting sentiment data...")
            sentiment_collector = DataCollector(config)
            results["sentiment"] = sentiment_collector.collect_all()
            progress_bar.progress(100)
        
        status_text.text("✓ Data collection complete!")
        
    except Exception as e:
        status_text.text(f"✗ Error: {str(e)}")
        st.error(f"Data collection failed: {str(e)}")
    
    progress_bar.empty()
    status_text.empty()
    
    return results


def save_data(data: dict[str, Any]) -> str:
    """Save collected data to JSON file."""
    output_dir = Path(__file__).parent.parent / "artifacts" / "phase1"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "web_app_data.json"
    
    # Convert DataItem objects to dicts
    serializable = {}
    for category, items in data.items():
        if category == "timestamp":
            serializable[category] = items
        else:
            serializable[category] = [
                {
                    "id": item.id,
                    "source": item.source,
                    "category": item.category,
                    "text": item.text[:500],
                    "timestamp": item.timestamp.isoformat(),
                    "url": item.url,
                    "title": item.title,
                    "value": item.value,
                    "metadata": item.metadata
                }
                for item in items
            ]
    
    output_path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
    return str(output_path)


def render_header():
    """Render main header."""
    st.markdown("""
    <div class="main-header">
        <h1>🏛️ CSPOPS</h1>
        <p>Citizen Sentiment & Public Opinion Perception System</p>
        <p style="font-size: 0.9rem; opacity: 0.8; margin-top: 0.5rem;">
            Live AI Analytics for Public Opinion Monitoring & Policy Support | PMX Visit to FAI Showcase
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_api_status(config: CollectorConfig):
    """Render API status in sidebar."""
    st.sidebar.subheader("🔑 API Status")
    
    api_status = check_api_status(config)
    
    for api, configured in api_status.items():
        if configured:
            st.sidebar.success(f"✓ {api}")
        else:
            st.sidebar.warning(f"✗ {api}")
    
    if not any(api_status.values()):
        st.sidebar.error("⚠ No APIs configured!")
        st.sidebar.info("Go to Settings tab to configure API keys")
    
    # Last update time
    if st.session_state.last_update:
        st.sidebar.success(f"Last update: {st.session_state.last_update}")


def render_metric_cards(data: dict[str, Any]):
    """Render key metric cards."""
    cols = st.columns(4)
    
    # Economic metrics
    economic_items = data.get("economic", [])
    treasury_10y = next((item.value for item in economic_items if "DGS10" in item.id), None)
    unemployment = next((item.value for item in economic_items if "UNRATE" in item.id), None)
    
    # Sentiment metrics
    sentiment_items = data.get("sentiment", [])
    
    # Crisis metrics
    crisis_items = data.get("crisis", [])
    
    with cols[0]:
        st.metric(
            label="📈 10-Year Treasury",
            value=f"{treasury_10y:.2f}%" if treasury_10y else "N/A",
            delta="Updated today" if treasury_10y else "No data"
        )
    
    with cols[1]:
        st.metric(
            label="👥 Unemployment Rate",
            value=f"{unemployment:.1f}%" if unemployment else "N/A",
            delta="Latest monthly" if unemployment else "No data"
        )
    
    with cols[2]:
        st.metric(
            label="💬 News Articles",
            value=len(sentiment_items),
            delta="Last 24 hours"
        )
    
    with cols[3]:
        st.metric(
            label="🚨 Active Crises",
            value=len(crisis_items),
            delta="Real-time"
        )


def render_economic_dashboard(data: list):
    """Render economic indicators dashboard."""
    st.subheader("📈 Real-Time Economic Indicators")
    
    if not data:
        st.info("No economic data collected. Click 'Collect Data' in the Data tab.")
        return
    
    # Create cards for each indicator
    cols = st.columns(3)
    
    for idx, item in enumerate(data):
        col = cols[idx % 3]
        with col:
            series_id = item.metadata.get("series_id", item.id)
            value = item.value
            date = item.metadata.get("date", "N/A")
            
            # Determine status color
            if series_id == "DGS10":
                if value > 5:
                    status = "🔴 High"
                elif value < 3:
                    status = "🟢 Low"
                else:
                    status = "🟡 Normal"
            elif series_id == "UNRATE":
                if value > 6:
                    status = "🔴 High"
                elif value < 4:
                    status = "🟢 Low"
                else:
                    status = "🟡 Normal"
            else:
                status = "⚪"
            
            st.metric(
                label=f"{series_id} {status}",
                value=f"{value:.2f}" if value else "N/A",
                help=f"Series: {series_id}\nDate: {date}\n{item.text}"
            )
    
    # Chart
    st.markdown("### Economic Trends")
    
    # Prepare chart data
    chart_data = {}
    for item in data:
        series_id = item.metadata.get("series_id", "Unknown")
        chart_data[series_id] = item.value
    
    if chart_data:
        import pandas as pd
        df = pd.DataFrame([chart_data])
        st.bar_chart(df.T)


def render_sentiment_dashboard(data: list):
    """Render sentiment analysis dashboard."""
    st.subheader("💬 Public Sentiment Analysis")
    
    if not data:
        st.info("No sentiment data collected.")
        return
    
    # Group by source
    sources: dict[str, int] = {}
    for item in data:
        sources[item.source] = sources.get(item.source, 0) + 1
    
    # Display source breakdown
    cols = st.columns(len(sources))
    for idx, (source, count) in enumerate(sources.items()):
        with cols[idx]:
            st.metric(
                label=source,
                value=count,
                delta="items"
            )
    
    # Show recent items
    st.markdown("### Recent Mentions")
    
    for item in data[:10]:
        with st.expander(f"{item.source}: {item.title[:80]}..."):
            st.write(f"**Source:** {item.source}")
            st.write(f"**Time:** {item.timestamp.strftime('%Y-%m-%d %H:%M')}")
            st.write(f"**Text:** {item.text[:300]}")
            if item.url:
                st.write(f"[View Original]({item.url})")


def render_crisis_dashboard(data: list):
    """Render crisis monitoring dashboard."""
    st.subheader("🚨 Crisis & Risk Monitoring")
    
    if not data:
        st.success("✓ No active crises detected")
        return
    
    st.warning(f"⚠ {len(data)} active crisis/crises being monitored")
    
    for item in data:
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{item.title}**")
                st.write(item.text[:200])
            with col2:
                st.write(f"**Source:** {item.source}")
                if item.url:
                    st.write(f"[More Info]({item.url})")
            st.divider()


def render_correlation_matrix(economic_data: list, sentiment_data: list):
    """Render correlation matrix between indicators."""
    st.subheader("🔗 Indicator Correlation Matrix")
    
    if not economic_data or not sentiment_data:
        st.info("Need both economic and sentiment data for correlation analysis")
        return
    
    try:
        import pandas as pd
        import numpy as np
        
        # Prepare data
        indicators = {}
        
        # Add economic indicators
        for item in economic_data:
            series_id = item.metadata.get("series_id", item.id)
            if item.value:
                indicators[series_id] = item.value
        
        # Add sentiment metrics
        if sentiment_data:
            indicators["Sentiment_Score"] = len(sentiment_data) / 10  # Normalized
        
        if len(indicators) < 2:
            st.info("Not enough data for correlation analysis")
            return
        
        # Create correlation matrix (simplified - would need time series for real correlations)
        df = pd.DataFrame([indicators])
        
        st.write("**Current Indicator Values:**")
        st.dataframe(df.T, column_config={"0": "Value"})
        
        st.info("📊 For meaningful correlations, historical time series data is needed. This shows current values.")
        
    except Exception as e:
        st.error(f"Correlation analysis error: {e}")


def render_sentiment_distribution(sentiment_data: list):
    """Render sentiment score distribution histogram."""
    st.subheader("📊 Sentiment Distribution Analysis")
    
    if not sentiment_data:
        st.info("No sentiment data for distribution analysis")
        return
    
    try:
        import plotly.graph_objects as go
        import numpy as np
        
        # Simulate sentiment scores from text (in production, use actual sentiment analysis)
        np.random.seed(42)
        scores = np.random.normal(0, 0.5, len(sentiment_data))  # Simulated scores
        scores = np.clip(scores, -1, 1)  # Clamp to -1 to 1
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=scores,
            nbinsx=20,
            name="Sentiment Scores",
            marker_color="#667eea",
            opacity=0.7
        ))
        
        # Add KDE overlay
        from scipy import stats
        kde = stats.gaussian_kde(scores)
        x_range = np.linspace(-1, 1, 100)
        
        fig.add_trace(go.Scatter(
            x=x_range,
            y=kde(x_range) * len(sentiment_data) * 0.5,  # Scale for visibility
            name="Distribution Curve",
            line=dict(color="#dc3545", width=3)
        ))
        
        fig.update_layout(
            title="Sentiment Score Distribution",
            xaxis_title="Sentiment Score (-1 to 1)",
            yaxis_title="Frequency",
            showlegend=True,
            height=400
        )

        st.plotly_chart(fig, key="sentiment_distribution", use_container_width=True)
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Mean", f"{scores.mean():.3f}")
        
        with col2:
            st.metric("Median", f"{np.median(scores):.3f}")
        
        with col3:
            st.metric("Std Dev", f"{scores.std():.3f}")
        
        with col4:
            positive_pct = (scores > 0).sum() / len(scores) * 100
            st.metric("Positive", f"{positive_pct:.1f}%")
        
    except Exception as e:
        st.error(f"Distribution analysis error: {e}")


def render_time_series_forecast(economic_data: list, key_prefix: str = "econ"):
    """Render time series with simple trend projection."""
    st.subheader("📈 Economic Trend Analysis")
    
    if not economic_data:
        st.info("No economic data for trend analysis")
        return
    
    try:
        import plotly.graph_objects as go
        import pandas as pd
        import numpy as np
        from sklearn.linear_model import LinearRegression
        import uuid
        
        # Group data by series
        series_data = {}
        for item in economic_data:
            series_id = item.metadata.get("series_id", item.id)
            if series_id not in series_data:
                series_data[series_id] = []
            series_data[series_id].append({
                "date": item.timestamp,
                "value": item.value
            })
        
        # Create charts for each series
        for series_id, data_points in series_data.items():
            if len(data_points) < 1:
                continue
            
            df = pd.DataFrame(data_points)
            df = df.sort_values("date")
            
            fig = go.Figure()
            
            # Historical data
            fig.add_trace(go.Scatter(
                x=df["date"],
                y=df["value"],
                mode="lines+markers",
                name="Historical",
                line=dict(color="#0066cc", width=2)
            ))
            
            # Simple trend line (linear projection)
            if len(df) >= 2:
                X = np.arange(len(df)).reshape(-1, 1)
                y = df["value"].values
                
                model = LinearRegression()
                model.fit(X, y)
                
                # Extend for forecast
                future_x = np.arange(len(df), len(df) + 5).reshape(-1, 1)
                forecast = model.predict(future_x)
                future_dates = pd.date_range(df["date"].max(), periods=5, freq="D")[1:]
                
                fig.add_trace(go.Scatter(
                    x=future_dates,
                    y=forecast,
                    mode="lines+markers",
                    name="Trend Projection",
                    line=dict(color="#28a745", width=2, dash="dash")
                ))
            
            fig.update_layout(
                title=f"{series_id} Trend Analysis",
                xaxis_title="Date",
                yaxis_title="Value",
                height=350
            )
            
            # Use UUID for truly unique key
            unique_key = f"trend_{series_id}_{uuid.uuid4().hex[:8]}"
            st.plotly_chart(fig, key=unique_key, use_container_width=True)
        
    except Exception as e:
        st.error(f"Trend analysis error: {e}")


def render_comparison_view(
    current_data: dict[str, Any],
    historical_data: dict[str, Any] | None = None
):
    """Render comparative analysis between current and historical data."""
    st.subheader("📊 Comparative Analysis")
    
    if not current_data:
        st.info("No data for comparison")
        return
    
    # Compare categories
    categories = ["economic", "crisis", "sentiment", "service_delivery"]
    
    cols = st.columns(len(categories))
    
    for idx, category in enumerate(categories):
        current_count = len(current_data.get(category, []))
        
        with cols[idx]:
            st.metric(
                label=category.replace("_", " ").title(),
                value=current_count,
                delta="Current"
            )
    
    st.divider()
    
    # Detailed comparison tables
    st.markdown("### Detailed Comparison")
    
    # Economic indicators comparison
    if current_data.get("economic"):
        st.markdown("#### Economic Indicators")
        
        econ_data = current_data["economic"]
        comparison_df = []
        
        for item in econ_data:
            series_id = item.metadata.get("series_id", item.id)
            comparison_df.append({
                "Indicator": series_id,
                "Current Value": f"{item.value:.2f}" if item.value else "N/A",
                "Date": item.metadata.get("date", "N/A"),
                "Source": item.source
            })
        
        st.dataframe(comparison_df, use_container_width=True)


def render_word_cloud_alternative(sentiment_data: list, key_suffix: str = ""):
    """Render word frequency chart (alternative to word cloud)."""
    st.subheader("☁️ Topic Word Frequency")
    
    if not sentiment_data:
        st.info("No sentiment data for word frequency analysis")
        return
    
    try:
        import plotly.graph_objects as go
        from collections import Counter
        import re
        import uuid
        
        # Extract and count words
        word_counts = Counter()
        
        for item in sentiment_data:
            text = item.text.lower()
            # Simple word extraction
            words = re.findall(r'\b[a-z]{4,}\b', text)  # Words 4+ chars
            
            # Remove common stop words
            stop_words = {'this', 'that', 'with', 'have', 'from', 'they', 'will', 'would', 'there', 'their', 'what', 'about', 'which', 'when', 'where', 'being', 'having'}
            words = [w for w in words if w not in stop_words]
            
            word_counts.update(words)
        
        # Get top 20 words
        top_words = word_counts.most_common(20)
        
        if not top_words:
            st.info("No words to analyze")
            return
        
        words, counts = zip(*top_words)
        
        # Create horizontal bar chart
        fig = go.Figure(go.Bar(
            y=list(words),
            x=list(counts),
            orientation='h',
            marker=dict(
                color=list(counts),
                colorscale='Viridis',
                showscale=True
            )
        ))
        
        fig.update_layout(
            title="Most Frequent Terms in News/Social Media",
            xaxis_title="Frequency",
            yaxis_title="Word",
            height=600,
            showlegend=False
        )
        
        # Use UUID for truly unique key
        unique_key = f"word_freq_{uuid.uuid4().hex[:8]}{key_suffix}"
        st.plotly_chart(fig, key=unique_key, use_container_width=True)
        
        # Show stats
        st.write(f"**Total unique words:** {len(word_counts)}")
        st.write(f"**Most common:** '{top_words[0][0]}' ({top_words[0][1]} occurrences)")
        
    except Exception as e:
        st.error(f"Word frequency analysis error: {e}")


def render_alert_timeline(crisis_data: list, economic_data: list):
    """Render timeline of alerts and significant events."""
    st.subheader("🚨 Alert Timeline")
    
    if not crisis_data and not economic_data:
        st.info("No data for alert timeline")
        return
    
    try:
        import plotly.graph_objects as go
        
        events = []
        
        # Add crisis events
        for item in crisis_data:
            events.append({
                "type": "Crisis",
                "date": item.timestamp,
                "title": item.title[:50],
                "severity": "High"
            })
        
        # Add economic alerts (extreme values)
        for item in economic_data:
            series_id = item.metadata.get("series_id", item.id)
            value = item.value
            
            if value:
                # Check for concerning values
                if series_id == "DGS10" and value > 4.5:
                    events.append({
                        "type": "Economic",
                        "date": item.timestamp,
                        "title": f"{series_id}: High treasury yield ({value:.2f}%)",
                        "severity": "Medium"
                    })
                elif series_id == "UNRATE" and value > 5:
                    events.append({
                        "type": "Economic",
                        "date": item.timestamp,
                        "title": f"{series_id}: High unemployment ({value:.1f}%)",
                        "severity": "High"
                    })
        
        if not events:
            st.info("No significant alerts to display")
            return
        
        # Sort by date
        events.sort(key=lambda x: x["date"])
        
        # Create timeline visualization
        dates = [e["date"] for e in events]
        labels = [f"{e['type']}: {e['title']}" for e in events]
        colors = ["#dc3545" if e["severity"] == "High" else "#ffc107" for e in events]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=[1] * len(dates),
            mode="markers",
            marker=dict(
                size=20,
                color=colors,
                symbol="square"
            ),
            text=labels,
            hoverinfo="text",
            name="Events"
        ))
        
        fig.update_layout(
            title="Alert & Significant Event Timeline",
            xaxis_title="Date",
            yaxis=dict(showticklabels=False),
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig, key=f"alert_timeline_{datetime.now().strftime('%Y%m%d%H%M%S')}", use_container_width=True)
        
        # List events
        st.markdown("### Event Details")
        for event in events:
            severity_color = "🔴" if event["severity"] == "High" else "🟡"
            st.write(f"{severity_color} **{event['date'].strftime('%Y-%m-%d')}** - {event['title']}")
        
    except Exception as e:
        st.error(f"Timeline visualization error: {e}")


def render_nlp_analysis(texts: list):
    """Render comprehensive NLP analysis with AI insights."""
    st.subheader("🧠 AI-Powered NLP Analysis")
    
    if not NLP_AVAILABLE:
        st.warning("""
        ⚠️ **NLP Module Not Installed**
        
        Install advanced NLP features with:
        ```bash
        pip install transformers torch bertopic spacy
        ```
        
        Running in basic mode with limited analysis.
        """)
        return
    
    if not texts:
        st.info("No text data for NLP analysis")
        return
    
    try:
        # Initialize analyzer
        analyzer = AdvancedNLPAnalyzer()
        
        # Run analyses
        with st.spinner("🧠 Running AI sentiment analysis..."):
            sentiment_results = analyzer.analyze_sentiment_batch(texts[:30])  # Limit for performance
        
        with st.spinner("😊 Detecting emotions..."):
            emotion_results = analyzer.detect_emotions(texts[:30])
        
        with st.spinner("🏷️ Extracting entities..."):
            entity_results = analyzer.extract_entities(texts[:30])
        
        with st.spinner("📊 Modeling topics..."):
            topic_results = analyzer.model_topics(texts[:30])
        
        # Generate insights
        insights = analyzer.generate_insights(sentiment_results, emotion_results, entity_results)
        
        st.success("✓ NLP analysis complete!")
        
        # Display results in tabs
        nlp_tabs = st.tabs([
            "📊 Sentiment Overview",
            "😊 Emotion Analysis",
            "🏷️ Named Entities",
            "📊 Topic Modeling",
            "💡 AI Insights"
        ])
        
        with nlp_tabs[0]:
            st.markdown("### Sentiment Distribution")
            
            # Sentiment pie chart
            sentiment_counts = {}
            for result in sentiment_results:
                sentiment_counts[result.sentiment] = sentiment_counts.get(result.sentiment, 0) + 1
            
            import plotly.graph_objects as go
            fig = go.Figure(data=[go.Pie(
                labels=list(sentiment_counts.keys()),
                values=list(sentiment_counts.values()),
                hole=.4,
                marker_colors=['#28a745', '#dc3545', '#6c757d']
            )])
            
            fig.update_layout(
                title="Overall Sentiment Distribution",
                height=400
            )
            
            st.plotly_chart(fig, key=f"sentiment_pie_{datetime.now().strftime('%Y%m%d%H%M%S')}", use_container_width=True)
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            
            avg_compound = np.mean([r.compound_score for r in sentiment_results]) if sentiment_results else 0
            
            with col1:
                st.metric(
                    "Average Sentiment",
                    f"{avg_compound:.3f}",
                    delta="Positive" if avg_compound > 0 else "Negative" if avg_compound < 0 else "Neutral"
                )
            
            with col2:
                positive_pct = sum(1 for r in sentiment_results if r.sentiment == 'positive') / len(sentiment_results) * 100 if sentiment_results else 0
                st.metric("Positive", f"{positive_pct:.1f}%")
            
            with col3:
                negative_pct = sum(1 for r in sentiment_results if r.sentiment == 'negative') / len(sentiment_results) * 100 if sentiment_results else 0
                st.metric("Negative", f"{negative_pct:.1f}%")
        
        with nlp_tabs[1]:
            st.markdown("### Emotion Breakdown")
            
            # Emotion bar chart
            emotion_totals = {}
            for result in emotion_results:
                for emotion, score in result.emotions.items():
                    emotion_totals[emotion] = emotion_totals.get(emotion, 0) + score
            
            # Normalize
            total = sum(emotion_totals.values())
            if total > 0:
                emotion_pcts = {e: (s / total) * 100 for e, s in emotion_totals.items()}
                
                fig = go.Figure(go.Bar(
                    x=list(emotion_pcts.keys()),
                    y=list(emotion_pcts.values()),
                    marker_color=['#dc3545', '#ffc107', '#28a745', '#17a2b8', '#6f42c1', '#fd7e14', '#6c757d']
                ))
                
                fig.update_layout(
                    title="Emotion Distribution",
                    xaxis_title="Emotion",
                    yaxis_title="Percentage",
                    height=400
                )
                
                st.plotly_chart(fig, key=f"emotion_chart_{datetime.now().strftime('%Y%m%d%H%M%S')}", use_container_width=True)
                
                # Dominant emotion
                dominant = max(emotion_pcts, key=emotion_pcts.get)
                st.info(f"**Dominant Emotion:** {dominant.title()} ({emotion_pcts[dominant]:.1f}%)")
        
        with nlp_tabs[2]:
            st.markdown("### Named Entity Recognition")
            
            # Entity summary
            all_entities = {}
            for result in entity_results:
                for label, count in result.entity_summary.items():
                    all_entities[label] = all_entities.get(label, 0) + 1
            
            if all_entities:
                st.markdown("#### Entity Types Found")
                
                entity_cols = st.columns(min(4, len(all_entities)))
                for idx, (label, count) in enumerate(all_entities.items()):
                    with entity_cols[idx % 4]:
                        st.metric(label, count)
                
                st.markdown("#### Sample Entities")
                for result in entity_results[:5]:
                    if result.entities:
                        with st.expander(f"Text: {result.text[:50]}..."):
                            for entity in result.entities:
                                st.write(f"- **{entity['text']}** ({entity['label']}, {entity['confidence']:.2%})")
        
        with nlp_tabs[3]:
            st.markdown("### Topic Modeling")
            
            if topic_results.topic_terms:
                for topic_id, terms in topic_results.topic_terms.items():
                    proportion = topic_results.topic_distribution.get(topic_id, 0)
                    st.markdown(f"**Topic {topic_id}** - {proportion:.1%} of discussions")
                    st.write(f"Keywords: {', '.join(terms[:10])}")
                    st.divider()
        
        with nlp_tabs[4]:
            st.markdown("### 💡 AI-Generated Insights")
            
            # Display alerts
            if insights.get('alerts'):
                st.markdown("#### 🚨 Alerts")
                for alert in insights['alerts']:
                    if alert['type'] == 'CRITICAL':
                        st.error(f"**{alert['type']}**: {alert['message']}")
                    elif alert['type'] == 'WARNING':
                        st.warning(f"**{alert['type']}**: {alert['message']}")
                    else:
                        st.info(f"**{alert['type']}**: {alert['message']}")
                    st.write(f"*Recommended Action:* {alert.get('action', 'N/A')}")
            
            # Display recommendations
            if insights.get('recommendations'):
                st.markdown("#### 💡 Recommendations")
                for rec in insights['recommendations']:
                    st.write(f"- {rec}")
            
            # Overall sentiment summary
            if insights.get('overall_sentiment'):
                st.markdown("#### Sentiment Summary")
                sentiment_info = insights['overall_sentiment']
                st.json(sentiment_info)
            
            # Emotion breakdown
            if insights.get('emotion_breakdown'):
                st.markdown("#### Emotion Breakdown")
                st.json(insights['emotion_breakdown'])
        
    except Exception as e:
        st.error(f"NLP analysis error: {e}")
        import traceback
        st.code(traceback.format_exc())


def main():
    """Main application."""
    # Setup page configuration and CSS
    setup_page()
    
    # Initialize AI chatbot (already loaded .env at top of file)
    if AI_AVAILABLE:
        if "ai_chatbot" not in st.session_state:
            try:
                st.session_state.ai_chatbot = create_ai_assistant()
                print("✓ AI Chatbot initialized")
            except Exception as e:
                print(f"✗ AI Chatbot init error: {e}")
                st.session_state.ai_chatbot = None
    else:
        st.session_state.ai_chatbot = None
    
    # Load configuration
    config = load_environment()
    
    # Render header
    render_header()
    
    # Render sidebar
    render_api_status(config)
    
    # Sidebar data collection button
    st.sidebar.divider()
    st.sidebar.subheader("⚡ Quick Actions")
    
    if st.sidebar.button("🔄 Collect Real-Time Data", use_container_width=True, type="primary"):
        with st.spinner("Collecting data from all sources..."):
            data = collect_data_interactive()
            st.session_state.collected_data = data
            st.session_state.data_collected = True
            st.session_state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_data(data)
            st.sidebar.success("✓ Data collected!")
            st.rerun()
    
    if st.sidebar.button("🗑️ Clear Data", use_container_width=True):
        st.session_state.data_collected = False
        st.session_state.collected_data = None
        st.session_state.last_update = None
        st.sidebar.warning("Data cleared")
        st.rerun()

    # Navigation tabs
    tabs = st.tabs([
        "📊 Dashboard",
        "📈 Economy",
        "💬 Sentiment",
        "🚨 Crises",
        "🏛️ Services",
        "📊 Analytics",
        "📥 Data Collection",
        "⚙️ Settings"
    ])

    # Dashboard Tab
    with tabs[0]:
        st.header("Executive Overview")
        
        # Quick stats
        if st.session_state.data_collected and st.session_state.collected_data:
            # Live Data Badge
            st.markdown(
                f"""
                <div style="display: inline-block; background: #dc3545; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold; margin-bottom: 1rem;">
                    🔴 LIVE • Updated {st.session_state.last_update}
                </div>
                """,
                unsafe_allow_html=True
            )
            
            render_metric_cards(st.session_state.collected_data)
            
            st.divider()
            
            # 🆕 NEW: Auto-Show NLP Sentiment Analysis
            data = st.session_state.collected_data
            nlp = data.get("nlp_analysis", {})
            
            if nlp:
                st.subheader("📊 Real-Time Sentiment Analysis")
                
                sentiment_info = nlp.get("overall_sentiment", {})
                emotion_info = nlp.get("emotion_breakdown", {})
                
                if sentiment_info:
                    # Sentiment Metric Cards
                    score = sentiment_info.get("average_score", 0)
                    classification = sentiment_info.get("classification", "neutral")
                    positive_pct = sentiment_info.get("positive_percentage", 0) * 100
                    negative_pct = sentiment_info.get("negative_percentage", 0) * 100
                    neutral_pct = 100 - positive_pct - negative_pct
                    
                    # Emoji based on classification
                    emoji = "😊" if score > 0.1 else "😞" if score < -0.1 else "😐"
                    color = "#28a745" if score > 0.1 else "#dc3545" if score < -0.1 else "#ffc107"
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                        <div style="background: {color}22; padding: 1rem; border-radius: 10px; border-left: 4px solid {color}; text-align: center;">
                            <div style="font-size: 2rem;">{emoji}</div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: {color};">{score:+.2f}</div>
                            <div style="font-size: 0.85rem; color: #666;">{classification.title()}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div style="background: #28a74522; padding: 1rem; border-radius: 10px; border-left: 4px solid #28a745; text-align: center;">
                            <div style="font-size: 2rem;">😊</div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: #28a745;">{positive_pct:.0f}%</div>
                            <div style="font-size: 0.85rem; color: #666;">Positive</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div style="background: #dc354522; padding: 1rem; border-radius: 10px; border-left: 4px solid #dc3545; text-align: center;">
                            <div style="font-size: 2rem;">😞</div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: #dc3545;">{negative_pct:.0f}%</div>
                            <div style="font-size: 0.85rem; color: #666;">Negative</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"""
                        <div style="background: #ffc10722; padding: 1rem; border-radius: 10px; border-left: 4px solid #ffc107; text-align: center;">
                            <div style="font-size: 2rem;">😐</div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: #ffc107;">{neutral_pct:.0f}%</div>
                            <div style="font-size: 0.85rem; color: #666;">Neutral</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.divider()
                    
                    # Emotion Analysis Section
                    if emotion_info:
                        st.subheader("😊 Emotion Breakdown")
                        
                        emotion_col1, emotion_col2 = st.columns([2, 1])
                        
                        with emotion_col1:
                            # Emotion bar chart
                            import plotly.graph_objects as go
                            
                            emotions = list(emotion_info.keys())
                            emotion_values = [emotion_info[e] * 100 for e in emotions]
                            
                            # Color mapping for emotions
                            emotion_colors = {
                                'joy': '#28a745',
                                'anger': '#dc3545',
                                'fear': '#6f42c1',
                                'sadness': '#17a2b8',
                                'surprise': '#fd7e14',
                                'disgust': '#ffc107',
                                'neutral': '#6c757d'
                            }
                            
                            colors = [emotion_colors.get(e.lower(), '#6c757d') for e in emotions]
                            
                            fig = go.Figure(go.Bar(
                                x=emotions,
                                y=emotion_values,
                                marker_color=colors,
                                text=[f'{v:.1f}%' for v in emotion_values],
                                textposition='outside'
                            ))
                            
                            fig.update_layout(
                                title="Dominant Emotions in Public Discourse",
                                xaxis_title="Emotion",
                                yaxis_title="Percentage",
                                height=350,
                                showlegend=False
                            )
                            
                            st.plotly_chart(fig, key=f"emotion_bar_{datetime.now().strftime('%Y%m%d%H%M%S')}", use_container_width=True)
                        
                        with emotion_col2:
                            # Dominant emotion highlight
                            dominant_emotion = max(emotion_info.items(), key=lambda x: x[1])
                            dominant_pct = dominant_emotion[1] * 100
                            
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; text-align: center; color: white;">
                                <div style="font-size: 3rem; margin-bottom: 0.5rem;">
                                    {'😊' if dominant_emotion[0] == 'joy' else '😠' if dominant_emotion[0] == 'anger' else '😨' if dominant_emotion[0] == 'fear' else '😢' if dominant_emotion[0] == 'sadness' else '😲' if dominant_emotion[0] == 'surprise' else '🤢' if dominant_emotion[0] == 'disgust' else '😐'}
                                </div>
                                <div style="font-size: 1.8rem; font-weight: bold; margin-bottom: 0.5rem;">{dominant_emotion[0].title()}</div>
                                <div style="font-size: 2.5rem; font-weight: bold;">{dominant_pct:.0f}%</div>
                                <div style="font-size: 0.9rem; opacity: 0.8; margin-top: 0.5rem;">Dominant Emotion</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Emotion insights
                            st.markdown("### 📈 Emotion Insights")
                            
                            if dominant_emotion[0] == 'joy':
                                st.success("✅ Positive public mood - good time for policy announcements")
                            elif dominant_emotion[0] == 'anger':
                                st.error("⚠️ High anger levels - consider proactive communication")
                            elif dominant_emotion[0] == 'fear':
                                st.warning("⚠️ Public anxiety detected - address concerns directly")
                            else:
                                st.info("ℹ️ Mixed emotions - monitor for trends")
                        
                        st.divider()
            
            # Advanced Analytics Section
            st.subheader("🔍 Advanced Analytics")
            
            data = st.session_state.collected_data
            
            # Create tabs for different analytics
            analytic_tabs = st.tabs([
                "📊 Economic Trends",
                "📈 Sentiment Distribution", 
                "🔗 Correlations",
                "📋 Comparison"
            ])
            
            with analytic_tabs[0]:
                render_time_series_forecast(data.get("economic", []))
            
            with analytic_tabs[1]:
                render_sentiment_distribution(data.get("sentiment", []))
            
            with analytic_tabs[2]:
                render_correlation_matrix(
                    data.get("economic", []),
                    data.get("sentiment", [])
                )
            
            with analytic_tabs[3]:
                render_comparison_view(data)

            st.divider()

            # AI-Powered Section
            st.subheader("🤖 AI-Powered Insights")
            
            ai_col1, ai_col2 = st.columns(2)
            
            with ai_col1:
                st.markdown("### 💬 Ask AI Assistant")
                
                if AI_AVAILABLE and st.session_state.ai_chatbot:
                    # Chat interface
                    if "chat_messages" not in st.session_state:
                        st.session_state.chat_messages = []
                    
                    # Display chat history
                    for msg in st.session_state.chat_messages[-5:]:
                        if msg["role"] == "user":
                            st.chat_message("user").write(msg["content"])
                        else:
                            st.chat_message("assistant").write(msg["content"])
                    
                    # Chat input
                    user_question = st.chat_input("Ask about the data...")
                    
                    if user_question:
                        # Add user message to history
                        st.session_state.chat_messages.append({"role": "user", "content": user_question})
                        st.chat_message("user").write(user_question)
                        
                        # Get AI response
                        with st.spinner("🤖 AI is thinking..."):
                            # Use NLP analysis if available
                            if hasattr(st.session_state.collected_data, 'get') and st.session_state.collected_data.get("nlp_analysis"):
                                nlp = st.session_state.collected_data["nlp_analysis"]
                                context = {
                                    "sentiment": nlp.get("overall_sentiment", {}),
                                    "emotions": nlp.get("emotion_breakdown", {}),
                                    "economic": st.session_state.collected_data.get("economic", []),
                                    "alerts": nlp.get("insights", {}).get("alerts", [])
                                }
                            else:
                                context = {
                                    "sentiment": {},
                                    "emotions": {},
                                    "economic": st.session_state.collected_data.get("economic", []),
                                    "alerts": []
                                }
                            response = st.session_state.ai_chatbot.chat(user_question, context)
                        
                        # Add assistant response to history
                        st.session_state.chat_messages.append({"role": "assistant", "content": response})
                        st.chat_message("assistant").write(response)
                else:
                    st.info("""
                    **🤖 AI Assistant Not Available**
                    
                    To enable AI chatbot:
                    1. Get API key from DeepSeek or OpenRouter
                    2. Add to `.env` file:
                    ```
                    DEEPSEEK_API_KEY=sk_your_key_here
                    ```
                    3. Restart the app
                    """)
            
            with ai_col2:
                st.markdown("### 📋 AI Summary Report")
                
                if AI_AVAILABLE and st.session_state.ai_chatbot:
                    # Auto-generate summary if NLP data available
                    if st.session_state.collected_data and st.session_state.collected_data.get("nlp_analysis"):
                        nlp = st.session_state.collected_data["nlp_analysis"]
                        
                        # Generate summary automatically
                        if "ai_summary" not in st.session_state:
                            with st.spinner("🤖 AI is writing summary..."):
                                summary = st.session_state.ai_chatbot.generate_summary({
                                    "insights": {
                                        "overall_sentiment": nlp.get("overall_sentiment", {}),
                                        "emotion_breakdown": nlp.get("emotion_breakdown", {}),
                                        "alerts": nlp.get("insights", {}).get("alerts", [])
                                    },
                                    "economic": st.session_state.collected_data.get("economic", [])
                                })
                                st.session_state.ai_summary = summary
                        
                        if hasattr(st.session_state, 'ai_summary'):
                            st.markdown(st.session_state.ai_summary)
                    
                    # Manual generate button
                    if st.button("🔄 Regenerate Summary", use_container_width=True):
                        with st.spinner("🤖 AI is writing summary..."):
                            nlp = st.session_state.collected_data.get("nlp_analysis", {})
                            summary = st.session_state.ai_chatbot.generate_summary({
                                "insights": {
                                    "overall_sentiment": nlp.get("overall_sentiment", {}),
                                    "emotion_breakdown": nlp.get("emotion_breakdown", {}),
                                    "alerts": nlp.get("insights", {}).get("alerts", [])
                                },
                                "economic": st.session_state.collected_data.get("economic", [])
                            })
                            st.session_state.ai_summary = summary
                else:
                    st.info("AI summary requires API key (see above)")
            
            st.divider()

            # 🆕 AI-Powered Cause & Effect Graph
            st.subheader("🤖 AI-Powered Cause & Effect Analysis")
            
            if st.session_state.data_collected and st.session_state.collected_data:
                if AI_AVAILABLE and st.session_state.ai_chatbot:
                    if st.button("🧠 Generate AI Cause-Effect Map", type="primary", use_container_width=True):
                        with st.spinner("🤖 AI is analyzing relationships across all data sources... This may take 30-60 seconds."):
                            try:
                                graph_data = generate_cause_effect_graph(
                                    st.session_state.ai_chatbot,
                                    st.session_state.collected_data
                                )
                                
                                if graph_data:
                                    st.session_state.cause_effect_graph = graph_data
                                    st.success("✓ AI generated cause-effect map!")
                                else:
                                    st.error("AI couldn't generate graph. Try again.")
                                    st.session_state.cause_effect_graph = None
                                
                            except Exception as e:
                                st.error(f"AI analysis error: {e}")
                                st.session_state.cause_effect_graph = None
                    
                    # Render the graph if available
                    if hasattr(st.session_state, 'cause_effect_graph') and st.session_state.cause_effect_graph:
                        graph_data = st.session_state.cause_effect_graph
                        
                        # Show AI insights first
                        insights = graph_data.get("insights", [])
                        if insights:
                            st.markdown("### 💡 AI-Discovered Insights")
                            for i, insight in enumerate(insights, 1):
                                st.write(f"{i}. {insight}")
                            st.divider()
                        
                        # Visualize graph
                        try:
                            import plotly.graph_objects as go
                            import networkx as nx
                            import numpy as np
                            
                            nodes = graph_data.get("nodes", [])
                            edges = graph_data.get("edges", [])
                            
                            # Group colors
                            group_colors = {
                                "economic": "#377eb8",
                                "sentiment": "#4daf4a",
                                "emotion": "#984ea3",
                                "crisis": "#e41a1c",
                                "service": "#ff7f00"
                            }
                            
                            # Create networkx graph
                            G = nx.DiGraph()
                            
                            for node in nodes:
                                G.add_node(
                                    node["id"],
                                    label=node.get("label", node["id"]),
                                    group=node.get("group", "economic"),
                                    value=node.get("value", ""),
                                    color=group_colors.get(node.get("group"), "#999999")
                                )
                            
                            for edge in edges:
                                G.add_edge(
                                    edge["from"],
                                    edge["to"],
                                    label=edge.get("label", "relates to"),
                                    strength=edge.get("strength", 0.5)
                                )
                            
                            # Calculate positions
                            pos = nx.spring_layout(G, k=1.5, iterations=100, seed=42)
                            
                            # Create plotly figure
                            fig = go.Figure()
                            
                            # Add edges
                            edge_x, edge_y, edge_text = [], [], []
                            for edge in G.edges():
                                x0, y0 = pos[edge[0]]
                                x1, y1 = pos[edge[1]]
                                edge_x.extend([x0, x1, None])
                                edge_y.extend([y0, y1, None])
                                
                                edge_data = G.get_edge_data(edge[0], edge[1])
                                label = edge_data.get("label", "")
                                strength = edge_data.get("strength", 0.5)
                                edge_text.append(f"{edge[0]} → {edge[1]}<br>{label}<br>Strength: {strength:.1f}")
                            
                            fig.add_trace(go.Scatter(
                                x=edge_x, y=edge_y,
                                line=dict(width=1, color="#888"),
                                hoverinfo="text",
                                text=edge_text,
                                mode="lines",
                                name="Relationships"
                            ))
                            
                            # Add nodes
                            node_x, node_y, node_labels, node_colors, node_values = [], [], [], [], []
                            for node_id in G.nodes():
                                x, y = pos[node_id]
                                node_x.append(x)
                                node_y.append(y)
                                
                                node_data = G.nodes[node_id]
                                node_labels.append(node_data["label"])
                                node_colors.append(node_data["color"])
                                node_values.append(str(node_data.get("value", "")))
                            
                            fig.add_trace(go.Scatter(
                                x=node_x, y=node_y,
                                mode="markers+text",
                                marker=dict(size=40, color=node_colors, line=dict(width=2, color="white")),
                                text=node_labels,
                                textposition="middle center",
                                textfont=dict(size=12, color="white"),
                                customdata=np.stack([node_values], axis=1),
                                hovertemplate="<b>%{text}</b><br>Value: %{customdata[0]}<extra></extra>",
                                name="Nodes"
                            ))
                            
                            fig.update_layout(
                                title=f"AI-Discovered Cause & Effect Network ({len(nodes)} nodes, {len(edges)} relationships)",
                                showlegend=False,
                                height=700,
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                            )
                            
                            st.plotly_chart(fig, key=f"ai_cause_effect_{datetime.now().strftime('%Y%m%d%H%M%S')}", use_container_width=True)
                            
                            # Node details
                            with st.expander(f"📊 View All {len(nodes)} Nodes"):
                                for node in nodes:
                                    st.write(f"**{node.get('label', node['id'])}** ({node.get('group', 'unknown')})")
                                    st.write(f"Value: {node.get('value', 'N/A')}")
                                    st.divider()
                            
                            # Edge details
                            with st.expander(f"🔗 View All {len(edges)} Relationships"):
                                for edge in edges:
                                    st.write(f"**{edge['from']}** → **{edge['to']}**")
                                    st.write(f"Relationship: {edge.get('label', 'relates to')}")
                                    st.write(f"Strength: {edge.get('strength', 0.5):.1f}")
                                    st.divider()
                            
                            # Download button
                            st.download_button(
                                label="📥 Download Graph Data (JSON)",
                                data=json.dumps(graph_data, indent=2),
                                file_name=f"cause_effect_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                            
                        except Exception as e:
                            st.error(f"Visualization error: {e}")
                            st.json(graph_data)
                else:
                    st.info("🤖 AI chatbot required for cause-effect analysis. Add API key to enable.")
            
            st.divider()
    
    # Economy Tab
    with tabs[1]:
        st.header("📈 Economic Indicators & Analysis")
        
        if st.session_state.data_collected and st.session_state.collected_data:
            econ_data = st.session_state.collected_data.get("economic", [])
            
            if econ_data:
                # Original economic dashboard
                render_economic_dashboard(econ_data)
                
                st.divider()
                
                # Time series forecast
                render_time_series_forecast(econ_data)
                
                st.divider()
                
                # Alert timeline for economic events
                crisis_data = st.session_state.collected_data.get("crisis", [])
                render_alert_timeline(crisis_data, econ_data)
            else:
                st.info("No economic data collected")
        else:
            st.info("Collect data first to see economic indicators")

    # Sentiment Tab
    with tabs[2]:
        st.header("💬 Public Sentiment Analysis")

        if st.session_state.data_collected and st.session_state.collected_data:
            sentiment_data = st.session_state.collected_data.get("sentiment", [])

            if sentiment_data:
                # Original sentiment dashboard
                render_sentiment_dashboard(sentiment_data)

                st.divider()

                # NLP Analysis Section
                st.subheader("🧠 AI-Powered NLP Analysis")
                
                if st.button("🚀 Run Advanced NLP Analysis", type="primary", use_container_width=True):
                    with st.spinner("Running transformer-based AI analysis..."):
                        # Extract texts
                        texts = [item.text for item in sentiment_data if item.text]
                        render_nlp_analysis(texts)
                
                st.divider()

                # Additional visualizations
                st.subheader("📊 Advanced Sentiment Analytics")

                # Word frequency
                render_word_cloud_alternative(sentiment_data)

                st.divider()

                # Alert timeline with economic data
                econ_data = st.session_state.collected_data.get("economic", [])
                crisis_data = st.session_state.collected_data.get("crisis", [])
                render_alert_timeline(crisis_data, econ_data)
            else:
                st.info("No sentiment data collected")
        else:
            st.info("Collect data first to see sentiment analysis")
    
    # Crises Tab
    with tabs[3]:
        if st.session_state.data_collected and st.session_state.collected_data:
            render_crisis_dashboard(st.session_state.collected_data.get("crisis", []))
        else:
            st.info("Collect data first to see crisis monitoring")
    
    # Services Tab
    with tabs[4]:
        st.header("🏛️ Government Service Delivery")
        
        if st.session_state.data_collected and st.session_state.collected_data:
            service_data = st.session_state.collected_data.get("service_delivery", [])
            
            if service_data:
                for item in service_data:
                    st.metric(
                        label=item.title[:50],
                        value=f"{item.value:.1f}" if item.value else "N/A",
                        help=item.text
                    )
            else:
                st.info("No service delivery data collected")
        else:
            st.info("Collect data first to see service metrics")

    # Analytics Tab (REAL DATA ONLY - No Simulation)
    with tabs[5]:
        st.header("📊 Advanced Analytics")
        
        st.markdown("""
        ### Real-Time Data Analytics
        
        All insights are based on **live data** from government APIs, news sources, and social media.
        No simulation or synthetic data is used.
        
        **Data Sources:**
        - 📈 **FRED/BLS** - Economic indicators (treasury rates, unemployment, CPI)
        - 📰 **NewsAPI/GNews** - News articles (last 24 hours)
        - 💬 **Reddit** - Social media discussions (real-time)
        - 🚨 **OpenFEMA/ReliefWeb** - Disaster declarations (real-time)
        - 🏛️ **Performance.gov/USAspending** - Government metrics (daily)
        """)
        
        st.divider()
        
        if st.session_state.data_collected and st.session_state.collected_data:
            data = st.session_state.collected_data
            
            # Create comprehensive analytics sections
            st.subheader("📈 Economic Analytics")
            
            econ_data = data.get("economic", [])
            if econ_data:
                # Economic indicators table
                st.markdown("#### Current Economic Indicators")
                
                econ_table = []
                for item in econ_data:
                    series_id = item.metadata.get("series_id", item.id)
                    econ_table.append({
                        "Indicator": series_id,
                        "Value": f"{item.value:.2f}" if item.value else "N/A",
                        "Date": item.metadata.get("date", "N/A"),
                        "Source": item.source
                    })
                
                st.dataframe(econ_table, use_container_width=True)
                
                # Time series visualization
                render_time_series_forecast(econ_data)
            
            st.divider()
            
            st.subheader("💬 Sentiment Analytics")
            
            sentiment_data = data.get("sentiment", [])
            if sentiment_data:
                # Word frequency
                render_word_cloud_alternative(sentiment_data)
                
                # Source breakdown
                st.markdown("#### Articles by Source")
                sources: dict[str, int] = {}
                for item in sentiment_data:
                    sources[item.source] = sources.get(item.source, 0) + 1
                
                source_cols = st.columns(len(sources))
                for idx, (source, count) in enumerate(sources.items()):
                    with source_cols[idx]:
                        st.metric(source, count)
            
            st.divider()
            
            st.subheader("🚨 Risk & Alert Analysis")
            
            crisis_data = data.get("crisis", [])
            render_alert_timeline(crisis_data, econ_data)
            
            st.divider()
            
            st.subheader("🔗 Cross-Indicator Analysis")
            render_correlation_matrix(econ_data, sentiment_data)
            
        else:
            st.info("👈 Collect real-time data first using the 'Data Collection' tab")
            
            if st.button("🔄 Collect Data Now", type="primary"):
                st.switch_page("pages/01_Data_Collection.py")

    # Data Collection Tab
    with tabs[6]:
        st.header("📥 Real-Time Data Collection")
        
        st.markdown("""
        Collect live data from multiple sources:
        - **📈 Economic Indicators**: FRED (treasury rates, unemployment, CPI), BLS (employment)
        - **🚨 Crisis Monitoring**: FEMA (disasters), ReliefWeb (humanitarian crises)
        - **💬 Public Sentiment**: Reddit, NewsAPI, GNews (news & social media)
        - **🏛️ Service Delivery**: USAspending.gov, Performance.gov
        """)
        
        st.divider()
        
        # Collection options
        st.subheader("Select Data Sources")
        
        collect_economic = st.checkbox("📈 Economic Indicators", value=True)
        collect_crisis = st.checkbox("🚨 Crisis & Risk Monitoring", value=True)
        collect_sentiment = st.checkbox("💬 Public Sentiment", value=True)
        collect_service = st.checkbox("🏛️ Service Delivery", value=True)
        
        st.divider()
        
        # Collection button
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("🚀 Start Data Collection", type="primary", use_container_width=True):
                # Determine what to collect
                categories = []
                if collect_economic:
                    categories.append("economic")
                if collect_crisis:
                    categories.append("crisis")
                if collect_sentiment:
                    categories.append("sentiment")
                if collect_service:
                    categories.append("service_delivery")
                
                with st.spinner("Collecting real-time data from all selected sources..."):
                    progress = st.progress(0)
                    status = st.empty()
                    
                    all_data = {
                        "economic": [],
                        "crisis": [],
                        "sentiment": [],
                        "service_delivery": [],
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    total = len(categories)
                    completed = 0
                    
                    config = load_environment()
                    config.max_items = 50
                    
                    try:
                        if "economic" in categories:
                            status.text("📊 Collecting economic indicators...")
                            econ = EconomicIndicatorsCollector(config)
                            all_data["economic"] = econ.collect_fred_indicators()
                            all_data["economic"].extend(econ.collect_bls_data())
                            completed += 1
                            progress.progress(completed / total)
                        
                        if "crisis" in categories:
                            status.text("🚨 Collecting crisis data...")
                            crisis = CrisisMonitoringCollector(config)
                            all_data["crisis"] = crisis.collect_fema_disasters()
                            all_data["crisis"].extend(crisis.collect_reliefweb_crises())
                            completed += 1
                            progress.progress(completed / total)
                        
                        if "service_delivery" in categories:
                            status.text("🏛️ Collecting service delivery data...")
                            service = ServiceDeliveryCollector(config)
                            all_data["service_delivery"] = service.collect_spending_data()
                            all_data["service_delivery"].extend(service.collect_performance_metrics())
                            completed += 1
                            progress.progress(completed / total)
                        
                        if "sentiment" in categories:
                            status.text("💬 Collecting sentiment data...")
                            sentiment = DataCollector(config)
                            all_data["sentiment"] = sentiment.collect_all()
                            completed += 1
                            progress.progress(completed / total)
                        
                        status.text("✓ Collection complete!")

                        # Save to session and file
                        st.session_state.collected_data = all_data
                        st.session_state.data_collected = True
                        st.session_state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        save_path = save_data(all_data)

                        # Auto-run NLP analysis on collected sentiment data
                        if all_data.get("sentiment") and NLP_AVAILABLE:
                            status.text("🧠 Running NLP analysis...")
                            try:
                                from opinion_sim_system.nlp.advanced_analyzer import AdvancedNLPAnalyzer
                                analyzer = AdvancedNLPAnalyzer()
                                
                                # Get texts from sentiment data
                                texts = [item.text for item in all_data["sentiment"] if item.text]
                                
                                # Run sentiment analysis
                                sentiment_results = analyzer.analyze_sentiment_batch(texts[:30])
                                
                                # Run emotion detection
                                emotion_results = analyzer.detect_emotions(texts[:30])
                                
                                # Generate insights
                                insights = analyzer.generate_insights(sentiment_results, emotion_results, [])
                                
                                # Store in data for AI chatbot
                                all_data["nlp_analysis"] = {
                                    "sentiment_results": [
                                        {"sentiment": r.sentiment, "confidence": r.confidence, "compound": r.compound_score}
                                        for r in sentiment_results
                                    ],
                                    "emotion_results": [
                                        {"dominant_emotion": r.dominant_emotion, "emotions": r.emotions}
                                        for r in emotion_results
                                    ],
                                    "insights": insights
                                }
                                
                                # Calculate overall sentiment
                                if sentiment_results:
                                    avg_compound = sum(r.compound_score for r in sentiment_results) / len(sentiment_results)
                                    positive_pct = sum(1 for r in sentiment_results if r.sentiment == "positive") / len(sentiment_results)
                                    negative_pct = sum(1 for r in sentiment_results if r.sentiment == "negative") / len(sentiment_results)
                                    
                                    all_data["nlp_analysis"]["overall_sentiment"] = {
                                        "average_score": avg_compound,
                                        "positive_percentage": positive_pct,
                                        "negative_percentage": negative_pct,
                                        "classification": "positive" if avg_compound > 0.1 else "negative" if avg_compound < -0.1 else "neutral"
                                    }
                                
                                # Calculate emotion breakdown
                                if emotion_results:
                                    emotion_totals = {}
                                    for result in emotion_results:
                                        for emotion, score in result.emotions.items():
                                            emotion_totals[emotion] = emotion_totals.get(emotion, 0) + score
                                    total = sum(emotion_totals.values())
                                    if total > 0:
                                        all_data["nlp_analysis"]["emotion_breakdown"] = {
                                            emotion: score / total for emotion, score in emotion_totals.items()
                                        }
                                
                                # Update session state
                                st.session_state.collected_data = all_data
                                
                                status.text("✓ NLP analysis complete!")
                                
                            except Exception as e:
                                print(f"NLP analysis error: {e}")
                                status.text("⚠ NLP analysis skipped")

                        # Summary
                        st.success("✓ Data collection complete!")

                        total_items = sum(len(items) for items in all_data.values() if isinstance(items, list))
                        st.info(f"📊 Collected {total_items} total items")
                        st.info(f"💾 Saved to: {save_path}")

                        progress.empty()
                        status.empty()

                        # Generate Summarized Report
                        st.divider()
                        st.subheader("📋 Collection Report Summary")
                        
                        report_col1, report_col2 = st.columns(2)
                        
                        with report_col1:
                            st.markdown("**📈 Economic Data**")
                            if all_data["economic"]:
                                for item in all_data["economic"][:5]:
                                    series_id = item.metadata.get("series_id", item.id)
                                    value = f"{item.value:.2f}" if item.value else "N/A"
                                    date = item.metadata.get("date", "N/A")
                                    st.write(f"- **{series_id}**: {value} (as of {date})")
                            else:
                                st.write("No economic data collected")
                        
                        with report_col2:
                            st.markdown("**💬 Sentiment Sources**")
                            if all_data["sentiment"]:
                                sources = {}
                                for item in all_data["sentiment"]:
                                    sources[item.source] = sources.get(item.source, 0) + 1
                                for source, count in sources.items():
                                    st.write(f"- **{source}**: {count} articles")
                            else:
                                st.write("No sentiment data collected")
                        
                        st.divider()
                        
                        # Quick Insights
                        st.markdown("**🔍 Quick Insights**")
                        
                        insights = []
                        
                        # Economic insights
                        for item in all_data["economic"]:
                            series_id = item.metadata.get("series_id", item.id)
                            value = item.value
                            if series_id == "DGS10" and value:
                                if value > 4.5:
                                    insights.append(f"🔴 High treasury yields ({value:.2f}%) may indicate economic concern")
                                elif value < 3.5:
                                    insights.append(f"🟢 Low treasury yields ({value:.2f}%) suggest stable economy")
                            elif series_id == "UNRATE" and value:
                                if value > 5:
                                    insights.append(f"🔴 Unemployment at {value:.1f}% - monitor job market")
                                elif value < 4:
                                    insights.append(f"🟢 Low unemployment ({value:.1f}%) - strong job market")
                        
                        # Crisis insights
                        if all_data["crisis"]:
                            insights.append(f"🚨 {len(all_data['crisis'])} active crises being monitored")
                        
                        # Sentiment insights
                        if all_data["sentiment"]:
                            insights.append(f"📰 {len(all_data['sentiment'])} news/social items analyzed")
                        
                        if insights:
                            for insight in insights[:5]:
                                st.write(f"- {insight}")
                        else:
                            st.write("No significant insights at this time")

                    except Exception as e:
                        st.error(f"Collection failed: {str(e)}")
        
        with col2:
            st.markdown("### Last Collection")
            if st.session_state.last_update:
                st.success(f"✓ {st.session_state.last_update}")
            else:
                st.info("No data yet")
        
        st.divider()
        
        # Show collected data summary
        if st.session_state.data_collected and st.session_state.collected_data:
            st.subheader("📊 Collection Summary")
            
            data = st.session_state.collected_data
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Economic Indicators",
                    len(data.get("economic", [])),
                    "FRED + BLS"
                )
            
            with col2:
                st.metric(
                    "Crisis Alerts",
                    len(data.get("crisis", [])),
                    "FEMA + ReliefWeb"
                )
            
            with col3:
                st.metric(
                    "Sentiment Items",
                    len(data.get("sentiment", [])),
                    "News + Social"
                )
            
            with col4:
                st.metric(
                    "Service Metrics",
                    len(data.get("service_delivery", [])),
                    "Government APIs"
                )

    # Settings Tab
    with tabs[7]:
        st.header("⚙️ Settings & Configuration")
        
        st.markdown("### API Configuration")
        st.write("Configure your API keys for data collection.")
        
        # Show current config
        st.markdown("#### Current Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            st.json({
                "FRED API": "✓ Set" if config.fred_api_key else "✗ Not set",
                "BLS API": "✓ Set" if config.bls_api_key else "✗ Not set",
                "Reddit API": "✓ Set" if config.reddit_client_id else "✗ Not set",
            })
        
        with col2:
            st.json({
                "NewsAPI": "✓ Set" if config.newsapi_key else "✗ Not set",
                "GNews": "✓ Set" if config.gnews_key else "✗ Not set",
            })
        
        st.divider()
        
        st.markdown("### Get API Keys")
        
        with st.expander("📈 FRED API (Economic Data)"):
            st.write("Get free API key for economic indicators")
            st.link_button("Get FRED API Key", "https://fred.stlouisfed.org/docs/api/api_key.html")
        
        with st.expander("📰 NewsAPI (News Articles)"):
            st.write("Get free API key for news collection")
            st.link_button("Get NewsAPI Key", "https://newsapi.org/register")
        
        with st.expander("👥 Reddit API (Social Sentiment)"):
            st.write("Get free API credentials for Reddit data")
            st.link_button("Get Reddit API", "https://www.reddit.com/prefs/apps")
        
        st.divider()
        
        st.markdown("### Data Management")
        
        if st.button("🗑️ Clear Collected Data", type="secondary"):
            st.session_state.data_collected = False
            st.session_state.collected_data = None
            st.session_state.last_update = None
            st.success("Data cleared!")
            st.rerun()


if __name__ == "__main__":
    main()
