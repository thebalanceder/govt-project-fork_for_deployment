"""Phase 1 runner: text input -> semantic state -> archetypes -> evolution -> JSON output."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import random
from typing import Any

from ..archetypes.clustering import validate_cluster_coverage
from ..archetypes.profiles import derive_initial_attitudes, get_default_profiles
from ..models.embedding.embedder import Embedder
from ..models.sentiment.sentiment_model import SentimentModel
from ..models.topic.topic_model import TopicModel
from .network import build_network, neighbor_mean
from .update_rules import UpdateConfig, update_attitude


@dataclass(slots=True)
class RunnerConfig:
    rounds: int = 3
    seed: int = 42
    topology: str = "fully_connected"
    update: UpdateConfig = field(default_factory=UpdateConfig)

    def __post_init__(self) -> None:
        if self.rounds < 3:
            msg = "rounds must be >= 3 for milestone M1"
            raise ValueError(msg)


def _module_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_sample_comments() -> list[str]:
    path = _module_root() / "data" / "raw" / "product" / "sample_reviews.json"
    if not path.exists():
        msg = f"sample data not found: {path}"
        raise FileNotFoundError(msg)
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [str(item.get("comment", "")) for item in payload]


def _sentiment_signal(scores: list[float]) -> float:
    if not scores:
        return 0.0
    return max(-1.0, min(1.0, sum(scores) / len(scores)))


def _topic_distribution(topic_ids: list[int]) -> dict[str, float]:
    if not topic_ids:
        return {"topic_0": 1.0}
    total = len(topic_ids)
    counts: dict[int, int] = {}
    for topic_id in topic_ids:
        counts[topic_id] = counts.get(topic_id, 0) + 1
    return {f"topic_{topic_id}": count / total for topic_id, count in sorted(counts.items())}


def run_phase1_simulation(
    product_description: str,
    comments: list[str] | None = None,
    config: RunnerConfig | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Run Phase 1 end-to-end simulation and optionally persist JSON artifact."""
    if not product_description.strip() and not comments:
        msg = "product_description or comments must be provided"
        raise ValueError(msg)

    runtime = config or RunnerConfig()
    texts = comments if comments else load_sample_comments()
    if not texts:
        msg = "no comments available for simulation"
        raise ValueError(msg)

    embedder = Embedder()
    sentiment_model = SentimentModel()
    topic_model = TopicModel()

    embeddings = embedder.encode([product_description, *texts])
    coverage = validate_cluster_coverage(embeddings, n_clusters=6)

    sentiment_results = sentiment_model.analyze(texts)
    sentiment_scores = [item.score for item in sentiment_results]
    sentiment_signal = _sentiment_signal(sentiment_scores)

    topics, topic_words = topic_model.fit_transform(texts)
    topic_ids = [item.topic_id for item in topics]
    topic_distribution = _topic_distribution(topic_ids)

    initial_attitudes = derive_initial_attitudes(sentiment_signal)
    groups = list(initial_attitudes.keys())
    adjacency = build_network(groups, topology=runtime.topology)

    rng = random.Random(runtime.seed)
    current_states = dict(initial_attitudes)
    trajectories: list[dict[str, Any]] = []

    for round_index in range(1, runtime.rounds + 1):
        next_states: dict[str, float] = {}
        for group in groups:
            n_mean = neighbor_mean(group, adjacency, current_states)
            next_states[group] = update_attitude(
                current_state=current_states[group],
                input_state=(sentiment_signal + 1.0) / 2.0,
                mean_neighbor_state=n_mean,
                config=runtime.update,
                rng=rng,
            )

        current_states = next_states
        overall = sum(current_states.values()) / len(current_states)
        trajectories.append(
            {
                "round": round_index,
                "group_attitudes": dict(current_states),
                "overall_satisfaction": overall,
                "topic_distribution": topic_distribution,
            }
        )

    output: dict[str, Any] = {
        "input": {
            "product_description": product_description,
            "n_comments": len(texts),
        },
        "profiles": get_default_profiles(),
        "initial_attitudes": initial_attitudes,
        "trajectories": trajectories,
        "semantic_summary": {
            "sentiment_signal": sentiment_signal,
            "topic_distribution": topic_distribution,
            "topic_words": topic_words,
        },
        "coverage_validation": asdict(coverage),
    }

    destination = Path(output_path) if output_path else _module_root() / "artifacts" / "phase1" / "milestone_m1_output.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    output["artifact_path"] = str(destination)
    return output


def _print_summary(result: dict[str, Any]) -> None:
    print("Phase 1 simulation complete")
    print(f"Artifact: {result['artifact_path']}")
    print(f"Groups: {len(result['initial_attitudes'])}")
    print(f"Rounds: {len(result['trajectories'])}")


if __name__ == "__main__":
    sample_description = "A smart home product emphasizing battery life, simple setup, and reliable daily use."
    sim_result = run_phase1_simulation(product_description=sample_description)
    _print_summary(sim_result)
