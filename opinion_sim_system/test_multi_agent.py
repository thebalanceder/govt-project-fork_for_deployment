#!/usr/bin/env python3
"""
Test Multi-Agent Discussion System

Demonstrates 6 AI experts discussing economic, political, and cultural topics
using MiroFish opinion evolution methodology
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from opinion_sim_system.mirofish.discussion import run_all_topics_discussion
from opinion_sim_system.data_collection.malaysia_collector import MalaysiaDataCollector


def main():
    """Run complete multi-agent discussion test."""
    
    print("=" * 70)
    print("🇲🇾 CSPOPS Malaysia - Multi-Agent AI Discussion System")
    print("=" * 70)
    print()
    print("6 Expert Agents:")
    print("  1. Dr. Lim Wei Chen - Chief Economist")
    print("  2. Datin Sri Aisha - Policy Advisor")
    print("  3. Encik Razak - Business Leader")
    print("  4. Dr. Muthu - Sociologist")
    print("  5. Ms. Wong - International Relations Expert")
    print("  6. Ahmad - Public Representative")
    print()
    print("3 Topics:")
    print("  • Economic")
    print("  • Political")
    print("  • Cultural")
    print()
    print("=" * 70)
    
    # Collect some test data
    print("\n📥 Collecting data...")
    collector = MalaysiaDataCollector()
    
    data = {
        'economic': collector.collect_malaysian_economic_data(),
        'political': [],  # Would collect political news
        'cultural': [],   # Would collect cultural news
        'social_media': [],  # Would collect social media
        'news': []  # Would collect general news
    }
    
    print(f"✓ Collected {len(data['economic'])} economic indicators")
    
    # Convert DataItem objects to dicts for the discussion engine
    data_dict = {
        'economic': [
            {
                'text': item.text,
                'value': item.value,
                'metadata': item.metadata
            }
            for item in data['economic']
        ],
        'political': data['political'],
        'cultural': data['cultural'],
        'social_media': data['social_media'],
        'news': data['news']
    }
    
    # Run multi-agent discussions for all topics
    print("\n🤖 Starting Multi-Agent Discussions...")
    print()
    
    results = run_all_topics_discussion(data_dict)
    
    # Print final results
    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS")
    print("=" * 70)
    
    for topic, result in results.items():
        print(f"\n{topic.upper()}:")
        print(f"  Consensus: {result.final_consensus:.2f}")
        print(f"  Convergence: {result.convergence_rate:.0%}")
        print(f"  Rounds: {len(result.rounds)}")
        
        sentiment_label = "positive" if result.final_consensus > 0.1 else "negative" if result.final_consensus < -0.1 else "neutral"
        print(f"  Sentiment: {sentiment_label}")
        
        # Show agent forecasts
        print(f"\n  Agent Forecasts:")
        for agent_name, forecast in result.agent_forecasts.items():
            print(f"    {agent_name}:")
            print(f"      Current: {forecast['sentiment']:.2f}")
            print(f"      7-day: {forecast['forecast_7d']:.2f}")
            print(f"      30-day: {forecast['forecast_30d']:.2f}")
            print(f"      Confidence: {forecast['confidence']:.0%}")
    
    print("\n" + "=" * 70)
    print("✅ Multi-Agent Discussion Complete!")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    main()
