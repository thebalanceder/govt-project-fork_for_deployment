from ..reporting.report_builder import build_dashboard_view, build_evidence_activation


def test_build_dashboard_view_with_enhanced_payload() -> None:
    data = {
        "semantic_evidence": {
            "experts": {
                "acceptance": {"label": "ACCEPT", "score": 0.82},
                "conflict": {"label": "LOW_CONFLICT", "score": 0.24},
                "frame": {"label": "fairness", "score": 0.71},
                "sentiment": {"label": "POSITIVE", "score": 0.65},
            }
        },
        "trajectories": [
            {
                "round": 1,
                "group_attitudes": {"cost": 0.51, "risk": 0.42},
                "overall_satisfaction": 0.46,
                "overall_delta": 0.00,
                "dominant_driver": "acceptance",
            },
            {
                "round": 2,
                "group_attitudes": {"cost": 0.58, "risk": 0.40},
                "overall_satisfaction": 0.49,
                "overall_delta": 0.03,
                "dominant_driver": "frame",
            },
        ],
        "visualization_payload": {
            "rounds": [
                {
                    "round": 2,
                    "delta_by_group": {"cost": 0.07, "risk": -0.02},
                    "activation_reasons": [
                        {"expert": "frame", "label": "fairness", "weight": 0.66},
                        {"expert": "acceptance", "label": "ACCEPT", "weight": 0.40},
                    ],
                }
            ]
        },
    }

    view = build_dashboard_view(data)

    overview = view["executive_overview"]
    assert set(overview.keys()) >= {
        "overall_acceptance",
        "polarization",
        "main_driver",
        "risk_level",
        "conclusion_line",
    }

    assert isinstance(view["evidence_activation"], list)
    assert view["evidence_activation"]
    assert isinstance(view["evolution_highlights"], list)
    assert len(view["evolution_highlights"]) == 3

    report = view["report_recommendation"]
    assert "recommended_action" in report
    assert "expanded_analysis" in report


def test_build_evidence_activation_has_legacy_fallback() -> None:
    data = {
        "semantic_evidence": {
            "experts": {
                "acceptance": {"label": "ACCEPT", "score": 0.8},
                "conflict": {"label": "LOW_CONFLICT", "score": 0.3},
                "frame": {"label": "fairness", "score": 0.5},
            }
        },
        "trajectories": [
            {
                "round": 1,
                "group_attitudes": {"cost": 0.52, "risk": 0.33},
                "overall_satisfaction": 0.42,
            }
        ],
    }

    links = build_evidence_activation(data)
    assert links
    assert {item["source"] for item in links}.issubset({"acceptance", "conflict", "frame"})
