"""
PM Briefing Report Generator

Generates executive summary reports in HTML format suitable for printing
or presentation to government leadership.

Features:
- One-page executive summary
- Key metrics and alerts
- Policy recommendations
- Professional government styling
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from .pm_dashboard import (
    _load_simulation_result,
    generate_risk_alerts,
    ARCHETYPE_LABELS,
)


def generate_html_report(
    data: dict[str, Any],
    title: str = "Public Opinion Simulation Briefing",
    classification: str = "OFFICIAL USE ONLY"
) -> str:
    """
    Generate an HTML briefing report.
    
    Args:
        data: Simulation result data
        title: Report title
        classification: Security classification banner
    
    Returns:
        HTML string
    """
    # Extract key data
    trajectories = data.get("trajectories", [])
    latest = trajectories[-1] if trajectories else {}
    initial = data.get("initial_attitudes", {})
    
    overall = latest.get("overall_satisfaction", 0)
    group_attitudes = latest.get("group_attitudes", {})
    semantic = data.get("semantic_summary", {})
    topic_dist = semantic.get("topic_distribution", {})
    topic_words = semantic.get("topic_words", {})
    
    alerts = generate_risk_alerts(data)
    high_alerts = sum(1 for a in alerts if a["severity"] == "HIGH")
    
    # Calculate trend
    if len(trajectories) >= 2:
        prev = trajectories[-2].get("overall_satisfaction", overall)
        trend = overall - prev
        trend_direction = "↑" if trend > 0 else "↓" if trend < 0 else "→"
        trend_class = "positive" if trend > 0 else "negative" if trend < 0 else "neutral"
    else:
        trend = 0
        trend_direction = "→"
        trend_class = "neutral"
    
    # Determine overall status
    if overall < 0.4:
        status_color = "#dc3545"
        status_text = "CRITICAL - Immediate Action Required"
        status_icon = "🔴"
    elif overall < 0.6:
        status_color = "#ffc107"
        status_text = "CAUTION - Monitoring Required"
        status_icon = "🟡"
    else:
        status_color = "#28a745"
        status_text = "STABLE - Continue Current Policies"
        status_icon = "🟢"
    
    # Generate segment rows
    segment_rows = ""
    for group, attitude in sorted(group_attitudes.items(), key=lambda x: x[1]):
        initial_val = initial.get(group, attitude)
        change = attitude - initial_val
        change_class = "positive" if change > 0 else "negative" if change < 0 else "neutral"
        change_icon = "↑" if change > 0 else "↓" if change < 0 else "→"
        
        label = ARCHETYPE_LABELS.get(group, group.title())
        
        if attitude < 0.4:
            row_color = "#ffe6e6"
        elif attitude < 0.6:
            row_color = "#fff3cd"
        else:
            row_color = "#d4edda"
        
        segment_rows += f"""
        <tr style="background-color: {row_color}">
            <td style="padding: 10px; border: 1px solid #ddd;">{label}</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center; font-weight: bold;">{attitude:.2f}</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;" class="{change_class}">{change_icon} {abs(change):.2f}</td>
        </tr>
        """
    
    # Generate alert rows
    alert_rows = ""
    if alerts:
        for alert in alerts[:5]:
            severity_color = {"HIGH": "#dc3545", "MEDIUM": "#ffc107", "LOW": "#28a745"}.get(alert["severity"], "#666")
            alert_rows += f"""
            <tr>
                <td style="padding: 8px; border-left: 4px solid {severity_color};">
                    <strong>[{alert["severity"]}]</strong> {alert["category"]}<br>
                    <small>{alert["message"]}</small>
                </td>
            </tr>
            """
    else:
        alert_rows = '<tr><td style="padding: 10px; color: #28a745;">✓ No critical alerts</td></tr>'
    
    # Generate topic rows
    topic_rows = ""
    sorted_topics = sorted(topic_dist.items(), key=lambda x: x[1], reverse=True)[:5]
    for topic, proportion in sorted_topics:
        words = topic_words.get(topic, [])
        topic_rows += f"""
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>{topic}</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{proportion:.1%}</td>
            <td style="padding: 8px; border: 1px solid #ddd;"><small>{', '.join(words[:5]) if words else 'N/A'}</small></td>
        </tr>
        """
    
    # Generate recommendations
    recommendations = []
    if overall < 0.4:
        recommendations.append(("🔴 URGENT", "Launch National Communication Campaign", "Immediate (24-48 hours)"))
    elif overall < 0.6:
        recommendations.append(("🟡 HIGH", "Enhance Public Engagement Initiatives", "This week"))
    
    for group, attitude in group_attitudes.items():
        if attitude < 0.4:
            recommendations.append(("🔴 URGENT", f"Targeted Outreach to {group.title()} Segments", "Immediate"))
    
    if trend < -0.1:
        recommendations.append(("🟡 HIGH", "Investigate Emerging Negative Issues", "This week"))
    elif trend > 0.1:
        recommendations.append(("🟢 POSITIVE", "Document and Scale Success Factors", "Ongoing"))
    
    if not recommendations:
        recommendations.append(("🟢 ON TRACK", "Continue Current Policy Approach", "Ongoing"))
    
    rec_rows = ""
    for priority, action, timeline in recommendations[:5]:
        rec_rows += f"""
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">{priority}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{action}</td>
            <td style="padding: 10px; border: 1px solid #ddd;"><small>{timeline}</small></td>
        </tr>
        """
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        @media print {{
            .no-print {{ display: none; }}
            body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #1a1a2e;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        
        .classification-banner {{
            background: #1a1a2e;
            color: white;
            text-align: center;
            padding: 8px;
            font-weight: bold;
            font-size: 14px;
            letter-spacing: 2px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .header p {{
            opacity: 0.9;
            font-size: 14px;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .executive-summary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 25px;
        }}
        
        .executive-summary h2 {{
            margin-bottom: 15px;
            font-size: 20px;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 15px;
        }}
        
        .summary-item {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .summary-item .value {{
            font-size: 32px;
            font-weight: bold;
        }}
        
        .summary-item .label {{
            font-size: 12px;
            opacity: 0.9;
            margin-top: 5px;
        }}
        
        .status-banner {{
            background: {status_color}22;
            border-left: 5px solid {status_color};
            padding: 20px;
            margin-bottom: 25px;
            border-radius: 5px;
        }}
        
        .status-banner h3 {{
            color: {status_color};
            margin-bottom: 10px;
        }}
        
        .section {{
            margin-bottom: 25px;
        }}
        
        .section h2 {{
            color: #1a1a2e;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 15px;
            font-size: 18px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }}
        
        th {{
            background: #1a1a2e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px;
            border: 1px solid #ddd;
        }}
        
        tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        .positive {{ color: #28a745; }}
        .negative {{ color: #dc3545; }}
        .neutral {{ color: #6c757d; }}
        
        .alert-box {{
            background: #fff;
            border-radius: 5px;
            overflow: hidden;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 12px;
            border-top: 2px solid #667eea;
        }}
        
        .print-button {{
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
        }}
        
        .print-button:hover {{
            background: #5a6fd6;
        }}
        
        .timestamp {{
            color: #666;
            font-size: 12px;
            text-align: right;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="classification-banner">{classification}</div>
        
        <div class="header">
            <h1>🏛️ {title}</h1>
            <p>Prime Minister's Office | Opinion Simulation System</p>
        </div>
        
        <div class="content">
            <div class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
            
            <div class="no-print" style="text-align: center; margin-bottom: 20px;">
                <button class="print-button" onclick="window.print()">🖨️ Print Report</button>
                <button class="print-button" onclick="window.location.reload()">🔄 Refresh Data</button>
            </div>
            
            <!-- Executive Summary -->
            <div class="executive-summary">
                <h2>📋 Executive Summary</h2>
                <div class="summary-grid">
                    <div class="summary-item">
                        <div class="value">{status_icon}</div>
                        <div class="label">Overall Status</div>
                    </div>
                    <div class="summary-item">
                        <div class="value">{overall:.2f}</div>
                        <div class="label">National Sentiment</div>
                    </div>
                    <div class="summary-item">
                        <div class="value">{trend_direction} {abs(trend):.2f}</div>
                        <div class="label">Trend (Last Round)</div>
                    </div>
                    <div class="summary-item">
                        <div class="value">{high_alerts}</div>
                        <div class="label">Critical Alerts</div>
                    </div>
                </div>
            </div>
            
            <!-- Status Banner -->
            <div class="status-banner">
                <h3>{status_icon} {status_text}</h3>
                <p>
                    Current national sentiment index stands at <strong>{overall:.2f}</strong> 
                    based on analysis of {data.get('input', {}).get('n_comments', 'N/A')} public comments.
                    Simulation ran for {len(trajectories)} rounds tracking {len(initial)} population segments.
                </p>
            </div>
            
            <!-- Population Segments -->
            <div class="section">
                <h2>👥 Population Segment Attitudes</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Segment</th>
                            <th>Current Attitude</th>
                            <th>Change</th>
                        </tr>
                    </thead>
                    <tbody>
                        {segment_rows}
                    </tbody>
                </table>
            </div>
            
            <!-- Risk Alerts -->
            <div class="section">
                <h2>⚠️ Risk Alerts</h2>
                <div class="alert-box">
                    <table>
                        <tbody>
                            {alert_rows}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Key Topics -->
            <div class="section">
                <h2>🏷️ Key Discussion Topics</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Topic</th>
                            <th>Proportion</th>
                            <th>Keywords</th>
                        </tr>
                    </thead>
                    <tbody>
                        {topic_rows}
                    </tbody>
                </table>
            </div>
            
            <!-- Policy Recommendations -->
            <div class="section">
                <h2>💡 Policy Recommendations</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Priority</th>
                            <th>Recommended Action</th>
                            <th>Timeline</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rec_rows}
                    </tbody>
                </table>
            </div>
            
            <!-- Technical Details -->
            <div class="section">
                <h2>📊 Simulation Details</h2>
                <table>
                    <tr>
                        <th style="width: 30%;">Input Source</th>
                        <td>{data.get('input', {}).get('product_description', 'N/A')[:100]}...</td>
                    </tr>
                    <tr>
                        <th>Comments Analyzed</th>
                        <td>{data.get('input', {}).get('n_comments', 'N/A')}</td>
                    </tr>
                    <tr>
                        <th>Simulation Rounds</th>
                        <td>{len(trajectories)}</td>
                    </tr>
                    <tr>
                        <th>Sentiment Signal</th>
                        <td>{semantic.get('sentiment_signal', 'N/A'):.3f}</td>
                    </tr>
                </table>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Classification:</strong> {classification}</p>
            <p>Opinion Simulation System Phase 1 | For Official Government Use Only</p>
            <p>This report is generated from simulation data and should be used in conjunction with other intelligence sources.</p>
        </div>
    </div>
</body>
</html>
    """.strip()
    
    return html


def save_html_report(
    json_path: str | Path | None = None,
    output_path: str | Path | None = None,
    title: str = "Public Opinion Simulation Briefing",
    classification: str = "OFFICIAL USE ONLY"
) -> str:
    """
    Generate and save an HTML briefing report.
    
    Args:
        json_path: Path to simulation JSON (uses default if None)
        output_path: Path to save HTML report
        title: Report title
        classification: Security classification banner
    
    Returns:
        Path to saved report
    """
    if json_path is None:
        json_path = Path(__file__).parent.parent / "artifacts" / "phase1" / "milestone_m1_output.json"
    
    if output_path is None:
        output_path = Path(__file__).parent.parent / "artifacts" / "phase1" / "pm_briefing_report.html"
    
    json_path = Path(json_path)
    output_path = Path(output_path)
    
    data = _load_simulation_result(json_path)
    html = generate_html_report(data, title, classification)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    
    return str(output_path)


def create_briefing(
    json_path: str | Path | None = None,
    output_path: str | Path | None = None
) -> str:
    """
    Convenience function to create PM briefing report.
    
    Args:
        json_path: Path to simulation JSON
        output_path: Path to save report
    
    Returns:
        Path to saved report
    """
    return save_html_report(
        json_path,
        output_path,
        title="Public Opinion Simulation Briefing",
        classification="OFFICIAL USE ONLY"
    )


if __name__ == "__main__":
    try:
        report_path = create_briefing()
        print(f"✓ PM Briefing Report created: {report_path}")
        print("Open this file in a web browser to view or print the report.")
    except FileNotFoundError as e:
        print(f"Run simulation first: {e}")
        print("Execute: python -m opinion_sim_system.simulation.runner")
