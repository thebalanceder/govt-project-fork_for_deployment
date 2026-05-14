"""Prompt templates for expert research briefings (pre-MiroFish layer)."""

from __future__ import annotations

RESEARCH_REPORT_PROMPT = """{prompt_role}.

You are writing a concise **expert research briefing** for the chief briefing coordinator (Dr. Helena Marlowe).
Base your briefing only on the **case text** and **available evidence** below. Your domain focus: **{research_focus}**.

---

### Case and evidence pack

{case_and_evidence}

---

### Required output structure

Use exactly these section headings (Markdown):

## 1. Key judgment
## 2. Supporting evidence
## 3. Risks and uncertainties
## 4. What the chief coordinator should watch
## 5. One-sentence recommendation

### Rules
- Do **not** invent facts that are not supported by the evidence pack. If the evidence is insufficient for a claim, say so explicitly in section 2 or 3.
- Keep tone professional, concise, and decision-oriented.
- Stay strictly within your domain focus; do not impersonate other experts’ specialties.
- If evidence is empty or extremely thin, state that the brief is **evidence-limited** and rely on clearly labeled conditional judgments.
"""
