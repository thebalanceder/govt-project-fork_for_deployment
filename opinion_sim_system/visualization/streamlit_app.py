"""
Streamlit Executive Dashboard for Prime Minister
Interactive decision support system for public opinion analysis

Run with: streamlit run opinion_sim_system/visualization/streamlit_app.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import streamlit as st

# Handle both module and script execution
if __name__ == "__main__":
    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from visualization.pm_dashboard import (
        _load_simulation_result,
        create_sentiment_gauge,
        create_archetype_breakdown,
        create_evolution_chart,
        create_topic_chart,
        generate_risk_alerts,
        create_alerts_panel,
        ARCHETYPE_LABELS,
    )
else:
    from .pm_dashboard import (
        _load_simulation_result,
        create_sentiment_gauge,
        create_archetype_breakdown,
        create_evolution_chart,
        create_topic_chart,
        generate_risk_alerts,
        create_alerts_panel,
        ARCHETYPE_LABELS,
    )


# Page configuration
st.set_page_config(
    page_title="PM Executive Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for executive look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1a1a2e;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #0066cc;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .alert-high {
        background-color: #ffe6e6;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .alert-medium {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .alert-low {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .stAlert {
        max-width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def format_percentage(value: float) -> str:
    """Format value as percentage."""
    return f"{value:.1%}"


def format_score(value: float) -> str:
    """Format attitude score with color indicator."""
    if value < 0.4:
        return f"🔴 {value:.2f}"
    elif value < 0.6:
        return f"🟡 {value:.2f}"
    else:
        return f"🟢 {value:.2f}"


def get_default_json_path() -> Path:
    """Get default simulation output path."""
    return Path(__file__).parent.parent / "artifacts" / "phase1" / "milestone_m1_output.json"


def sidebar_config() -> Path:
    """Render sidebar configuration and return JSON path."""
    st.sidebar.header("⚙️ Configuration")
    
    # File selection
    json_path = st.sidebar.text_input(
        "Simulation Output JSON",
        value=str(get_default_json_path()),
        help="Path to simulation output JSON file"
    )
    
    st.sidebar.markdown("---")
    
    # Quick actions
    st.sidebar.header("🚀 Quick Actions")
    
    if st.sidebar.button("📊 Run New Simulation", use_container_width=True):
        from ..simulation.runner import run_phase1_simulation
        with st.spinner("Running simulation..."):
            result = run_phase1_simulation(
                product_description="A smart home product emphasizing battery life, simple setup, and reliable daily use."
            )
            st.sidebar.success(f"Output saved to: {result.get('artifact_path', 'unknown')}")
            json_path = result.get('artifact_path', str(get_default_json_path()))
    
    if st.sidebar.button("🔄 Refresh Dashboard", use_container_width=True):
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Info
    st.sidebar.header("ℹ️ About")
    st.sidebar.info(
        """
        **Executive Decision Dashboard**
        
        This dashboard provides real-time analysis of public opinion 
        simulation results for policy decision support.
        
        **Data Sources:**
        - Opinion simulation engine
        - Sentiment analysis
        - Topic modeling
        - Population archetype segmentation
        
        **Last Updated:** {date}
        """.format(date=Path(json_path).stat().st_mtime if Path(json_path).exists() else "N/A")
    )
    
    return Path(json_path)


def render_key_metrics(data: dict[str, Any]) -> None:
    """Render key metrics row."""
    trajectories = data.get("trajectories", [])
    latest = trajectories[-1] if trajectories else {}
    initial = data.get("initial_attitudes", {})
    
    overall = latest.get("overall_satisfaction", 0)
    
    # Calculate changes
    if initial:
        initial_avg = sum(initial.values()) / len(initial)
        change = overall - initial_avg
    else:
        change = 0
    
    # Trend
    if len(trajectories) >= 2:
        prev = trajectories[-2].get("overall_satisfaction", overall)
        trend = overall - prev
    else:
        trend = 0
    
    # Render metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📈 National Sentiment Index",
            value=f"{overall:.2f}",
            delta=f"{change:+.2f} from start",
            delta_color="normal" if overall > 0.6 else "inverse"
        )
    
    with col2:
        st.metric(
            label="👥 Population Segments",
            value=len(initial) if initial else "N/A",
            delta="6 archetypes",
            delta_color="off"
        )
    
    with col3:
        st.metric(
            label="📊 Simulation Rounds",
            value=len(trajectories),
            delta=f"{trend:+.2f} from last round",
            delta_color="normal" if trend >= 0 else "inverse"
        )
    
    with col4:
        alerts = generate_risk_alerts(data)
        high_alerts = sum(1 for a in alerts if a["severity"] == "HIGH")
        st.metric(
            label="⚠️ Risk Alerts",
            value=len(alerts),
            delta=f"{high_alerts} critical" if high_alerts > 0 else "All clear",
            delta_color="inverse" if high_alerts > 0 else "normal"
        )


def render_alerts_section(data: dict[str, Any]) -> None:
    """Render alerts section."""
    alerts = generate_risk_alerts(data)
    
    if not alerts:
        st.success("✅ **No Critical Alerts** - All indicators within normal range")
        return
    
    st.subheader("⚠️ Risk Alerts")
    
    for alert in alerts:
        severity = alert["severity"]
        category = alert["category"]
        message = alert["message"]
        recommendation = alert["recommendation"]
        
        if severity == "HIGH":
            st.error(f"**[{severity}] {category}**\n\n{message}\n\n💡 *{recommendation}*")
        elif severity == "MEDIUM":
            st.warning(f"**[{severity}] {category}**\n\n{message}\n\n💡 *{recommendation}*")
        else:
            st.info(f"**[{severity}] {category}**\n\n{message}\n\n💡 *{recommendation}*")


def render_archetype_analysis(data: dict[str, Any]) -> None:
    """Render archetype segment analysis."""
    st.subheader("👥 Population Segment Analysis")
    
    trajectories = data.get("trajectories", [])
    latest = trajectories[-1] if trajectories else {}
    group_attitudes = latest.get("group_attitudes", {})
    initial = data.get("initial_attitudes", {})
    
    if not group_attitudes:
        st.warning("No segment data available")
        return
    
    # Create cards for each segment
    cols = st.columns(3)
    
    for idx, (group, attitude) in enumerate(sorted(group_attitudes.items(), key=lambda x: x[1])):
        col = cols[idx % 3]
        
        initial_val = initial.get(group, attitude)
        change = attitude - initial_val
        
        label = ARCHETYPE_LABELS.get(group, group.title())
        
        with col:
            if attitude < 0.4:
                st.error(f"**{label}**\n\nAttitude: {attitude:.2f}\n\nChange: {change:+.2f}")
            elif attitude < 0.6:
                st.warning(f"**{label}**\n\nAttitude: {attitude:.2f}\n\nChange: {change:+.2f}")
            else:
                st.success(f"**{label}**\n\nAttitude: {attitude:.2f}\n\nChange: {change:+.2f}")


def render_topic_analysis(data: dict[str, Any]) -> None:
    """Render topic analysis section."""
    st.subheader("🏷️ Key Discussion Topics")
    
    semantic = data.get("semantic_summary", {})
    topic_dist = semantic.get("topic_distribution", {})
    topic_words = semantic.get("topic_words", {})
    
    if not topic_dist:
        st.info("No topic data available")
        return
    
    # Sort topics by proportion
    sorted_topics = sorted(topic_dist.items(), key=lambda x: x[1], reverse=True)
    
    for topic, proportion in sorted_topics:
        words = topic_words.get(topic, [])
        
        with st.expander(f"**{topic}** - {proportion:.1%} of discussion"):
            if words:
                st.write(f"**Keywords:** {', '.join(words[:10])}")
            else:
                st.write("No keywords available")


def render_policy_recommendations(data: dict[str, Any]) -> None:
    """Render policy recommendations based on analysis."""
    st.subheader("💡 Policy Recommendations")
    
    alerts = generate_risk_alerts(data)
    trajectories = data.get("trajectories", [])
    latest = trajectories[-1] if trajectories else {}
    overall = latest.get("overall_satisfaction", 0)
    
    recommendations = []
    
    # Generate recommendations based on data
    if overall < 0.4:
        recommendations.append({
            "priority": "🔴 URGENT",
            "action": "Launch National Communication Campaign",
            "rationale": f"National sentiment critically low ({overall:.2f})",
            "timeline": "Immediate (24-48 hours)"
        })
    elif overall < 0.6:
        recommendations.append({
            "priority": "🟡 HIGH",
            "action": "Enhance Public Engagement Initiatives",
            "rationale": f"Sentiment below optimal threshold ({overall:.2f})",
            "timeline": "This week"
        })
    
    # Segment-specific recommendations
    group_attitudes = latest.get("group_attitudes", {})
    for group, attitude in group_attitudes.items():
        if attitude < 0.4:
            recommendations.append({
                "priority": "🔴 URGENT",
                "action": f"Targeted Outreach to {ARCHETYPE_LABELS.get(group, group)}",
                "rationale": f"Segment showing strong negative attitude ({attitude:.2f})",
                "timeline": "Immediate"
            })
    
    # Trend-based recommendations
    if len(trajectories) >= 2:
        prev = trajectories[-2].get("overall_satisfaction", overall)
        if overall < prev - 0.1:
            recommendations.append({
                "priority": "🟡 HIGH",
                "action": "Investigate Emerging Issues",
                "rationale": f"Declining trend detected (-{prev - overall:.2f})",
                "timeline": "This week"
            })
        elif overall > prev + 0.1:
            recommendations.append({
                "priority": "🟢 POSITIVE",
                "action": "Document Success Factors",
                "rationale": f"Improving trend detected (+{overall - prev:.2f})",
                "timeline": "Ongoing"
            })
    
    if not recommendations:
        st.success("✅ Current policies showing positive results. Continue monitoring.")
        return
    
    # Display recommendations
    for rec in recommendations:
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{rec['priority']}** - {rec['action']}")
                st.write(f"*Rationale:* {rec['rationale']}")
            with col2:
                st.info(f"📅 {rec['timeline']}")
            st.divider()


def render_charts(data: dict[str, Any]) -> None:
    """Render interactive charts."""
    st.subheader("📊 Interactive Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Evolution Trends", "Segment Radar", "Topic Distribution"])
    
    trajectories = data.get("trajectories", [])
    latest = trajectories[-1] if trajectories else {}
    group_attitudes = latest.get("group_attitudes", {})
    semantic = data.get("semantic_summary", {})
    topic_dist = semantic.get("topic_distribution", {})
    topic_words = semantic.get("topic_words", {})
    
    with tab1:
        if trajectories:
            fig = create_evolution_chart(trajectories)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No evolution data available")
    
    with tab2:
        if group_attitudes:
            fig = create_archetype_breakdown(group_attitudes)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No segment data available")
    
    with tab3:
        if topic_dist:
            fig = create_topic_chart(topic_dist, topic_words)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No topic data available")


def render_raw_data(data: dict[str, Any]) -> None:
    """Render raw data explorer."""
    st.subheader("📁 Data Explorer")
    
    with st.expander("View Raw Simulation Data"):
        st.json(data)
    
    with st.expander("Export Options"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Download JSON"):
                st.download_button(
                    label="Confirm Download",
                    data=json.dumps(data, indent=2),
                    file_name="simulation_data.json",
                    mime="application/json"
                )
        
        with col2:
            st.info("PDF export coming soon")
        
        with col3:
            st.info("CSV export coming soon")


def main():
    """Main dashboard application."""
    # Header
    st.markdown('<h1 class="main-header">🏛️ Executive Decision Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### Public Opinion Simulation Analysis | Prime Minister's Office")
    st.markdown("---")
    
    # Sidebar
    json_path = sidebar_config()
    
    # Load data
    try:
        data = _load_simulation_result(json_path)
    except FileNotFoundError:
        st.error(f"❌ Simulation output not found at: {json_path}")
        st.info("💡 Run the simulation first: `python -m opinion_sim_system.simulation.runner`")
        return
    except json.JSONDecodeError:
        st.error(f"❌ Invalid JSON in: {json_path}")
        return
    
    # Key metrics
    render_key_metrics(data)
    
    st.markdown("---")
    
    # Main content - two columns
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        # Alerts section
        render_alerts_section(data)
        
        st.markdown("---")
        
        # Charts
        render_charts(data)
    
    with right_col:
        # Archetype analysis
        render_archetype_analysis(data)
        
        st.markdown("---")
        
        # Topic analysis
        render_topic_analysis(data)
    
    st.markdown("---")
    
    # Policy recommendations
    render_policy_recommendations(data)
    
    # Raw data
    render_raw_data(data)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <small>
                🏛️ Executive Decision Dashboard | Opinion Simulation System Phase 1<br>
                For official government use only | Data refreshes on simulation run
            </small>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
