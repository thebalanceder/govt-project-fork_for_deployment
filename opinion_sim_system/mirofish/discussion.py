"""
MiroFish Multi-Agent Discussion Engine

Implements opinion evolution through structured agent discussions
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

from ..agents.six_agents import create_all_agents, BaseAgent, AgentState


@dataclass
class DiscussionRound:
    """Represents one round of multi-agent discussion."""
    round_number: int
    agent_states: Dict[str, AgentState]
    responses: List[str]
    average_sentiment: float
    convergence_score: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DiscussionResult:
    """Final result of multi-agent discussion."""
    topic: str
    rounds: List[DiscussionRound]
    final_consensus: float
    convergence_rate: float
    agent_forecasts: Dict[str, Dict[str, float]]
    explanation: str
    timestamp: datetime = field(default_factory=datetime.now)


class MiroFishDiscussion:
    """
    MiroFish-style multi-agent discussion engine.
    
    Process:
    1. Each agent analyzes data independently
    2. Agents share initial positions
    3. Multiple rounds of discussion (respond to each other)
    4. Opinion evolution (agents update based on others)
    5. Convergence toward consensus
    6. Final forecast generation
    """
    
    def __init__(self, agents: Optional[List[BaseAgent]] = None):
        """
        Initialize discussion engine.
        
        Args:
            agents: List of agents (default: all 6 expert agents)
        """
        self.agents = agents or create_all_agents()
        self.discussion_history: List[DiscussionRound] = []
        self.current_topic: str = ""
    
    def analyze_initial(self, data: Dict[str, Any], topic: str) -> Dict[str, AgentState]:
        """
        Step 1: Each agent analyzes data independently.
        
        Args:
            data: News, social media, economic data
            topic: 'economic', 'political', or 'cultural'
        
        Returns:
            Dictionary of agent states
        """
        self.current_topic = topic
        initial_states = {}
        
        print(f"\n📊 Topic: {topic.capitalize()}")
        print("─" * 60)
        print("🔄 Initial Agent Analysis")
        print("─" * 60)
        
        for agent in self.agents:
            state = agent.analyze(data, topic)
            initial_states[agent.profile.name] = state
            
            sentiment_label = "positive" if state.sentiment > 0.1 else "negative" if state.sentiment < -0.1 else "neutral"
            print(f"{agent.profile.name}: {state.sentiment:.2f} ({sentiment_label})")
        
        return initial_states
    
    def run_discussion(self, data: Dict[str, Any], topic: str, num_rounds: int = 3) -> DiscussionResult:
        """
        Run complete MiroFish discussion process.
        
        Args:
            data: Input data for analysis
            topic: Topic to discuss
            num_rounds: Number of discussion rounds
        
        Returns:
            DiscussionResult with consensus and forecasts
        """
        # Step 1: Initial analysis
        initial_states = self.analyze_initial(data, topic)
        
        # Create first round
        round_0 = DiscussionRound(
            round_number=0,
            agent_states=initial_states.copy(),
            responses=[],
            average_sentiment=sum(s.sentiment for s in initial_states.values()) / len(initial_states),
            convergence_score=0.0
        )
        self.discussion_history = [round_0]
        
        # Step 2: Discussion rounds
        for round_num in range(1, num_rounds + 1):
            round_result = self._run_round(round_num, data, topic)
            self.discussion_history.append(round_result)
        
        # Step 3: Calculate final consensus
        final_states = self.discussion_history[-1].agent_states
        final_consensus = sum(s.sentiment for s in final_states.values()) / len(final_states)
        
        # Calculate convergence (how close agents are to each other)
        sentiments = [s.sentiment for s in final_states.values()]
        variance = sum((s - final_consensus) ** 2 for s in sentiments) / len(sentiments)
        convergence_rate = 1.0 - min(1.0, variance * 10)  # Higher variance = lower convergence
        
        # Step 4: Generate forecasts
        agent_forecasts = {}
        for agent in self.agents:
            if agent.state:
                agent_forecasts[agent.profile.name] = {
                    'sentiment': agent.state.sentiment,
                    'forecast_7d': agent.generate_forecast(7),
                    'forecast_30d': agent.generate_forecast(30),
                    'confidence': agent.state.confidence
                }
        
        # Step 5: Generate explanation
        explanation = self._generate_explanation(topic, final_consensus, convergence_rate, agent_forecasts)
        
        return DiscussionResult(
            topic=topic,
            rounds=self.discussion_history.copy(),
            final_consensus=final_consensus,
            convergence_rate=convergence_rate,
            agent_forecasts=agent_forecasts,
            explanation=explanation
        )
    
    def _run_round(self, round_num: int, data: Dict[str, Any], topic: str) -> DiscussionRound:
        """Run one round of discussion."""
        
        print(f"\n🔄 MiroFish Discussion - Round {round_num}")
        print("─" * 60)
        
        responses = []
        current_states = {agent.profile.name: agent.state for agent in self.agents if agent.state}
        
        # Each agent responds to others
        for i, agent in enumerate(self.agents):
            # Get other agents' states
            other_states = [s for name, s in current_states.items() if name != agent.profile.name]
            
            if other_states:
                # Pick one agent to respond to (round-robin style)
                other_idx = i % len(other_states)
                other_state = other_states[other_idx]
                other_name = [name for name, s in current_states.items() if name != agent.profile.name][other_idx]
                
                # Generate response
                response = agent.respond_to(other_name, other_state)
                responses.append(f"{agent.profile.name}: {response}")
                
                # Update opinion based on others (MiroFish evolution)
                influence_factor = 0.15  # How much agents influence each other
                agent.update_opinion(other_states, influence_factor)
                
                print(f"{agent.profile.name}: Updated to {agent.state.sentiment:.2f}")
        
        # Calculate round statistics
        new_states = {agent.profile.name: agent.state for agent in self.agents if agent.state}
        average_sentiment = sum(s.sentiment for s in new_states.values()) / len(new_states)
        
        # Calculate convergence
        sentiments = [s.sentiment for s in new_states.values()]
        variance = sum((s - average_sentiment) ** 2 for s in sentiments) / len(sentiments)
        convergence_score = 1.0 - min(1.0, variance * 10)
        
        return DiscussionRound(
            round_number=round_num,
            agent_states=new_states.copy(),
            responses=responses,
            average_sentiment=average_sentiment,
            convergence_score=convergence_score
        )
    
    def _generate_explanation(self, topic: str, consensus: float, convergence: float, 
                            forecasts: Dict[str, Dict[str, float]]) -> str:
        """Generate natural language explanation of results."""
        
        sentiment_label = "positive" if consensus > 0.1 else "negative" if consensus < -0.1 else "neutral"
        
        explanation_parts = [
            f"After multi-agent discussion on {topic} matters, the consensus is {sentiment_label} ({consensus:.2f}).",
            f"Convergence rate: {convergence:.0%} (agents {'largely agree' if convergence > 0.7 else 'have diverse views'}).",
            "",
            "Key insights from agents:"
        ]
        
        # Add top 3 agent insights
        sorted_agents = sorted(forecasts.items(), key=lambda x: x[1]['confidence'], reverse=True)
        
        for name, forecast in sorted_agents[:3]:
            agent_label = "positive" if forecast['sentiment'] > 0.1 else "negative" if forecast['sentiment'] < -0.1 else "neutral"
            explanation_parts.append(
                f"- {name}: {agent_label} outlook ({forecast['sentiment']:.2f}), "
                f"7-day forecast: {forecast['forecast_7d']:.2f}"
            )
        
        # Add forecast summary
        avg_7d = sum(f['forecast_7d'] for f in forecasts.values()) / len(forecasts)
        avg_30d = sum(f['forecast_30d'] for f in forecasts.values()) / len(forecasts)
        
        explanation_parts.extend([
            "",
            f"Forecast Summary:",
            f"- 7-day: {avg_7d:.2f} ({'improving' if avg_7d > consensus else 'declining' if avg_7d < consensus else 'stable'})",
            f"- 30-day: {avg_30d:.2f} ({'sustained growth' if avg_30d > 0.1 else 'challenges ahead' if avg_30d < -0.1 else 'stability expected'})"
        ])
        
        return "\n".join(explanation_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert discussion result to dictionary."""
        if not self.discussion_history:
            return {}
        
        final_round = self.discussion_history[-1]
        
        return {
            'topic': self.current_topic,
            'num_rounds': len(self.discussion_history),
            'final_consensus': final_round.average_sentiment,
            'convergence_rate': final_round.convergence_score,
            'agent_states': {
                name: {
                    'sentiment': state.sentiment,
                    'confidence': state.confidence,
                    'key_factors': state.key_factors
                }
                for name, state in final_round.agent_states.items()
            },
            'timestamp': final_round.timestamp.isoformat()
        }


def run_multi_agent_discussion(data: Dict[str, Any], topic: str) -> DiscussionResult:
    """
    Convenience function to run complete multi-agent discussion.
    
    Args:
        data: Input data (news, social media, economic indicators)
        topic: 'economic', 'political', or 'cultural'
    
    Returns:
        DiscussionResult with consensus and forecasts
    """
    engine = MiroFishDiscussion()
    return engine.run_discussion(data, topic)


def run_all_topics_discussion(data: Dict[str, Any]) -> Dict[str, DiscussionResult]:
    """
    Run discussions for all three topics.
    
    Args:
        data: Input data
    
    Returns:
        Dictionary of results per topic
    """
    results = {}
    
    for topic in ['economic', 'political', 'cultural']:
        print(f"\n{'='*70}")
        print(f"🇲🇾 CSPOPS Malaysia - {topic.capitalize()} Analysis")
        print(f"{'='*70}")
        
        engine = MiroFishDiscussion()
        result = engine.run_discussion(data, topic)
        results[topic] = result
        
        print(f"\n✅ Consensus: {result.final_consensus:.2f}")
        print(f"📈 Convergence: {result.convergence_rate:.0%}")
    
    return results
