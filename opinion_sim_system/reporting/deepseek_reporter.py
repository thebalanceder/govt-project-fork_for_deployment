"""DeepSeek reporting placeholder for Phase2A demos.

This module intentionally does not call any external API in-repo.
It provides a deterministic text summary interface so downstream callers
can later swap in real DeepSeek integration without changing call sites.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Any
from urllib import error, request

from ..demo.contracts import PHASE2B_SCHEMA_VERSION


@dataclass(slots=True)
class DeepSeekReporter:
    provider: str = "deepseek"
    mode: str = "auto"
    model: str = "deepseek-chat"
    api_base: str = "https://api.deepseek.com/v1"
    api_key: str | None = None
    timeout_seconds: float = 20.0

    def _resolve_api_key(self) -> str:
        if self.api_key:
            return self.api_key
        env_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        return env_key

    def _fallback_text(self, model_evidence: dict[str, Any], simulation_result: dict[str, Any]) -> str:
        experts = model_evidence.get("experts", {}) if isinstance(model_evidence, dict) else {}
        acceptance = experts.get("acceptance", {}) if isinstance(experts, dict) else {}
        conflict = experts.get("conflict", {}) if isinstance(experts, dict) else {}
        frame = experts.get("frame", {}) if isinstance(experts, dict) else {}

        trajectories = simulation_result.get("trajectories", []) if isinstance(simulation_result, dict) else []
        final_overall = trajectories[-1].get("overall_satisfaction", 0.0) if trajectories else 0.0

        return (
            "[DeepSeek fallback] "
            f"acceptance={acceptance.get('label', 'N/A')}, "
            f"conflict={conflict.get('label', 'N/A')}, "
            f"frame={frame.get('label', 'N/A')}, "
            f"final_overall={float(final_overall):.3f}."
        )

    def _build_prompt(self, model_evidence: dict[str, Any], simulation_result: dict[str, Any]) -> str:
        reduced = {
            "experts": model_evidence.get("experts", {}),
            "fusion": model_evidence.get("fusion", {}),
            "final_round": (simulation_result.get("trajectories") or [{}])[-1],
            "input": simulation_result.get("input", {}),
        }
        return (
            "You are a concise analyst. Based on the JSON evidence, explain acceptance trend, conflict risk, "
            "and group divergence in 3-5 sentences.\nJSON:\n"
            + json.dumps(reduced, ensure_ascii=False)
        )

    def _call_deepseek(self, prompt: str, api_key: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You explain simulation outputs clearly and concretely."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            url=f"{self.api_base.rstrip('/')}/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with request.urlopen(req, timeout=self.timeout_seconds) as response:
            content = response.read().decode("utf-8")
        parsed = json.loads(content)
        choices = parsed.get("choices", [])
        if not choices:
            raise RuntimeError("DeepSeek response missing choices")
        message = choices[0].get("message", {})
        text = str(message.get("content", "")).strip()
        if not text:
            raise RuntimeError("DeepSeek response content is empty")
        return text

    def generate_report(self, model_evidence: dict[str, Any], simulation_result: dict[str, Any]) -> dict[str, Any]:
        """Structured report envelope for Phase2B demo contract."""
        api_key = self._resolve_api_key()
        use_live = self.mode in {"auto", "live"} and bool(api_key)

        if use_live:
            try:
                prompt = self._build_prompt(model_evidence=model_evidence, simulation_result=simulation_result)
                text = self._call_deepseek(prompt=prompt, api_key=api_key)
                return {
                    "schema_version": PHASE2B_SCHEMA_VERSION,
                    "status": "ok",
                    "provider": self.provider,
                    "mode": "live",
                    "text": text,
                    "meta": {"model": self.model},
                    "errors": [],
                }
            except (RuntimeError, ValueError, json.JSONDecodeError, error.URLError, TimeoutError) as exc:
                fallback = self._fallback_text(model_evidence=model_evidence, simulation_result=simulation_result)
                return {
                    "schema_version": PHASE2B_SCHEMA_VERSION,
                    "status": "partial",
                    "provider": self.provider,
                    "mode": "fallback",
                    "text": fallback,
                    "meta": {"model": self.model},
                    "errors": [str(exc)],
                }

        fallback = self._fallback_text(model_evidence=model_evidence, simulation_result=simulation_result)
        return {
            "schema_version": PHASE2B_SCHEMA_VERSION,
            "status": "ok",
            "provider": self.provider,
            "mode": "fallback",
            "text": fallback,
            "meta": {"model": self.model},
            "errors": [],
        }

    def generate(self, model_evidence: dict[str, Any], simulation_result: dict[str, Any]) -> str:
        """Backward-compatible text-only API."""
        report = self.generate_report(model_evidence=model_evidence, simulation_result=simulation_result)
        return str(report.get("text", ""))
