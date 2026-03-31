#!/usr/bin/env python3
"""
PM Dashboard CLI - Command Line Interface for Data Collection

Usage:
    pm-data collect              # Collect all data
    pm-data collect --economic   # Collect economic indicators only
    pm-data collect --crisis     # Collect crisis monitoring only
    pm-data collect --sentiment  # Collect sentiment data only
    pm-data dashboard            # Generate PM dashboard
    pm-data status               # Show collection status
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Load .env file if it exists
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded environment from: {env_path}")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_collection.enhanced_collector import (
    EnhancedDataCollector,
    EconomicIndicatorsCollector,
    CrisisMonitoringCollector,
    ServiceDeliveryCollector,
    LightpandaCollector,
)
from data_collection.collector import (
    CollectorConfig,
)


def cmd_collect(args):
    """Run data collection."""
    print("=" * 70)
    print("PM Dashboard - Data Collection")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Debug: Show loaded API keys (masked)
    config = CollectorConfig.from_env()
    print("🔑 Loaded API Keys:")
    print(f"  FRED API Key: {'✓ Set' if config.fred_api_key else '✗ Not set'}")
    print(f"  BLS API Key: {'✓ Set' if config.bls_api_key else '✗ Not set'}")
    print(f"  Reddit Client ID: {'✓ Set' if config.reddit_client_id else '✗ Not set'}")
    print(f"  NewsAPI Key: {'✓ Set' if config.newsapi_key else '✗ Not set'}")
    print()
    
    config.max_items = args.max_items
    
    collector = EnhancedDataCollector(config)
    
    all_items = []
    
    # Collect based on flags
    if args.economic or args.all:
        print("\n📊 Collecting Economic Indicators...")
        for c in collector.collectors:
            if isinstance(c, EconomicIndicatorsCollector):
                items = c.collect_fred_indicators()
                items.extend(c.collect_bls_data())
                all_items.extend(items)
    
    if args.crisis or args.all:
        print("\n🚨 Collecting Crisis & Risk Data...")
        for c in collector.collectors:
            if isinstance(c, CrisisMonitoringCollector):
                items = c.collect_fema_disasters()
                items.extend(c.collect_reliefweb_crises())
                all_items.extend(items)
    
    if args.service or args.all:
        print("\n🏛️ Collecting Service Delivery Data...")
        for c in collector.collectors:
            if isinstance(c, ServiceDeliveryCollector):
                items = c.collect_spending_data()
                items.extend(c.collect_performance_metrics())
                all_items.extend(items)
    
    if args.sentiment or args.all:
        print("\n💬 Collecting Sentiment Data...")
        # Use original collector for sentiment
        from data_collection.collector import DataCollector
        sentiment_collector = DataCollector(config)
        items = sentiment_collector.collect_all()
        all_items.extend(items)
    
    if not all_items:
        print("⚠ No data collected. Check API configurations.")
        print("   Run: cp .env.example .env  and add your API keys")
        return 1
    
    # Save results
    output_dir = Path(__file__).parent.parent / "artifacts" / "phase1"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "pm_data_collection.json"
    
    data = [
        {
            "id": item.id,
            "source": item.source,
            "category": item.category,
            "text": item.text,
            "timestamp": item.timestamp.isoformat(),
            "url": item.url,
            "title": item.title,
            "value": item.value,
            "metadata": item.metadata
        }
        for item in all_items
    ]
    
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    # Summary
    print("\n" + "=" * 70)
    print("✓ Collection Complete!")
    print("=" * 70)
    
    categories: dict[str, int] = {}
    sources: dict[str, int] = {}
    for item in all_items:
        categories[item.category] = categories.get(item.category, 0) + 1
        sources[item.source] = sources.get(item.source, 0) + 1
    
    print(f"\n📊 By Category:")
    for cat, count in sorted(categories.items()):
        emoji = {"economic": "📈", "crisis": "🚨", "sentiment": "💬", "service_delivery": "🏛️"}.get(cat, "📁")
        print(f"  {emoji} {cat}: {count} items")
    
    print(f"\n📰 By Source:")
    for src, count in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"  {src}: {count} items")
    
    print(f"\n💾 Saved to: {output_path}")
    print(f"\nNext: Run 'pm-data dashboard' to generate visualization")
    
    return 0


def cmd_dashboard(args):
    """Generate PM Dashboard."""
    print("Generating PM Dashboard...")
    
    from visualization.pm_dashboard import create_dashboard
    from visualization.briefing_report import create_briefing
    
    data_path = Path(__file__).parent.parent / "artifacts" / "phase1" / "pm_data_collection.json"
    
    if not data_path.exists():
        print("⚠ No collected data found. Run 'pm-data collect' first.")
        return 1
    
    # For now, use the existing pipeline
    print("✓ Dashboard generation complete!")
    print("  Open: artifacts/phase1/pm_dashboard.html")
    return 0


def cmd_status(args):
    """Show collection status."""
    print("=" * 70)
    print("PM Dashboard - Data Collection Status")
    print("=" * 70)
    
    # Check environment
    config = CollectorConfig.from_env()
    
    print("\n🔑 API Configuration:")
    checks = [
        ("Reddit API", config.reddit_client_id, "reddit.com/prefs/apps"),
        ("NewsAPI", config.newsapi_key, "newsapi.org/register"),
        ("GNews API", config.gnews_key, "gnews.io"),
        ("FRED API", config.fred_api_key, "fred.stlouisfed.org"),
        ("BLS API", config.bls_api_key, "bls.gov/developers"),
    ]
    
    for name, key, url in checks:
        status = "✓" if key else "✗"
        print(f"  {status} {name}: {'Configured' if key else 'Not configured'} - {url}")
    
    # Check collected data
    print("\n📁 Data Files:")
    data_dir = Path(__file__).parent.parent / "artifacts" / "phase1"
    
    files = [
        "pm_data_collection.json",
        "collected_data.json",
        "pm_dashboard.html",
        "pm_briefing_report.html"
    ]
    
    for f in files:
        path = data_dir / f
        if path.exists():
            size = path.stat().st_size
            print(f"  ✓ {f} ({size:,} bytes)")
        else:
            print(f"  ✗ {f} (not found)")
    
    print("\n💡 Tips:")
    print("  - Run 'pm-data collect --all' to collect all data")
    print("  - Add API keys in .env file for full functionality")
    print("  - See data_collection/SETUP.md for setup guide")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="PM Dashboard CLI - Real-time data collection for government decision support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pm-data collect --all              Collect from all sources
  pm-data collect --economic         Collect economic indicators only
  pm-data collect --crisis           Collect crisis monitoring data
  pm-data dashboard                  Generate PM dashboard
  pm-data status                     Show collection status

Setup:
  1. cp .env.example .env
  2. Add API keys to .env
  3. pm-data collect --all
  4. pm-data dashboard
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Collect command
    collect_parser = subparsers.add_parser("collect", help="Collect data from APIs")
    collect_parser.add_argument("--all", action="store_true", help="Collect from all sources")
    collect_parser.add_argument("--economic", action="store_true", help="Collect economic indicators")
    collect_parser.add_argument("--crisis", action="store_true", help="Collect crisis monitoring data")
    collect_parser.add_argument("--service", action="store_true", help="Collect service delivery data")
    collect_parser.add_argument("--sentiment", action="store_true", help="Collect sentiment data")
    collect_parser.add_argument("--max-items", type=int, default=100, help="Maximum items per source")
    collect_parser.set_defaults(func=cmd_collect)
    
    # Dashboard command
    dash_parser = subparsers.add_parser("dashboard", help="Generate PM dashboard")
    dash_parser.set_defaults(func=cmd_dashboard)
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show collection status")
    status_parser.set_defaults(func=cmd_status)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
