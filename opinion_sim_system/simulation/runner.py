"""Phase 1 runner: text input -> semantic state -> archetypes -> evolution -> JSON output."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import random
from typing import Any

from ..archetypes.clustering import validate_cluster_coverage
from ..archetypes.profiles import derive_initial_attitudes, get_default_profiles
from ..models.semantic_mapper_v2 import SemanticMapperV2
from ..models.task_experts import InputCase
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


def run_phase1_simulation(
    product_description: str,
    comments: list[str] | None = None,
    target: str | None = None,
    domain: str = "product",
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

    mapper = SemanticMapperV2.with_defaults()

    embeddings = mapper.embedder.encode([product_description, *texts])
    coverage = validate_cluster_coverage(embeddings, n_clusters=6)

    case = InputCase(
        text=product_description,
        target=target if target else product_description,
        domain=domain,
    )
    semantic_state = mapper.build_from_case(case=case, comments=texts)
    sentiment_signal = semantic_state.sentiment
    topic_distribution = dict(semantic_state.topic)
    topic_payload = semantic_state.evidence_trace.get("experts", {}).get("topic", {}).get("payload", {})
    topic_words = topic_payload.get("topic_words", {})

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
                input_state=semantic_state.stance,
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
            "target": target if target else product_description,
            "domain": domain,
        },
        "profiles": get_default_profiles(),
        "initial_attitudes": initial_attitudes,
        "trajectories": trajectories,
        "semantic_summary": {
            "mapper_version": "v2",
            "sentiment_signal": sentiment_signal,
            "stance_signal": semantic_state.stance,
            "topic_distribution": topic_distribution,
            "topic_words": topic_words,
            "semantic_trace": semantic_state.evidence_trace,
            "semantic_evidence": semantic_state.evidence_trace,
        },
        "semantic_state": {
            "sentiment": semantic_state.sentiment,
            "stance": semantic_state.stance,
            "topic": semantic_state.topic,
            "embedding": semantic_state.embedding,
        },
        "semantic_trace": semantic_state.evidence_trace,
        "semantic_evidence": semantic_state.evidence_trace,
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
