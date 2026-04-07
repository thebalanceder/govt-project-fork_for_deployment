def test_import_deepseek_reporter_without_circular_import() -> None:
    from ..reporting.deepseek_reporter import DeepSeekReporter

    reporter = DeepSeekReporter(mode="fallback")
    assert reporter.provider == "deepseek"
