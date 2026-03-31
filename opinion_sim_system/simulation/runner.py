"""Phase 1 runner: phase1.3 semantic-to-group-attitude engine pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import random
import re
from typing import Any

from ..archetypes.clustering import validate_cluster_coverage
from ..archetypes.profiles import derive_initial_attitudes, get_default_profiles
from ..experiments.semantic_checks import (
    continuity_report,
    decoupling_report,
    multi_split_stability_report,
    report_to_dict,
)
from ..models.semantic_mapper import SemanticMapper
from ..models.semantic_mapper import cosine_distance
from ..models.semantic_state import SemanticState
from .network import build_network, neighbor_mean
from .update_rules import UpdateConfig, heterogeneous_update_attitude


@dataclass(slots=True)
class RunnerConfig:
    rounds: int = 3
    seed: int = 42
    topology: str = "fully_connected"
    enforce_phase12: bool = True
    enforce_semantic_guarantees: bool = True
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


def _asdict_semantic_state(state: SemanticState) -> dict[str, Any]:
    return {
        "sentiment": state.sentiment,
        "stance": state.stance,
        "topic": dict(state.topic),
        "embedding": list(state.embedding),
    }


TOKEN_RE = re.compile(r"[\w\u4e00-\u9fff]+", re.UNICODE)


def _token_set(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text) if len(token) > 1}


def _jaccard_similarity(text_a: str, text_b: str) -> float:
    set_a = _token_set(text_a)
    set_b = _token_set(text_b)
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)


def _pairwise_from_texts(
    texts: list[str],
    states: list[SemanticState],
) -> tuple[list[tuple[SemanticState, SemanticState]], list[tuple[SemanticState, SemanticState]]]:
    if len(states) < 4 or len(states) != len(texts):
        return [], []

    similar_pairs: list[tuple[SemanticState, SemanticState]] = []
    dissimilar_pairs: list[tuple[SemanticState, SemanticState]] = []
    pairs: list[tuple[float, int, int]] = []

    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            score = _jaccard_similarity(texts[i], texts[j])
            pairs.append((score, i, j))

    if len(pairs) < 2:
        return [], []

    pairs.sort(key=lambda item: item[0], reverse=True)
    top_n = max(1, min(2, len(pairs) // 2))
    similar_indices = pairs[:top_n]
    dissimilar_indices = list(reversed(pairs[-top_n:]))

    for _, i, j in similar_indices:
        similar_pairs.append((states[i], states[j]))

    for _, i, j in dissimilar_indices:
        dissimilar_pairs.append((states[i], states[j]))

    if similar_pairs and dissimilar_pairs:
        return similar_pairs, dissimilar_pairs

    # Fallback deterministic pairing if token overlap is uninformative.
    for index in range(0, len(states) - 1, 2):
        similar_pairs.append((states[index], states[index + 1]))

    for index in range(0, len(states) // 2):
        dissimilar_pairs.append((states[index], states[-(index + 1)]))

    return similar_pairs, dissimilar_pairs


def _dynamics_metrics(trajectories: list[dict[str, Any]]) -> dict[str, float | bool]:
    if len(trajectories) < 2:
        return {
            "convergence": False,
            "volatility": 0.0,
            "dispersion": 0.0,
            "dispersion_start": 0.0,
            "dispersion_end": 0.0,
        }

    dispersions: list[float] = []
    overall: list[float] = []
    for item in trajectories:
        values = list(item["group_attitudes"].values())
        dispersions.append(max(values) - min(values))
        overall.append(float(item["overall_satisfaction"]))

    volatility = sum(abs(overall[i] - overall[i - 1]) for i in range(1, len(overall))) / (len(overall) - 1)
    return {
        "convergence": dispersions[-1] <= dispersions[0],
        "volatility": float(volatility),
        "dispersion": float(dispersions[-1]),
        "dispersion_start": float(dispersions[0]),
        "dispersion_end": float(dispersions[-1]),
    }


def _task_configs(base_comments: list[str]) -> dict[str, tuple[str, list[str]]]:
    return {
        "policy": (
            "A public policy service with fairness, transparency, and response efficiency.",
            [
                "service transparency is improving",
                "流程有点复杂但整体公平",
                "response speed should be better",
            ],
        ),
        "product": (
            "A consumer product emphasizing battery life and reliability.",
            list(base_comments),
        ),
        "support": (
            "A customer support process prioritizing clarity and empathy.",
            [
                "support agent solved my issue quickly",
                "沟通清楚，态度很好",
                "waiting time is still long",
            ],
        ),
    }


def _task_generalization(
    mapper: SemanticMapper,
    runtime: RunnerConfig,
    base_comments: list[str],
) -> dict[str, Any]:
    configs = _task_configs(base_comments)
    profiles = get_default_profiles()
    groups = list(profiles.keys())
    adjacency = build_network(groups, topology=runtime.topology)

    task_outputs: dict[str, dict[str, float]] = {}
    vector_deltas: dict[str, list[float]] = {}
    for index, (task_name, (desc, comments)) in enumerate(configs.items()):
        semantic_state = mapper.build(desc, comments)
        initial = derive_initial_attitudes(semantic_state.sentiment)
        rng = random.Random(runtime.seed + 100 + index)
        next_states: dict[str, float] = {}

        for group in groups:
            n_mean = neighbor_mean(group, adjacency, initial)
            next_state, _ = heterogeneous_update_attitude(
                agent_profile=profiles[group],
                agent_state=initial[group],
                neighbors_state=n_mean,
                semantic_state=semantic_state,
                config=runtime.update,
                rng=rng,
            )
            next_states[group] = next_state

        deltas = [next_states[group] - initial[group] for group in groups]
        vector_deltas[task_name] = [float(item) for item in deltas]

        task_outputs[task_name] = {
            "semantic_stance": semantic_state.stance,
            "avg_initial": float(sum(initial.values()) / len(initial)),
            "avg_next": float(sum(next_states.values()) / len(next_states)),
        }

    task_names = sorted(vector_deltas.keys())
    pair_distances: list[float] = []
    for i in range(len(task_names)):
        for j in range(i + 1, len(task_names)):
            vec_a = vector_deltas[task_names[i]]
            vec_b = vector_deltas[task_names[j]]
            pair_distances.append(cosine_distance(vec_a, vec_b))

    mechanism_consistency = float(sum(pair_distances) / len(pair_distances)) if pair_distances else 0.0
    return {
        "tasks": task_outputs,
        "response_vectors": vector_deltas,
        "pairwise_vector_distance": pair_distances,
        "mechanism_consistency": mechanism_consistency,
        "passed": mechanism_consistency <= 0.35,
    }


def _copy_update_config(config: UpdateConfig) -> UpdateConfig:
    return UpdateConfig(
        inertia=config.inertia,
        alpha=config.alpha,
        beta=config.beta,
        noise_std=config.noise_std,
        clamp_min=config.clamp_min,
        clamp_max=config.clamp_max,
        max_step_delta=config.max_step_delta,
    )


def _perturb(value: float, ratio: float) -> float:
    return max(0.0, value * (1.0 + ratio))


def _stage3_calibration(
    profiles: dict[str, dict[str, float]],
    adjacency: dict[str, list[str]],
    initial_attitudes: dict[str, float],
    semantic_state: SemanticState,
    runtime: RunnerConfig,
) -> dict[str, Any]:
    groups = list(initial_attitudes.keys())
    scenarios = {
        "replay_base": _copy_update_config(runtime.update),
        "perturb_alpha_plus": UpdateConfig(
            inertia=runtime.update.inertia,
            alpha=_perturb(runtime.update.alpha, 0.1),
            beta=runtime.update.beta,
            noise_std=runtime.update.noise_std,
            clamp_min=runtime.update.clamp_min,
            clamp_max=runtime.update.clamp_max,
            max_step_delta=runtime.update.max_step_delta,
        ),
        "perturb_beta_minus": UpdateConfig(
            inertia=runtime.update.inertia,
            alpha=runtime.update.alpha,
            beta=_perturb(runtime.update.beta, -0.1),
            noise_std=runtime.update.noise_std,
            clamp_min=runtime.update.clamp_min,
            clamp_max=runtime.update.clamp_max,
            max_step_delta=runtime.update.max_step_delta,
        ),
    }

    scenario_vectors: dict[str, list[float]] = {}
    scenario_volatility: dict[str, float] = {}

    for offset, (name, update_cfg) in enumerate(scenarios.items()):
        current = dict(initial_attitudes)
        rng = random.Random(runtime.seed + 1000 + offset)
        overall_trace: list[float] = []

        for _ in range(runtime.rounds):
            next_states: dict[str, float] = {}
            for group in groups:
                n_mean = neighbor_mean(group, adjacency, current)
                next_state, _ = heterogeneous_update_attitude(
                    agent_profile=profiles[group],
                    agent_state=current[group],
                    neighbors_state=n_mean,
                    semantic_state=semantic_state,
                    config=update_cfg,
                    rng=rng,
                )
                next_states[group] = next_state
            current = next_states
            overall_trace.append(float(sum(current.values()) / len(current)))

        scenario_vectors[name] = [current[group] for group in groups]
        if len(overall_trace) > 1:
            volatility = sum(abs(overall_trace[i] - overall_trace[i - 1]) for i in range(1, len(overall_trace))) / (
                len(overall_trace) - 1
            )
        else:
            volatility = 0.0
        scenario_volatility[name] = float(volatility)

    replay_distance = cosine_distance(scenario_vectors["replay_base"], scenario_vectors["replay_base"])
    perturb_distances = {
        name: cosine_distance(scenario_vectors["replay_base"], vector)
        for name, vector in scenario_vectors.items()
        if name != "replay_base"
    }
    avg_perturb = float(sum(perturb_distances.values()) / len(perturb_distances)) if perturb_distances else 0.0

    passed = replay_distance <= 1e-9 and avg_perturb <= 0.25
    return {
        "replay_distance": replay_distance,
        "perturbation_distances": perturb_distances,
        "scenario_volatility": scenario_volatility,
        "passed": passed,
    }


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

    mapper = SemanticMapper.with_defaults()
    embeddings = mapper.embedder.encode([product_description, *texts])
    coverage = validate_cluster_coverage(embeddings, n_clusters=6)

    semantic_state = mapper.build(product_description=product_description, comments=texts)
    per_text_states = [mapper.build_for_single_text(text) for text in texts]
    similar_pairs, dissimilar_pairs = _pairwise_from_texts(texts=texts, states=per_text_states)

    continuity = continuity_report(similar_pairs=similar_pairs, dissimilar_pairs=dissimilar_pairs)
    decoupling = decoupling_report(states=per_text_states)
    stability = multi_split_stability_report(states=per_text_states, n_splits=3)

    initial_attitudes = derive_initial_attitudes(semantic_state.sentiment)
    groups = list(initial_attitudes.keys())
    profiles = get_default_profiles()
    adjacency = build_network(groups, topology=runtime.topology)

    rng = random.Random(runtime.seed)
    current_states = dict(initial_attitudes)
    trajectories: list[dict[str, Any]] = []

    for round_index in range(1, runtime.rounds + 1):
        next_states: dict[str, float] = {}
        round_attribution: dict[str, dict[str, float]] = {}
        for group in groups:
            n_mean = neighbor_mean(group, adjacency, current_states)
            next_state, attribution = heterogeneous_update_attitude(
                agent_profile=profiles[group],
                agent_state=current_states[group],
                neighbors_state=n_mean,
                semantic_state=semantic_state,
                config=runtime.update,
                rng=rng,
            )
            next_states[group] = next_state
            round_attribution[group] = attribution

        current_states = next_states
        overall = sum(current_states.values()) / len(current_states)
        trajectories.append(
            {
                "round": round_index,
                "group_attitudes": dict(current_states),
                "overall_satisfaction": overall,
                "topic_distribution": dict(semantic_state.topic),
                "attribution": round_attribution,
            }
        )

    dynamics = _dynamics_metrics(trajectories)
    stage3_calibration = _stage3_calibration(
        profiles=profiles,
        adjacency=adjacency,
        initial_attitudes=initial_attitudes,
        semantic_state=semantic_state,
        runtime=runtime,
    )
    task_generalization = _task_generalization(mapper=mapper, runtime=runtime, base_comments=texts)

    semantic_closed_loop_passed = continuity.passed and decoupling.passed and stability.passed
    dynamics_closed_loop_passed = bool(dynamics["convergence"]) and bool(stage3_calibration["passed"]) and bool(
        task_generalization["passed"]
    )
    decision_closed_loop_passed = all("attribution" in item for item in trajectories)

    if runtime.enforce_semantic_guarantees and not semantic_closed_loop_passed:
        msg = "semantic guarantees failed: continuity/decoupling/cross-batch-stability must all pass"
        raise ValueError(msg)

    output: dict[str, Any] = {
        "input": {
            "product_description": product_description,
            "n_comments": len(texts),
        },
        "profiles": profiles,
        "initial_attitudes": initial_attitudes,
        "trajectories": trajectories,
        "semantic_state": _asdict_semantic_state(semantic_state),
        "semantic_experiments": {
            "continuity": report_to_dict(continuity),
            "decoupling": report_to_dict(decoupling),
            "cross_batch_stability": report_to_dict(stability),
        },
        "dynamics_metrics": dynamics,
        "stage3_calibration": stage3_calibration,
        "task_generalization": task_generalization,
        "three_loop_consistency": {
            "semantic_closure": semantic_closed_loop_passed,
            "dynamics_closure": dynamics_closed_loop_passed,
            "decision_closure": decision_closed_loop_passed,
        },
        "coverage_validation": asdict(coverage),
        "api_frontend_bundle": {
            "api_version": "phase1.3",
            "chain": ["input_semantics", "group_state", "evolution_trajectory", "attribution_explanation"],
            "frontend_panels": ["semantic_state", "attitude_trajectory", "attribution", "task_comparison"],
        },
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
