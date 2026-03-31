"""
Real Data Pipeline - Process real-world data for PM Dashboard

This script:
1. Collects real data from free APIs (Reddit, NewsAPI, GNews, Public datasets)
2. Analyzes sentiment using the existing sentiment model
3. Creates simulation-compatible output
4. Generates PM dashboard and briefing report

Usage:
    python -m opinion_sim_system.data_collection.run_pipeline
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..data_collection.collector import (
    CollectorConfig,
    DataCollector,
    DataItem,
    collect_data,
)
from ..models.sentiment.sentiment_model import SentimentModel
from ..models.topic.topic_model import TopicModel
from ..models.embedding.embedder import Embedder
from ..archetypes.profiles import derive_initial_attitudes
from ..simulation.runner import RunnerConfig, run_phase1_simulation


def analyze_real_data(items: list[DataItem]) -> dict[str, Any]:
    """
    Analyze collected real data and create simulation-compatible output.
    
    Args:
        items: List of collected DataItem objects
    
    Returns:
        Dictionary compatible with PM dashboard
    """
    if not items:
        raise ValueError("No data items to analyze")
    
    print(f"\n📊 Analyzing {len(items)} real data items...")
    
    # Initialize models
    sentiment_model = SentimentModel()
    topic_model = TopicModel()
    embedder = Embedder()
    
    # Extract texts
    texts = [item.text for item in items]
    
    # Sentiment analysis
    print("  → Running sentiment analysis...")
    sentiment_results = sentiment_model.analyze(texts)
    sentiment_scores = [item.score for item in sentiment_results]
    
    # Calculate overall sentiment signal
    overall_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    
    # Topic modeling
    print("  → Extracting topics...")
    topics, topic_words = topic_model.fit_transform(texts)
    
    # Create topic distribution
    topic_ids = [item.topic_id for item in topics]
    topic_counts: dict[int, int] = {}
    for tid in topic_ids:
        topic_counts[tid] = topic_counts.get(tid, 0) + 1
    
    topic_distribution = {
        f"topic_{tid}": count / len(topic_ids) if topic_ids else 0
        for tid, count in topic_counts.items()
    }
    
    # Derive initial attitudes from sentiment
    print("  → Computing population segment attitudes...")
    initial_attitudes = derive_initial_attitudes(overall_sentiment)
    
    # Simulate evolution (3 rounds)
    print("  → Running opinion evolution simulation...")
    result = run_phase1_simulation(
        product_description="Government policies and public services",
        comments=texts[:50],  # Use subset for simulation
        config=RunnerConfig(rounds=3),
    )
    
    # Enhance with real data metadata
    result["data_source"] = "real_world_data"
    result["collection_info"] = {
        "total_items": len(items),
        "sources": list(set(item.source for item in items)),
        "date_range": {
            "from": min(item.timestamp for item in items).isoformat(),
            "to": max(item.timestamp for item in items).isoformat(),
        }
    }
    
    # Add sample items (anonymized)
    result["sample_data"] = [
        {
            "source": item.source,
            "title": item.title[:100] if item.title else "",
            "timestamp": item.timestamp.isoformat(),
        }
        for item in items[:10]
    ]
    
    print(f"✓ Analysis complete!")
    print(f"  Overall sentiment: {overall_sentiment:.3f}")
    print(f"  Topics identified: {len(topic_counts)}")
    print(f"  Population segments: {len(initial_attitudes)}")
    
    return result


def run_pipeline(
    keywords: list[str] | None = None,
    max_items: int = 100,
    output_dir: str | Path | None = None,
    use_cached: bool = True,
) -> dict[str, Any]:
    """
    Run the complete real data pipeline.
    
    Args:
        keywords: Keywords to search for
        max_items: Maximum items to collect
        output_dir: Directory to save outputs
        use_cached: Use cached data if available
    
    Returns:
        Analysis result dictionary
    """
    output_path = Path(output_dir) if output_dir else Path(__file__).parent.parent / "artifacts" / "phase1"
    output_path.mkdir(parents=True, exist_ok=True)
    
    cache_file = output_path / "collected_data.json"
    result_file = output_path / "real_data_analysis.json"
    
    # Try to load cached data
    items: list[DataItem] = []
    if use_cached and cache_file.exists():
        print(f"📁 Loading cached data from {cache_file}")
        collector = DataCollector()
        items = collector.load_from_json(cache_file)
    
    # Collect fresh data if needed
    if not items:
        print("📡 Collecting real-world data...")
        config = CollectorConfig.from_env()
        if keywords:
            config.keywords = keywords
        config.max_items = max_items
        
        collector = DataCollector(config)
        items = collector.collect_all()
        
        # Cache the data
        if items:
            collector.save_to_json(items, cache_file)
    
    if not items:
        print("⚠ No data collected. Check API configurations.")
        # Use sample data as fallback
        from .collector import PublicDatasetsCollector
        fallback_collector = PublicDatasetsCollector(CollectorConfig())
        items = fallback_collector.collect()
    
    # Analyze the data
    result = analyze_real_data(items)
    
    # Save result
    result_file.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"\n💾 Results saved to: {result_file}")
    
    # Generate dashboard
    print("\n📊 Generating PM Dashboard...")
    from ..visualization.pm_dashboard import create_full_dashboard
    
    # Convert result to dashboard-compatible format
    dashboard_data = result.copy()
    
    dashboard_path = output_path / "pm_dashboard_real.html"
    create_full_dashboard(result_file, dashboard_path)
    print(f"✓ Dashboard saved to: {dashboard_path}")
    
    # Generate briefing report
    print("\n📋 Generating Briefing Report...")
    from ..visualization.briefing_report import save_html_report
    
    report_path = save_html_report(
        result_file,
        output_path / "pm_briefing_real.html",
        title="Real-Time Public Opinion Briefing",
    )
    print(f"✓ Briefing Report saved to: {report_path}")
    
    return result


if __name__ == "__main__":
    print("=" * 70)
    print("PM Dashboard - Real Data Pipeline")
    print("=" * 70)
    
    # Default keywords for government/public opinion monitoring
    default_keywords = [
        "government policy",
        "public service",
        "national news",
        "economy",
        "healthcare",
        "education",
        "infrastructure",
    ]
    
    result = run_pipeline(
        keywords=default_keywords,
        max_items=100,
        use_cached=True,
    )
    
    print("\n" + "=" * 70)
    print("✓ Pipeline Complete!")
    print("=" * 70)
    print(f"""
Generated Artifacts:
  📊 PM Dashboard:     artifacts/phase1/pm_dashboard_real.html
  📋 Briefing Report:  artifacts/phase1/pm_briefing_real.html
  💾 Analysis Data:    artifacts/phase1/real_data_analysis.json
  💾 Raw Data Cache:   artifacts/phase1/collected_data.json

Next Steps:
  1. Open pm_dashboard_real.html in your browser
  2. Print pm_briefing_real.html as PDF for distribution
  3. To collect fresh data: delete collected_data.json and re-run
    """)
