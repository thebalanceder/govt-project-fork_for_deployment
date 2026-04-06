from ..visualization.briefing_report import generate_html_report


def test_generate_html_report_handles_missing_sentiment_signal() -> None:
    data = {
        "input": {
            "product_description": "policy briefing sample",
            "n_comments": 3,
        },
        "initial_attitudes": {
            "group_a": 0.4,
            "group_b": 0.5,
        },
        "trajectories": [
            {
                "round": 1,
                "group_attitudes": {"group_a": 0.45, "group_b": 0.52},
                "overall_satisfaction": 0.485,
                "topic_distribution": {"topic_0": 1.0},
            }
        ],
        "semantic_summary": {
            "topic_distribution": {"topic_0": 1.0},
            "topic_words": {"topic_0": ["policy", "fairness"]},
            # sentiment_signal intentionally omitted
        },
    }

    html = generate_html_report(data)

    assert isinstance(html, str)
    assert "Sentiment Signal" in html
    assert "N/A" in html
