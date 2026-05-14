from __future__ import annotations

from ..orchestrator.planner import build_task_graph


def test_planner_defaults_all_topics() -> None:
    g = build_task_graph({"data": {}})
    assert g.topics == ["economic", "political", "cultural"]
    ids = [n.task_id for n in g.nodes]
    assert "mirofish_discussion_economic" in ids
    assert "mirofish_discussion_political" in ids
    assert "mirofish_discussion_cultural" in ids


def test_planner_single_topic() -> None:
    g = build_task_graph({"topics": ["political"], "data": {}})
    assert g.topics == ["political"]
    assert [n for n in g.nodes if n.task_type == "mirofish_discussion"][0].topic == "political"


def test_planner_topic_alias() -> None:
    g = build_task_graph({"topic": "cultural", "data": {}})
    assert g.topics == ["cultural"]
