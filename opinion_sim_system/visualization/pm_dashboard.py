"""
Executive Dashboard for Prime Minister - Opinion Simulation Visualization

Provides high-level decision support with:
- National sentiment gauge
- Population segment breakdown
- Opinion evolution trends
- Early warning alerts
- Key issue topics
- Policy impact scenarios
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


# Archetype group labels for PM consumption
ARCHETYPE_LABELS = {
    "efficiency": "Efficiency-Focused\n(Productivity)",
    "cost": "Cost-Conscious\n(Value Seekers)",
    "culture": "Culture-Oriented\n(Traditional Values)",
    "emotion": "Emotion-Driven\n(Experience Seekers)",
    "conformity": "Conformity-Minded\n(Social Harmony)",
    "risk": "Risk-Aware\n(Cautious Adopters)",
}

# Risk threshold colors
RISK_HIGH = 0.4
RISK_MEDIUM = 0.6


def _load_simulation_result(json_path: str | Path) -> dict[str, Any]:
    """Load simulation output JSON."""
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"Simulation output not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def create_sentiment_gauge(value: float, title: str = "National Sentiment Index") -> go.Figure:
    """
    Create a gauge chart showing overall sentiment.
    
    Args:
        value: Sentiment value (-1 to 1, normalized to 0-100 for display)
        title: Chart title
    
    Returns:
        Plotly figure object
    """
    if not PLOTLY_AVAILABLE:
        raise ImportError("plotly required. Install: pip install plotly")
    
    # Normalize to 0-100 scale
    normalized = (value + 1) / 2 * 100
    
    # Determine color based on sentiment
    if normalized < 40:
        color = "#dc3545"  # Red - concerning
        status = "Needs Attention"
    elif normalized < 60:
        color = "#ffc107"  # Yellow - moderate
        status = "Stable"
    else:
        color = "#28a745"  # Green - positive
        status = "Positive"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=normalized,
        domain={"x": [0, 1], "y": [0, 1]},
        title={
            "text": f"<b>{title}</b><br><span style='font-size:14px'>{status}</span>",
            "font": {"size": 16}
        },
        number={"font": {"size": 40, "color": color}},
        delta={"reference": 50, "increasing": {"color": "#28a745"}, "decreasing": {"color": "#dc3545"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "darkblue"},
            "bar": {"color": color},
            "bgcolor": "white",
            "borderwidth": 2,
            "bordercolor": "gray",
            "steps": [
                {"range": [0, 40], "color": "#ffe6e6"},
                {"range": [40, 60], "color": "#fff3cd"},
                {"range": [60, 100], "color": "#d4edda"}
            ],
        }
    ))
    
    fig.update_layout(
        height=300,
        margin={"l": 20, "r": 20, "t": 80, "b": 20},
        paper_bgcolor="white",
        font={"family": "Arial", "size": 12}
    )
    
    return fig


def create_archetype_breakdown(attitudes: dict[str, float]) -> go.Figure:
    """
    Create a radar chart showing attitudes across population segments.
    
    Args:
        attitudes: Dictionary mapping archetype names to attitude scores
    
    Returns:
        Plotly figure object
    """
    if not PLOTLY_AVAILABLE:
        raise ImportError("plotly required. Install: pip install plotly")
    
    categories = list(attitudes.keys())
    values = [attitudes[cat] for cat in categories]
    
    # Close the radar chart
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill="toself",
        name="Current Attitude",
        line={"color": "#0066cc", "width": 2},
        fillcolor="rgba(0, 102, 204, 0.3)"
    ))
    
    fig.update_layout(
        polar={
            "radialaxis": {
                "visible": True,
                "range": [-1, 1],
                "tickfont": {"size": 10}
            },
            "angularaxis": {
                "direction": "clockwise",
                "period": 6,
                "tickfont": {"size": 11}
            }
        },
        showlegend=True,
        height=400,
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
        title={"text": "<b>Population Segment Attitudes</b>", "x": 0.5}
    )
    
    return fig


def create_evolution_chart(trajectories: list[dict[str, Any]]) -> go.Figure:
    """
    Create a line chart showing opinion evolution over simulation rounds.
    
    Args:
        trajectories: List of trajectory data from simulation
    
    Returns:
        Plotly figure object
    """
    if not PLOTLY_AVAILABLE:
        raise ImportError("plotly required. Install: pip install plotly")
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Overall Satisfaction Trend", "Segment Evolution"),
        vertical_spacing=0.15,
        row_heights=[0.4, 0.6]
    )
    
    rounds = [t["round"] for t in trajectories]
    overall = [t["overall_satisfaction"] for t in trajectories]
    
    # Top: Overall trend
    fig.add_trace(
        go.Scatter(
            x=rounds, y=overall,
            mode="lines+markers",
            name="Overall",
            line={"color": "#0066cc", "width": 3},
            marker={"size": 8}
        ),
        row=1, col=1
    )
    
    # Bottom: Each archetype group
    colors = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33"]
    
    if trajectories and "group_attitudes" in trajectories[0]:
        groups = list(trajectories[0]["group_attitudes"].keys())
        
        for idx, group in enumerate(groups):
            group_values = [t["group_attitudes"].get(group, 0) for t in trajectories]
            fig.add_trace(
                go.Scatter(
                    x=rounds, y=group_values,
                    mode="lines+markers",
                    name=group.title(),
                    line={"color": colors[idx % len(colors)], "width": 2},
                    marker={"size": 6}
                ),
                row=2, col=1
            )
    
    fig.update_layout(
        height=500,
        showlegend=True,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "center", "x": 0.5},
        margin={"l": 50, "r": 20, "t": 60, "b": 40}
    )
    
    fig.update_xaxes(title_text="Simulation Round", row=2, col=1)
    fig.update_yaxes(title_text="Satisfaction Score", row=1, col=1)
    fig.update_yaxes(title_text="Attitude Score", row=2, col=1)
    
    return fig


def create_topic_chart(topic_distribution: dict[str, float], topic_words: dict[str, list[str]]) -> go.Figure:
    """
    Create a bar chart showing key topics driving opinion.
    
    Args:
        topic_distribution: Topic proportions
        topic_words: Key words per topic
    
    Returns:
        Plotly figure object
    """
    if not PLOTLY_AVAILABLE:
        raise ImportError("plotly required. Install: pip install plotly")
    
    topics = list(topic_distribution.keys())
    values = [topic_distribution[t] for t in topics]
    
    # Sort by value descending
    sorted_indices = sorted(range(len(values)), key=lambda i: values[i], reverse=True)
    topics_sorted = [topics[i] for i in sorted_indices]
    values_sorted = [values[i] for i in sorted_indices]
    
    # Add topic words as hover text
    hover_texts = []
    for topic in topics_sorted:
        words = topic_words.get(topic, [])
        hover_texts.append(f"Topic: {topic}<br>Proportion: {values_sorted[topics_sorted.index(topic)]:.1%}<br>Keywords: {', '.join(words[:5])}")
    
    fig = go.Figure(go.Bar(
        x=topics_sorted,
        y=values_sorted,
        hovertext=hover_texts,
        hoverinfo="text",
        marker={"color": "#0066cc", "line": {"color": "#004080", "width": 1}},
        text=[f"{v:.1%}" for v in values_sorted],
        textposition="outside"
    ))
    
    fig.update_layout(
        title={"text": "<b>Key Discussion Topics</b>", "x": 0.5},
        xaxis={"title": "Topic", "tickangle": -45},
        yaxis={"title": "Proportion of Discussion", "range": [0, max(values_sorted) * 1.2]},
        height=350,
        margin={"l": 40, "r": 20, "t": 50, "b": 80},
        showlegend=False
    )
    
    return fig


def generate_risk_alerts(data: dict[str, Any]) -> list[dict[str, str]]:
    """
    Generate risk alerts for PM attention.
    
    Args:
        data: Simulation result data
    
    Returns:
        List of alert dictionaries with severity, message, and recommendation
    """
    alerts = []
    
    trajectories = data.get("trajectories", [])
    if not trajectories:
        return alerts
    
    latest = trajectories[-1]
    overall = latest.get("overall_satisfaction", 0)
    group_attitudes = latest.get("group_attitudes", {})
    visualization_payload = data.get("visualization_payload", {})

    dispersion = 0.0
    if isinstance(visualization_payload, dict):
        divergence_summary = visualization_payload.get("divergence_summary", {})
        if isinstance(divergence_summary, dict):
            final_dispersion = divergence_summary.get("final_dispersion")
            if isinstance(final_dispersion, (int, float)):
                dispersion = float(final_dispersion)

    if dispersion == 0.0 and group_attitudes:
        values = [float(value) for value in group_attitudes.values()]
        dispersion = max(values) - min(values)
    
    # Check overall sentiment
    if overall < RISK_HIGH:
        alerts.append({
            "severity": "HIGH",
            "category": "National Sentiment",
            "message": f"Overall satisfaction critically low ({overall:.2f})",
            "recommendation": "Immediate intervention recommended. Consider public communication campaign."
        })
    elif overall < RISK_MEDIUM:
        alerts.append({
            "severity": "MEDIUM",
            "category": "National Sentiment",
            "message": f"Overall satisfaction below threshold ({overall:.2f})",
            "recommendation": "Monitor closely. Prepare contingency communication."
        })
    
    # Check for at-risk segments
    for group, attitude in group_attitudes.items():
        if attitude < RISK_HIGH:
            alerts.append({
                "severity": "HIGH",
                "category": "Population Segment",
                "message": f"{ARCHETYPE_LABELS.get(group, group)} showing strong negative attitude ({attitude:.2f})",
                "recommendation": f"Targeted outreach to {group}-focused communities needed."
            })

    # Check group divergence (polarization)
    if dispersion >= 0.35:
        alerts.append(
            {
                "severity": "HIGH",
                "category": "Group Divergence",
                "message": f"Segment divergence is high (dispersion={dispersion:.2f})",
                "recommendation": "Prioritize segment-specific messaging and conflict mitigation strategy.",
            }
        )
    elif dispersion >= 0.20:
        alerts.append(
            {
                "severity": "MEDIUM",
                "category": "Group Divergence",
                "message": f"Segment divergence is rising (dispersion={dispersion:.2f})",
                "recommendation": "Monitor segment gaps and reinforce shared value framing.",
            }
        )
    
    # Check trend direction
    if len(trajectories) >= 2:
        prev_overall = trajectories[-2].get("overall_satisfaction", 0)
        if overall < prev_overall - 0.1:
            alerts.append({
                "severity": "MEDIUM",
                "category": "Trend Alert",
                "message": f"Declining satisfaction trend detected (-{prev_overall - overall:.2f} from last round)",
                "recommendation": "Investigate emerging issues. Consider proactive policy adjustment."
            })
    
    # Sort by severity
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    alerts.sort(key=lambda x: severity_order.get(x["severity"], 3))
    
    return alerts


def create_alerts_panel(alerts: list[dict[str, str]]) -> go.Figure:
    """
    Create a visual alerts panel for the dashboard.

    Args:
        alerts: List of alert dictionaries

    Returns:
        Plotly figure object
    """
    if not PLOTLY_AVAILABLE:
        raise ImportError("plotly required. Install: pip install plotly")

    if not alerts:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[0], y=[0],
            mode="text",
            text="✓ No Critical Alerts<br><span style='font-size:12px'>All indicators within normal range</span>",
            textfont={"size": 16, "color": "#28a745"},
            showlegend=False
        ))
        fig.update_layout(
            height=200,
            xaxis={"visible": False, "range": [-1, 1]},
            yaxis={"visible": False, "range": [-1, 1]},
            margin={"l": 0, "r": 0, "t": 0, "b": 0}
        )
        return fig
    
    # Build alert table
    severity_colors = {"HIGH": "#dc3545", "MEDIUM": "#ffc107", "LOW": "#28a745"}
    
    y_positions = []
    texts = []
    colors = []
    
    for i, alert in enumerate(alerts[:5]):  # Show top 5 alerts
        y_positions.append(i * -0.15)
        severity = alert["severity"]
        category = alert["category"]
        message = alert["message"]
        texts.append(f"<b>{severity}</b> | {category}<br>{message}")
        colors.append(severity_colors.get(severity, "#666"))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=[0.1] * len(y_positions),
        y=y_positions,
        mode="markers",
        marker={"size": 15, "color": colors},
        hovertext=texts,
        hoverinfo="text",
        showlegend=False
    ))
    
    # Add legend
    for severity, color in severity_colors.items():
        count = sum(1 for a in alerts if a["severity"] == severity)
        if count > 0:
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode="markers",
                marker={"size": 10, "color": color},
                name=f"{severity}: {count} alert(s)",
                showlegend=True
            ))
    
    fig.update_layout(
        title={"text": "<b>Risk Alerts</b>", "x": 0.5},
        height=250,
        xaxis={"visible": False, "range": [-0.5, 1]},
        yaxis={"visible": False, "range": [-1, 0.1]},
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
        legend={"orientation": "h", "yanchor": "bottom", "y": -0.3, "xanchor": "center", "x": 0.5}
    )
    
    return fig


def create_full_dashboard(json_path: str | Path, output_path: str | Path | None = None) -> go.Figure:
    """
    Create a complete executive dashboard for the Prime Minister.
    
    Args:
        json_path: Path to simulation output JSON
        output_path: Optional path to save HTML dashboard
    
    Returns:
        Plotly figure object (can be shown or saved)
    """
    if not PLOTLY_AVAILABLE:
        raise ImportError("plotly required. Install: pip install plotly")
    
    data = _load_simulation_result(json_path)
    
    # Extract data
    trajectories = data.get("trajectories", [])
    latest = trajectories[-1] if trajectories else {}
    overall = latest.get("overall_satisfaction", 0)
    group_attitudes = latest.get("group_attitudes", {})
    topic_dist = latest.get("topic_distribution", {})
    topic_words = data.get("semantic_summary", {}).get("topic_words", {})
    
    # Generate alerts
    alerts = generate_risk_alerts(data)
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=3,
        specs=[
            [{"type": "indicator", "colspan": 1}, {"type": "scatterpolar", "colspan": 1}, {"type": "scatter", "colspan": 1}],
            [{"type": "scatter", "colspan": 2}, None, {"type": "bar", "colspan": 1}],
            [{"type": "scatter", "colspan": 3}, None, None]
        ],
        subplot_titles=(
            "National Sentiment",
            "Population Segments", 
            "Alerts",
            "Opinion Evolution",
            "Topic Distribution",
            "Segment Trends"
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
        row_heights=[0.35, 0.35, 0.3],
        column_widths=[0.33, 0.33, 0.34]
    )
    
    # Row 1: Gauge, Radar, Alerts
    gauge = create_sentiment_gauge(overall, "National Sentiment Index")
    fig.add_trace(gauge.data[0], row=1, col=1)
    
    radar = create_archetype_breakdown(group_attitudes)
    fig.add_trace(radar.data[0], row=1, col=2)
    
    alerts_fig = create_alerts_panel(alerts)
    fig.add_trace(alerts_fig.data[0], row=1, col=3)
    
    # Row 2: Evolution chart (spanning 2 cols), Topics
    evolution = create_evolution_chart(trajectories)
    for trace in evolution.data[:1]:  # Overall only for main chart
        fig.add_trace(trace, row=2, col=1)
    
    topic_chart = create_topic_chart(topic_dist, topic_words)
    fig.add_trace(topic_chart.data[0], row=2, col=3)
    
    # Row 3: Detailed segment evolution
    for trace in evolution.data[1:]:  # Segment traces
        fig.add_trace(trace, row=3, col=1)
    
    # Update layout
    fig.update_layout(
        height=900,
        showlegend=True,
        legend={"orientation": "h", "yanchor": "bottom", "y": -0.15, "xanchor": "center", "x": 0.5},
        margin={"l": 40, "r": 40, "t": 60, "b": 60},
        paper_bgcolor="white",
        plot_bgcolor="white",
        title={
            "text": "<b>EXECUTIVE DECISION DASHBOARD</b><br><span style='font-size:14px'>Public Opinion Simulation Analysis</span>",
            "x": 0.5,
            "font": {"size": 20}
        }
    )
    
    # Save if path provided
    if output_path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(output)
    
    return fig


def create_dashboard(json_path: str | Path | None = None, output_path: str | Path | None = None) -> str | None:
    """
    Convenience function to create and save dashboard.
    
    Args:
        json_path: Path to simulation JSON (uses default if None)
        output_path: Path to save HTML dashboard
    
    Returns:
        Path to saved dashboard or None
    """
    if json_path is None:
        json_path = Path(__file__).parent.parent / "artifacts" / "phase1" / "milestone_m1_output.json"
    
    if output_path is None:
        output_path = Path(__file__).parent.parent / "artifacts" / "phase1" / "pm_dashboard.html"
    
    create_full_dashboard(json_path, output_path)
    return str(output_path)


if __name__ == "__main__":
    # Default: create dashboard from latest simulation output
    try:
        dashboard_path = create_dashboard()
        print(f"✓ PM Dashboard created: {dashboard_path}")
        print("Open this file in a web browser to view the executive dashboard.")
    except ImportError as e:
        print(f"Visualization library not available: {e}")
        print("Install with: pip install plotly")
    except FileNotFoundError as e:
        print(f"Run simulation first: {e}")
        print("Execute: python -m opinion_sim_system.simulation.runner")
