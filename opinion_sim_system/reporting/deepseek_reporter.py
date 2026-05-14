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
from .report_builder import (
    build_decision_trace,
    build_executive_summary,
    build_expanded_fallback_text,
)


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

    def _build_prompt(
        self,
        model_evidence: dict[str, Any],
        simulation_result: dict[str, Any],
        executive_summary: dict[str, Any],
        decision_trace: dict[str, Any],
    ) -> str:
        reduced = {
            "experts": model_evidence.get("experts", {}),
            "fusion": model_evidence.get("fusion", {}),
            "final_round": (simulation_result.get("trajectories") or [{}])[-1],
            "input": simulation_result.get("input", {}),
            "executive_summary": executive_summary,
            "decision_trace": decision_trace,
        }
        return (
            "You are a concise analyst for executive briefings. Expand the deterministic summary and decision trace "
            "into 4-6 concrete sentences covering acceptance trend, conflict risk, polarization, and action guidance.\nJSON:\n"
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
        executive_summary = build_executive_summary(
            model_evidence=model_evidence,
            simulation_result=simulation_result,
        )
        decision_trace = build_decision_trace(
            model_evidence=model_evidence,
            simulation_result=simulation_result,
        )
        fallback = build_expanded_fallback_text(
            executive_summary=executive_summary,
            decision_trace=decision_trace,
        )

        if use_live:
            try:
                prompt = self._build_prompt(
                    model_evidence=model_evidence,
                    simulation_result=simulation_result,
                    executive_summary=executive_summary,
                    decision_trace=decision_trace,
                )
                text = self._call_deepseek(prompt=prompt, api_key=api_key)
                return {
                    "schema_version": PHASE2B_SCHEMA_VERSION,
                    "status": "ok",
                    "provider": self.provider,
                    "mode": "live",
                    "text": text,
                    "executive_summary": executive_summary,
                    "expanded_analysis": text,
                    "decision_trace": decision_trace,
                    "meta": {"model": self.model},
                    "errors": [],
                }
            except (RuntimeError, ValueError, json.JSONDecodeError, error.URLError, TimeoutError) as exc:
                return {
                    "schema_version": PHASE2B_SCHEMA_VERSION,
                    "status": "partial",
                    "provider": self.provider,
                    "mode": "fallback",
                    "text": fallback,
                    "executive_summary": executive_summary,
                    "expanded_analysis": fallback,
                    "decision_trace": decision_trace,
                    "meta": {"model": self.model},
                    "errors": [str(exc)],
                }

        return {
            "schema_version": PHASE2B_SCHEMA_VERSION,
            "status": "ok",
            "provider": self.provider,
            "mode": "fallback",
            "text": fallback,
            "executive_summary": executive_summary,
            "expanded_analysis": fallback,
            "decision_trace": decision_trace,
            "meta": {"model": self.model},
            "errors": [],
        }

    def generate(self, model_evidence: dict[str, Any], simulation_result: dict[str, Any]) -> str:
        """Backward-compatible text-only API."""
        report = self.generate_report(model_evidence=model_evidence, simulation_result=simulation_result)
        return str(report.get("text", ""))

    def expand_orchestrator_briefing(self, briefing_markdown: str) -> dict[str, Any]:
        """
        Optional narrative expansion for orchestrator Markdown briefings.

        Does not affect deterministic planning or MiroFish outputs. Uses DEEPSEEK_API_KEY when
        mode is auto|live and the key is present; otherwise returns skipped status.
        """
        api_key = self._resolve_api_key()
        if self.mode == "off" or not api_key:
            return {"status": "skipped", "text": "", "errors": []}
        if self.mode not in {"auto", "live"}:
            return {"status": "skipped", "text": "", "errors": []}
        try:
            prompt = (
                "You are an analyst. Given the following deterministic executive briefing (Markdown), "
                "write 4-6 crisp English sentences that elaborate key tensions and actionable watch-items. "
                "Do not contradict numeric facts stated in the briefing; add texture only.\n\n"
                + briefing_markdown
            )
            text = self._call_deepseek(prompt=prompt, api_key=api_key)
            return {"status": "ok", "text": text, "errors": []}
        except (RuntimeError, ValueError, json.JSONDecodeError, error.URLError, TimeoutError, OSError) as exc:
            return {"status": "error", "text": "", "errors": [str(exc)]}
