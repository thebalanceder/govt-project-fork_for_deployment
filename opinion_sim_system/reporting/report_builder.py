"""Deterministic report builders for Phase2B/Phase3 briefing outputs."""

from __future__ import annotations

from typing import Any


def _safe_float(value: Any, default: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return default


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _compute_dispersion(group_attitudes: dict[str, Any]) -> float:
    if not group_attitudes:
        return 0.0
    values = [_safe_float(v) for v in group_attitudes.values()]
    return float(max(values) - min(values)) if values else 0.0


def _acceptance_outlook(overall: float) -> str:
    if overall >= 0.7:
        return "high"
    if overall >= 0.5:
        return "moderate"
    return "low"


def _polarization_label(dispersion: float) -> str:
    if dispersion >= 0.35:
        return "high"
    if dispersion >= 0.2:
        return "medium"
    return "low"


def _main_driver(experts: dict[str, Any]) -> str:
    candidates = {
        "acceptance": _safe_float(_safe_dict(experts.get("acceptance")).get("score", 0.0)),
        "conflict": _safe_float(_safe_dict(experts.get("conflict")).get("score", 0.0)),
        "frame": abs(_safe_float(_safe_dict(experts.get("frame")).get("score", 0.0))),
        "sentiment": _safe_float(_safe_dict(experts.get("sentiment")).get("score", 0.0)),
    }
    return max(candidates.items(), key=lambda item: item[1])[0]


def _recommended_action(overall: float, dispersion: float, conflict_score: float) -> str:
    if overall < 0.5:
        return "Prioritize confidence recovery with clear communication and fast feedback loops."
    if conflict_score > 0.6 or dispersion > 0.35:
        return "Run targeted segment outreach to reduce divergence and conflict risk."
    return "Sustain current direction and monitor leading segments for early drift."


def _risk_level(overall_final: float, dispersion: float) -> str:
    if overall_final < 0.5 or dispersion >= 0.35:
        return "high"
    if overall_final < 0.65 or dispersion >= 0.2:
        return "medium"
    return "low"


def _extract_rounds(data: dict[str, Any]) -> list[dict[str, Any]]:
    payload = data.get("visualization_payload", {})
    if isinstance(payload, dict):
        rounds = payload.get("rounds", [])
        if isinstance(rounds, list):
            return [item for item in rounds if isinstance(item, dict)]
    return []


def build_decision_trace(model_evidence: dict[str, Any], simulation_result: dict[str, Any]) -> dict[str, Any]:
    experts = _safe_dict(model_evidence.get("experts"))
    trajectories = simulation_result.get("trajectories", []) if isinstance(simulation_result, dict) else []
    final_round = trajectories[-1] if trajectories else {}
    final_round = _safe_dict(final_round)
    final_groups = _safe_dict(final_round.get("group_attitudes"))

    overall_final = _safe_float(final_round.get("overall_satisfaction", 0.0))
    dispersion = _compute_dispersion(final_groups)

    top_groups = sorted(
        (
            {"group": str(group), "attitude": _safe_float(score)}
            for group, score in final_groups.items()
        ),
        key=lambda item: item["attitude"],
        reverse=True,
    )[:3]

    acceptance = _safe_dict(experts.get("acceptance"))
    conflict = _safe_dict(experts.get("conflict"))
    frame = _safe_dict(experts.get("frame"))

    return {
        "overall_final": overall_final,
        "dispersion": dispersion,
        "main_driver": _main_driver(experts),
        "top_groups": top_groups,
        "acceptance": {
            "label": str(acceptance.get("label", "N/A")),
            "score": _safe_float(acceptance.get("score", 0.0)),
        },
        "conflict": {
            "label": str(conflict.get("label", "N/A")),
            "score": _safe_float(conflict.get("score", 0.0)),
        },
        "frame": {
            "label": str(frame.get("label", "N/A")),
            "score": _safe_float(frame.get("score", 0.0)),
        },
    }


def build_executive_summary(model_evidence: dict[str, Any], simulation_result: dict[str, Any]) -> dict[str, Any]:
    trace = build_decision_trace(model_evidence=model_evidence, simulation_result=simulation_result)
    overall_final = _safe_float(trace.get("overall_final", 0.0))
    dispersion = _safe_float(trace.get("dispersion", 0.0))
    conflict_score = _safe_float(_safe_dict(trace.get("conflict", {})).get("score", 0.0))
    main_driver = str(trace.get("main_driver", "acceptance"))

    acceptance_outlook = _acceptance_outlook(overall_final)
    polarization = _polarization_label(dispersion)

    conclusion_line = (
        f"Projected acceptance is {acceptance_outlook} ({overall_final:.2f}) "
        f"with {polarization} polarization (dispersion {dispersion:.2f})."
    )
    headline = (
        f"Decision outlook: {acceptance_outlook.title()} acceptance, "
        f"{polarization} divergence, driver={main_driver}."
    )

    return {
        "headline": headline,
        "conclusion_line": conclusion_line,
        "four_block_summary": {
            "acceptance_outlook": acceptance_outlook,
            "polarization": polarization,
            "main_driver": main_driver,
            "recommended_action": _recommended_action(overall_final, dispersion, conflict_score),
        },
    }


def build_expanded_fallback_text(executive_summary: dict[str, Any], decision_trace: dict[str, Any]) -> str:
    summary = _safe_dict(executive_summary)
    four_block = _safe_dict(summary.get("four_block_summary"))
    acceptance = _safe_dict(decision_trace.get("acceptance"))
    conflict = _safe_dict(decision_trace.get("conflict"))
    frame = _safe_dict(decision_trace.get("frame"))

    return (
        f"[DeepSeek fallback] {summary.get('conclusion_line', '')} "
        f"Main driver is {four_block.get('main_driver', 'N/A')}. "
        f"Expert signals: acceptance={acceptance.get('label', 'N/A')}, "
        f"conflict={conflict.get('label', 'N/A')}, frame={frame.get('label', 'N/A')}. "
        f"Recommended action: {four_block.get('recommended_action', 'N/A')}"
    ).strip()


def build_evidence_activation(data: dict[str, Any], max_links: int = 8) -> list[dict[str, Any]]:
    rounds = _extract_rounds(data)
    latest_round = rounds[-1] if rounds else {}

    reasons = latest_round.get("activation_reasons", []) if isinstance(latest_round, dict) else []
    if not isinstance(reasons, list):
        reasons = []

    delta_by_group = latest_round.get("delta_by_group", {}) if isinstance(latest_round, dict) else {}
    if not isinstance(delta_by_group, dict):
        delta_by_group = {}

    sorted_groups = sorted(
        ((str(group), abs(_safe_float(delta))) for group, delta in delta_by_group.items()),
        key=lambda item: item[1],
        reverse=True,
    )

    links: list[dict[str, Any]] = []
    for reason in reasons[:4]:
        if not isinstance(reason, dict):
            continue
        source = str(reason.get("expert", "unknown"))
        label = str(reason.get("label", ""))
        base_weight = abs(_safe_float(reason.get("weight", 0.0)))
        for group, delta_abs in sorted_groups[:2]:
            links.append(
                {
                    "source": source,
                    "source_label": label,
                    "target": group,
                    "weight": round(base_weight * (delta_abs + 1e-6), 6),
                    "delta_magnitude": round(delta_abs, 6),
                }
            )

    if links:
        return links[:max_links]

    evidence = data.get("semantic_evidence", {})
    experts = evidence.get("experts", {}) if isinstance(evidence, dict) else {}
    trajectories = data.get("trajectories", []) if isinstance(data, dict) else []
    final_round = trajectories[-1] if trajectories else {}
    group_attitudes = final_round.get("group_attitudes", {}) if isinstance(final_round, dict) else {}
    sorted_groups = sorted(
        ((str(group), _safe_float(score)) for group, score in group_attitudes.items()),
        key=lambda item: item[1],
        reverse=True,
    )

    fallback_links: list[dict[str, Any]] = []
    for expert_name in ("acceptance", "conflict", "frame"):
        expert = experts.get(expert_name, {}) if isinstance(experts, dict) else {}
        score = abs(_safe_float(expert.get("score", 0.0))) if isinstance(expert, dict) else 0.0
        label = str(expert.get("label", "")) if isinstance(expert, dict) else ""
        for group, attitude in sorted_groups[:2]:
            fallback_links.append(
                {
                    "source": expert_name,
                    "source_label": label,
                    "target": group,
                    "weight": round(score * (attitude + 1e-6), 6),
                    "delta_magnitude": round(attitude, 6),
                }
            )
    return fallback_links[:max_links]


def build_evolution_highlights(data: dict[str, Any]) -> list[dict[str, Any]]:
    trajectories = data.get("trajectories", []) if isinstance(data, dict) else []
    if not isinstance(trajectories, list) or not trajectories:
        return []

    rounds = [item for item in trajectories if isinstance(item, dict)]
    if not rounds:
        return []

    overall_series = [
        {
            "round": int(item.get("round", index + 1)),
            "overall": _safe_float(item.get("overall_satisfaction", 0.0)),
            "overall_delta": _safe_float(item.get("overall_delta", 0.0)),
            "dominant_driver": str(item.get("dominant_driver", "N/A")),
        }
        for index, item in enumerate(rounds)
    ]

    biggest_rise = max(overall_series, key=lambda item: item["overall_delta"])
    biggest_drop = min(overall_series, key=lambda item: item["overall_delta"])

    direction = "stable"
    if len(overall_series) >= 2:
        last_delta = overall_series[-1]["overall"] - overall_series[-2]["overall"]
        if last_delta > 0.02:
            direction = "rising"
        elif last_delta < -0.02:
            direction = "falling"

    return [
        {
            "type": "trend",
            "label": "Current momentum",
            "value": direction,
            "round": overall_series[-1]["round"],
            "driver": overall_series[-1]["dominant_driver"],
        },
        {
            "type": "rise",
            "label": "Largest round gain",
            "value": biggest_rise["overall_delta"],
            "round": biggest_rise["round"],
            "driver": biggest_rise["dominant_driver"],
        },
        {
            "type": "drop",
            "label": "Largest round drop",
            "value": biggest_drop["overall_delta"],
            "round": biggest_drop["round"],
            "driver": biggest_drop["dominant_driver"],
        },
    ]


def build_dashboard_view(data: dict[str, Any]) -> dict[str, Any]:
    model_evidence = data.get("semantic_evidence", {}) if isinstance(data, dict) else {}
    simulation_result = {
        "trajectories": data.get("trajectories", []) if isinstance(data, dict) else [],
    }
    executive_summary = build_executive_summary(
        model_evidence=model_evidence,
        simulation_result=simulation_result,
    )
    decision_trace = build_decision_trace(
        model_evidence=model_evidence,
        simulation_result=simulation_result,
    )
    expanded_fallback = build_expanded_fallback_text(
        executive_summary=executive_summary,
        decision_trace=decision_trace,
    )

    overall_final = _safe_float(decision_trace.get("overall_final", 0.0))
    dispersion = _safe_float(decision_trace.get("dispersion", 0.0))

    four_block = executive_summary.get("four_block_summary", {})
    if not isinstance(four_block, dict):
        four_block = {}

    return {
        "executive_overview": {
            "overall_acceptance": overall_final,
            "polarization": str(four_block.get("polarization", "unknown")),
            "main_driver": str(four_block.get("main_driver", "N/A")),
            "risk_level": _risk_level(overall_final=overall_final, dispersion=dispersion),
            "conclusion_line": str(executive_summary.get("conclusion_line", "")),
            "headline": str(executive_summary.get("headline", "")),
        },
        "evidence_activation": build_evidence_activation(data=data),
        "evolution_highlights": build_evolution_highlights(data=data),
        "report_recommendation": {
            "executive_summary": executive_summary,
            "decision_trace": decision_trace,
            "expanded_analysis": expanded_fallback,
            "recommended_action": str(four_block.get("recommended_action", "")),
        },
    }
