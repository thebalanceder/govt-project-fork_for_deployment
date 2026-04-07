from ..flask_app import app


def test_briefing_run_returns_phase3_view_layers() -> None:
    client = app.test_client()

    response = client.post(
        "/api/briefing-run",
        json={
            "text": "A policy proposal focused on fairness and service quality.",
            "target": "city service policy",
            "domain": "policy",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload is not None
    assert payload.get("success") is True

    assert "simulation_result" in payload
    simulation_result = payload["simulation_result"]
    assert set(simulation_result.keys()) >= {
        "overall_final",
        "dispersion",
        "top_groups",
        "final_group_attitudes",
        "rounds",
        "visualization_payload",
    }

    assert set(payload.keys()) >= {
        "executive_overview",
        "evidence_activation",
        "evolution_highlights",
        "report_recommendation",
    }

    semantic_evidence = payload.get("semantic_evidence", {})
    assert "fusion" in semantic_evidence
    assert "consensus" in semantic_evidence["fusion"]

    overview = payload["executive_overview"]
    assert set(overview.keys()) >= {
        "overall_acceptance",
        "polarization",
        "main_driver",
        "risk_level",
        "conclusion_line",
    }
