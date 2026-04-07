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
from .update_rules import UpdateConfig, update_attitude, heterogeneous_update_attitude


def _compute_dispersion(group_attitudes: dict[str, float]) -> float:
    if not group_attitudes:
        return 0.0
    values = list(group_attitudes.values())
    return float(max(values) - min(values))


def _safe_component(components: dict[str, Any], key: str) -> float:
    value = components.get(key, 0.0)
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def _build_driver_summary(semantic_evidence: dict[str, Any]) -> dict[str, Any]:
    fusion = semantic_evidence.get("fusion", {}) if isinstance(semantic_evidence, dict) else {}
    stance_components = fusion.get("stance_components", {}) if isinstance(fusion, dict) else {}
    experts = semantic_evidence.get("experts", {}) if isinstance(semantic_evidence, dict) else {}
    frame_score = 0.0
    if isinstance(experts, dict):
        frame = experts.get("frame", {})
        if isinstance(frame, dict):
            raw = frame.get("score", 0.0)
            if isinstance(raw, (int, float)):
                frame_score = abs(float(raw))

    scored = {
        "acceptance": _safe_component(stance_components, "acceptance_expert"),
        "sentiment": _safe_component(stance_components, "sentiment_component"),
        "conflict": _safe_component(stance_components, "conflict_component"),
        "frame": frame_score,
    }
    dominant_driver = max(scored.items(), key=lambda item: item[1])[0] if scored else "acceptance"
    return {
        "dominant_driver": dominant_driver,
        "scores": scored,
    }


def _build_activation_reasons(semantic_evidence: dict[str, Any]) -> list[dict[str, Any]]:
    experts = semantic_evidence.get("experts", {}) if isinstance(semantic_evidence, dict) else {}
    if not isinstance(experts, dict):
        return []

    reasons: list[dict[str, Any]] = []
    for expert_name in ("acceptance", "conflict", "frame", "sentiment"):
        expert = experts.get(expert_name, {})
        if not isinstance(expert, dict):
            continue
        score = expert.get("score", 0.0)
        confidence = expert.get("confidence", 0.0)
        reasons.append(
            {
                "expert": expert_name,
                "label": str(expert.get("label", "")),
                "score": float(score) if isinstance(score, (int, float)) else 0.0,
                "confidence": float(confidence) if isinstance(confidence, (int, float)) else 0.0,
                "weight": (float(score) if isinstance(score, (int, float)) else 0.0)
                * (float(confidence) if isinstance(confidence, (int, float)) else 0.0),
            }
        )
    return sorted(reasons, key=lambda item: item["weight"], reverse=True)


def _build_divergence_summary(trajectories: list[dict[str, Any]]) -> dict[str, Any]:
    if not trajectories:
        return {"final_dispersion": 0.0, "max_dispersion": 0.0, "trend": "stable"}

    dispersions = [float(round_item.get("dispersion", 0.0)) for round_item in trajectories]
    final_dispersion = dispersions[-1]
    max_dispersion = max(dispersions)
    start_dispersion = dispersions[0]
    if final_dispersion > start_dispersion + 0.05:
        trend = "widening"
    elif final_dispersion < start_dispersion - 0.05:
        trend = "narrowing"
    else:
        trend = "stable"
    return {
        "final_dispersion": float(final_dispersion),
        "max_dispersion": float(max_dispersion),
        "trend": trend,
    }


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
    texts = comments if comments else [product_description]

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
    semantic_evidence = semantic_state.evidence_trace

    driver_summary = _build_driver_summary(semantic_evidence=semantic_evidence)
    activation_reasons = _build_activation_reasons(semantic_evidence=semantic_evidence)

    profiles = get_default_profiles()
    initial_attitudes = derive_initial_attitudes(sentiment_signal)
    groups = list(initial_attitudes.keys())
    adjacency = build_network(groups, topology=runtime.topology)

    rng = random.Random(runtime.seed)
    current_states = dict(initial_attitudes)
    previous_states = dict(initial_attitudes)
    previous_overall = sum(current_states.values()) / len(current_states)
    trajectories: list[dict[str, Any]] = []

    for round_index in range(1, runtime.rounds + 1):
        next_states: dict[str, float] = {}
        round_attributions: dict[str, dict[str, float]] = {}
        for group in groups:
            n_mean = neighbor_mean(group, adjacency, current_states)
            profile = profiles.get(group, {})
            new_state, attribution = heterogeneous_update_attitude(
                agent_profile=profile,
                agent_state=current_states[group],
                neighbors_state=n_mean,
                semantic_state=semantic_state,
                config=runtime.update,
                rng=rng,
            )
            next_states[group] = new_state
            round_attributions[group] = attribution

        current_states = next_states
        overall = sum(current_states.values()) / len(current_states)
        delta_by_group = {
            group: float(current_states[group] - previous_states.get(group, 0.0))
            for group in groups
        }
        overall_delta = float(overall - previous_overall)
        dispersion = _compute_dispersion(current_states)
        trajectories.append(
            {
                "round": round_index,
                "group_attitudes": dict(current_states),
                "overall_satisfaction": overall,
                "topic_distribution": topic_distribution,
                "delta_by_group": delta_by_group,
                "overall_delta": overall_delta,
                "dominant_driver": driver_summary["dominant_driver"],
                "dispersion": dispersion,
                "activation_reasons": activation_reasons,
                "attributions": round_attributions,
            }
        )
        previous_states = dict(current_states)
        previous_overall = overall

    visualization_payload: dict[str, Any] = {
        "schema_version": "phase3.v1",
        "round_count": len(trajectories),
        "rounds": [
            {
                "round": int(item.get("round", 0)),
                "overall_satisfaction": float(item.get("overall_satisfaction", 0.0)),
                "overall_delta": float(item.get("overall_delta", 0.0)),
                "dispersion": float(item.get("dispersion", 0.0)),
                "dominant_driver": str(item.get("dominant_driver", "acceptance")),
                "delta_by_group": dict(item.get("delta_by_group", {})),
                "activation_reasons": list(item.get("activation_reasons", [])),
            }
            for item in trajectories
        ],
        "divergence_summary": _build_divergence_summary(trajectories),
        "driver_summary": driver_summary,
        "provenance_links": {
            "semantic_evidence": "semantic_evidence",
            "stance_components": "semantic_evidence.fusion.stance_components",
            "trajectory_rounds": "trajectories",
        },
    }

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
        "visualization_payload": visualization_payload,
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
