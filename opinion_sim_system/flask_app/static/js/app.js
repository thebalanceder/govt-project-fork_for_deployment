const API_BASE = "";

const EXPERT_ORDER = [
  { key: "acceptance", title: "Acceptance", hint: "Target acceptance tendency" },
  { key: "sentiment", title: "Sentiment", hint: "Overall positive/negative polarity" },
  { key: "emotion", title: "Emotion", hint: "Affective profile intensity" },
  { key: "topic", title: "Topic", hint: "Dominant semantic topic" },
  { key: "conflict", title: "Conflict", hint: "Social conflict risk" },
  { key: "frame", title: "Frame", hint: "Dominant value/policy frame" },
];

const FALLBACK_BACKENDS = new Set(["lexicon", "keyword", "fallback", "heuristic"]);
const PIPELINE_STEPS = ["input", "semantic", "activation", "simulation", "report"];

const uiState = {
  running: false,
  cards: {},
  revealTimers: [],
};

function announceStatus(message) {
  const node = document.getElementById("live-status");
  if (node) {
    node.textContent = message;
  }
}

function setPipelineStep(activeStep) {
  document.querySelectorAll(".pipeline-step").forEach((element) => {
    const step = element.dataset.step;
    element.classList.toggle("active", step === activeStep);
    if (PIPELINE_STEPS.indexOf(step) < PIPELINE_STEPS.indexOf(activeStep)) {
      element.classList.add("done");
    }
    if (step === activeStep) {
      element.setAttribute("aria-current", "true");
    } else {
      element.removeAttribute("aria-current");
    }
  });
}

function resetPipeline() {
  setPipelineStep("input");
}

function initSemanticCards() {
  const container = document.getElementById("semantic-cards");
  if (!container) return;

  container.innerHTML = "";
  uiState.cards = {};

  for (const expert of EXPERT_ORDER) {
    const card = document.createElement("article");
    card.className = "evidence-card status-waiting";
    card.id = `card-${expert.key}`;
    card.innerHTML = `
      <div class="card-head">
        <h3>${expert.title}</h3>
        <span class="status-pill">waiting</span>
      </div>
      <p class="card-hint">${expert.hint}</p>
      <div class="card-result">Waiting for pipeline slot...</div>
    `;
    container.appendChild(card);
    uiState.cards[expert.key] = card;
  }
}

function updateCardStatus(key, status, text) {
  const card = uiState.cards[key];
  if (!card) return;
  card.classList.remove("status-waiting", "status-running", "status-completed", "status-fallback", "status-failed");
  card.classList.add(`status-${status}`);
  const pill = card.querySelector(".status-pill");
  const result = card.querySelector(".card-result");
  if (pill) pill.textContent = status;
  if (result && text) result.textContent = text;
}

function scheduleProgressiveCardStart() {
  clearProgressTimers();
  EXPERT_ORDER.forEach((expert, index) => {
    const timer = window.setTimeout(() => {
      if (uiState.running) {
        updateCardStatus(expert.key, "running", "Running semantic inference...");
      }
    }, 450 * index);
    uiState.revealTimers.push(timer);
  });
}

function clearProgressTimers() {
  for (const timer of uiState.revealTimers) {
    window.clearTimeout(timer);
  }
  uiState.revealTimers = [];
}

function safeNumber(value, fallback = 0) {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string") {
    const parsed = Number.parseFloat(value);
    if (Number.isFinite(parsed)) return parsed;
  }
  return fallback;
}

function formatExpertText(entry) {
  const label = entry?.label ?? "N/A";
  const score = safeNumber(entry?.score, 0);
  const confidence = safeNumber(entry?.confidence, 0);
  return `${label} · score ${score.toFixed(2)} · confidence ${confidence.toFixed(2)}`;
}

function renderSemanticEvidence(evidence) {
  const experts = evidence?.experts ?? {};
  for (const spec of EXPERT_ORDER) {
    const entry = experts[spec.key];
    if (!entry) {
      updateCardStatus(spec.key, "failed", "No result returned from backend.");
      continue;
    }
    const backend = String(entry?.payload?.backend ?? "").toLowerCase();
    const status = FALLBACK_BACKENDS.has(backend) ? "fallback" : "completed";
    updateCardStatus(spec.key, status, formatExpertText(entry));
  }
}

function computeActivationGroups(evidence, initialAttitudes) {
  const experts = evidence?.experts ?? {};
  const acceptance = safeNumber(experts?.acceptance?.score, 0.5);
  const conflict = safeNumber(experts?.conflict?.score, 0.5);
  const frameLabel = String(experts?.frame?.label ?? "general").toLowerCase();

  const reasons = [];
  if (acceptance >= 0.65) reasons.push("high acceptance signal");
  if (acceptance <= 0.35) reasons.push("low acceptance signal");
  if (conflict >= 0.6) reasons.push("elevated conflict risk");
  if (frameLabel.includes("econom") || frameLabel.includes("cost")) reasons.push("economic/value frame");
  if (frameLabel.includes("identity") || frameLabel.includes("culture")) reasons.push("social identity frame");

  const groups = Object.entries(initialAttitudes ?? {}).map(([group, attitude]) => {
    let impact = 0;
    if (group.includes("risk") || group.includes("social")) impact += conflict;
    if (group.includes("budget") || group.includes("rational")) impact += 1 - Math.abs(acceptance - 0.5);
    if (group.includes("culture") || group.includes("emotion")) impact += frameLabel.includes("culture") ? 0.8 : 0.3;
    impact += safeNumber(attitude, 0.5);
    return {
      group,
      attitude: safeNumber(attitude, 0.5),
      impact,
      reason: reasons[0] || "core semantic evidence available",
    };
  });

  groups.sort((a, b) => b.impact - a.impact);
  return groups.slice(0, 6);
}

function renderActivation(groups) {
  const container = document.getElementById("group-activation");
  if (!container) return;
  container.innerHTML = "";

  groups.forEach((group, index) => {
    const card = document.createElement("article");
    card.className = "group-card pending";
    card.innerHTML = `
      <div class="group-title">${group.group}</div>
      <div class="group-meta">Initial attitude: ${group.attitude.toFixed(2)}</div>
      <div class="group-reason">Reason: ${group.reason}</div>
    `;
    container.appendChild(card);

    const timer = window.setTimeout(() => {
      card.classList.remove("pending");
      card.classList.add("active");
    }, 220 * index);
    uiState.revealTimers.push(timer);
  });
}

function renderEvidenceLinks(links) {
  const container = document.getElementById("evidence-links");
  if (!container) return;

  const data = Array.isArray(links) ? links : [];
  if (!data.length) {
    container.innerHTML = '<div class="empty-hint">No evidence links available.</div>';
    return;
  }

  const rows = data.slice(0, 12).map((item) => {
    const source = String(item?.source ?? "N/A");
    const label = String(item?.source_label ?? "");
    const target = String(item?.target ?? "N/A");
    const weight = safeNumber(item?.weight, 0);
    const delta = safeNumber(item?.delta_magnitude, 0);
    return `
      <tr>
        <td>${source}</td>
        <td>${label}</td>
        <td>${target}</td>
        <td>${weight.toFixed(4)}</td>
        <td>${delta.toFixed(3)}</td>
      </tr>
    `;
  }).join("");

  container.innerHTML = `
    <table class="links-table">
      <thead>
        <tr>
          <th>Signal</th>
          <th>Label</th>
          <th>Group</th>
          <th>Weight</th>
          <th>Δ Magnitude</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderExecutiveOverview(overview, simulationResult) {
  const container = document.getElementById("executive-overview-cards");
  if (!container) return;

  const data = overview ?? {};
  const overall = safeNumber(data?.overall_acceptance, safeNumber(simulationResult?.overall_final, 0));
  const polarization = String(data?.polarization ?? "unknown");
  const mainDriver = String(data?.main_driver ?? "N/A");
  const riskLevel = String(data?.risk_level ?? "unknown").toUpperCase();

  container.innerHTML = `
    <article class="overview-card">
      <span class="overview-label">Overall Acceptance</span>
      <strong>${overall.toFixed(2)}</strong>
    </article>
    <article class="overview-card">
      <span class="overview-label">Polarization</span>
      <strong>${polarization}</strong>
    </article>
    <article class="overview-card">
      <span class="overview-label">Main Driver</span>
      <strong>${mainDriver}</strong>
    </article>
    <article class="overview-card">
      <span class="overview-label">Risk Level</span>
      <strong>${riskLevel}</strong>
    </article>
  `;
}

function deriveHighlightsFromTrajectories(trajectories) {
  const rounds = Array.isArray(trajectories) ? trajectories : [];
  if (!rounds.length) return [];

  const series = rounds.map((item, index) => ({
    round: safeNumber(item?.round, index + 1),
    overall: safeNumber(item?.overall_satisfaction, 0),
    delta: safeNumber(item?.overall_delta, 0),
    driver: String(item?.dominant_driver ?? "N/A"),
  }));

  const biggestRise = [...series].sort((a, b) => b.delta - a.delta)[0];
  const biggestDrop = [...series].sort((a, b) => a.delta - b.delta)[0];
  const trend = series.length >= 2
    ? (series[series.length - 1].overall - series[series.length - 2].overall > 0.02 ? "rising"
      : series[series.length - 1].overall - series[series.length - 2].overall < -0.02 ? "falling"
        : "stable")
    : "stable";

  return [
    { label: "Current momentum", value: trend, round: series[series.length - 1].round, driver: series[series.length - 1].driver },
    { label: "Largest round gain", value: biggestRise.delta.toFixed(3), round: biggestRise.round, driver: biggestRise.driver },
    { label: "Largest round drop", value: biggestDrop.delta.toFixed(3), round: biggestDrop.round, driver: biggestDrop.driver },
  ];
}

function renderEvolutionHighlights(highlights, trajectories) {
  const container = document.getElementById("evolution-highlights");
  if (!container) return;

  let data = Array.isArray(highlights) ? highlights : [];
  if (!data.length) data = deriveHighlightsFromTrajectories(trajectories);

  if (!data.length) {
    container.innerHTML = '<div class="empty-hint">No evolution highlights available.</div>';
    return;
  }

  container.innerHTML = data.slice(0, 4).map((item) => `
    <article class="highlight-card">
      <span class="highlight-label">${String(item?.label ?? "Highlight")}</span>
      <strong>${String(item?.value ?? "N/A")}</strong>
      <small>Round ${safeNumber(item?.round, 0)} · Driver: ${String(item?.driver ?? "N/A")}</small>
    </article>
  `).join("");
}

function buildExportText(reportRecommendation, report, reportText, conclusionLine) {
  const summary = reportRecommendation?.executive_summary ?? {};
  const blocks = summary?.four_block_summary ?? {};
  const expanded = String(reportRecommendation?.expanded_analysis ?? report?.expanded_analysis ?? reportText ?? "").trim();

  const lines = [
    "# Executive Report",
    String(summary?.headline ?? ""),
    String(summary?.conclusion_line ?? conclusionLine ?? ""),
    "",
    "## Four-Block Summary",
    `- Acceptance Outlook: ${String(blocks?.acceptance_outlook ?? "N/A")}`,
    `- Polarization: ${String(blocks?.polarization ?? "N/A")}`,
    `- Main Driver: ${String(blocks?.main_driver ?? "N/A")}`,
    `- Recommended Action: ${String(blocks?.recommended_action ?? "N/A")}`,
  ];

  if (expanded) {
    lines.push("", "## Expanded Analysis", expanded);
  }
  return lines.filter((line) => line !== "").join("\n");
}

function wireExportButton(exportText) {
  const button = document.getElementById("export-report-btn");
  if (!button) return;
  button.disabled = !exportText;

  button.onclick = null;
  if (!exportText) return;

  button.onclick = () => {
    const blob = new Blob([exportText], { type: "text/plain;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "executive_report.txt";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(link.href);
  };
}

function renderStructuredReport(reportRecommendation, report, reportText, conclusionLine) {
  const container = document.getElementById("report-structured");
  if (!container) return;

  const summary = reportRecommendation?.executive_summary ?? {};
  const blocks = summary?.four_block_summary ?? {};
  const action = String(reportRecommendation?.recommended_action ?? blocks?.recommended_action ?? "N/A");

  container.innerHTML = `
    <div class="structured-grid">
      <div><span>Acceptance Outlook</span><strong>${String(blocks?.acceptance_outlook ?? "N/A")}</strong></div>
      <div><span>Polarization</span><strong>${String(blocks?.polarization ?? "N/A")}</strong></div>
      <div><span>Main Driver</span><strong>${String(blocks?.main_driver ?? "N/A")}</strong></div>
      <div><span>Recommended Action</span><strong>${action}</strong></div>
    </div>
  `;

  const exportText = buildExportText(reportRecommendation, report, reportText, conclusionLine);
  wireExportButton(exportText);
}

function renderSimulationSummary(simulationResult) {
  const summary = document.getElementById("simulation-summary");
  if (!summary) return;
  const overall = safeNumber(simulationResult?.overall_final, 0);
  const dispersion = safeNumber(simulationResult?.dispersion, 0);
  const topGroups = simulationResult?.top_groups ?? [];
  summary.innerHTML = `
    <div class="metric">
      <span class="metric-label">Overall Acceptance</span>
      <span class="metric-value">${overall.toFixed(2)}</span>
    </div>
    <div class="metric">
      <span class="metric-label">Dispersion</span>
      <span class="metric-value">${dispersion.toFixed(2)}</span>
    </div>
    <div class="metric-list">
      <span class="metric-label">Top Groups</span>
      <ul>
        ${topGroups.map((item) => `<li>${item.group}: ${safeNumber(item.attitude, 0).toFixed(2)}</li>`).join("")}
      </ul>
    </div>
  `;
}

function renderTrendChart(trajectories) {
  const svg = d3.select("#trend-chart");
  if (svg.empty()) return;

  const node = svg.node();
  const width = node.clientWidth || 640;
  const height = node.clientHeight || 220;
  svg.attr("viewBox", `0 0 ${width} ${height}`);
  svg.selectAll("*").remove();

  const data = (trajectories ?? []).map((item) => ({
    round: safeNumber(item.round, 0),
    value: safeNumber(item.overall_satisfaction, 0),
  }));
  if (!data.length) return;

  const x = d3.scaleLinear().domain(d3.extent(data, (d) => d.round)).range([48, width - 20]);
  const y = d3.scaleLinear().domain([0, 1]).range([height - 32, 18]);

  const line = d3.line().x((d) => x(d.round)).y((d) => y(d.value));

  svg.append("path")
    .datum(data)
    .attr("fill", "none")
    .attr("stroke", "#3b82f6")
    .attr("stroke-width", 3)
    .attr("d", line);

  svg.selectAll("circle")
    .data(data)
    .enter()
    .append("circle")
    .attr("cx", (d) => x(d.round))
    .attr("cy", (d) => y(d.value))
    .attr("r", 4)
    .attr("fill", "#0f172a");

  svg.append("g")
    .attr("transform", `translate(0, ${height - 32})`)
    .call(d3.axisBottom(x).ticks(data.length).tickFormat(d3.format("d")));
  svg.append("g")
    .attr("transform", "translate(48, 0)")
    .call(d3.axisLeft(y).ticks(5));
}

function renderNetwork(trajectories) {
  const finalRound = (trajectories ?? []).at(-1);
  const attitudes = finalRound?.group_attitudes ?? {};
  const groups = Object.keys(attitudes);
  const svg = d3.select("#simulation-network");
  if (svg.empty()) return;

  const node = svg.node();
  const width = node.clientWidth || 640;
  const height = node.clientHeight || 360;
  svg.attr("viewBox", `0 0 ${width} ${height}`);
  svg.selectAll("*").remove();

  if (!groups.length) return;

  const nodes = groups.map((group) => ({ id: group, attitude: safeNumber(attitudes[group], 0.5) }));
  const links = [];
  for (let i = 0; i < nodes.length; i += 1) {
    for (let j = i + 1; j < nodes.length; j += 1) {
      links.push({ source: nodes[i].id, target: nodes[j].id });
    }
  }

  const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id((d) => d.id).distance(140).strength(0.15))
    .force("charge", d3.forceManyBody().strength(-260))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .stop();

  for (let i = 0; i < 120; i += 1) simulation.tick();

  svg.append("g")
    .selectAll("line")
    .data(links)
    .enter()
    .append("line")
    .attr("x1", (d) => d.source.x)
    .attr("y1", (d) => d.source.y)
    .attr("x2", (d) => d.target.x)
    .attr("y2", (d) => d.target.y)
    .attr("stroke", "#94a3b8")
    .attr("stroke-opacity", 0.45);

  const nodeGroup = svg.append("g")
    .selectAll("g")
    .data(nodes)
    .enter()
    .append("g")
    .attr("transform", (d) => `translate(${d.x},${d.y})`);

  nodeGroup.append("circle")
    .attr("r", 26)
    .attr("fill", (d) => d3.interpolateBlues(0.35 + d.attitude * 0.55))
    .attr("stroke", "#0f172a")
    .attr("stroke-width", 1.5);

  nodeGroup.append("text")
    .text((d) => d.id.replaceAll("_", " "))
    .attr("text-anchor", "middle")
    .attr("dy", -34)
    .attr("font-size", 11)
    .attr("fill", "#0f172a");

  nodeGroup.append("text")
    .text((d) => d.attitude.toFixed(2))
    .attr("text-anchor", "middle")
    .attr("dy", 4)
    .attr("font-size", 11)
    .attr("font-weight", 700)
    .attr("fill", "#0f172a");
}

function renderRoundTimeline(trajectories) {
  const container = document.getElementById("round-timeline");
  if (!container) return;
  container.innerHTML = (trajectories ?? [])
    .map((item) => {
      const round = safeNumber(item.round, 0);
      const overall = safeNumber(item.overall_satisfaction, 0);
      return `<div class="timeline-item"><span>Round ${round}</span><strong>${overall.toFixed(2)}</strong></div>`;
    })
    .join("");
}

function renderReport(report, reportText) {
  const meta = document.getElementById("report-meta");
  const text = document.getElementById("report-text");
  if (meta) {
    const errors = Array.isArray(report?.errors) ? report.errors : [];
    meta.innerHTML = `
      <span>Status: ${report?.status ?? "unknown"}</span>
      <span>Provider: ${report?.provider ?? "deepseek"}</span>
      <span>Mode: ${report?.mode ?? "fallback"}</span>
      ${errors.length ? `<span class="report-error">Errors: ${errors[0]}</span>` : ""}
    `;
  }
  if (text) {
    text.textContent = reportText || "No report content returned.";
  }
}

function renderConvergence(convergence) {
  const node = document.getElementById("report-convergence");
  if (!node) return;
  const alignment = String(convergence?.alignment ?? "unknown");
  const dispersion = safeNumber(convergence?.dispersion, 0);
  const trend = String(convergence?.trend ?? "unknown");
  node.innerHTML = `
    <strong>Convergence</strong> · alignment: ${alignment} · dispersion: ${dispersion.toFixed(2)} · trend: ${trend}
  `;
}

function updateTopBars(payload) {
  const conclusion = document.getElementById("conclusion-line");
  const trust = document.getElementById("trust-bar");
  if (conclusion) {
    conclusion.textContent = payload?.conclusion_line ?? "Conclusion unavailable.";
  }
  if (trust) {
    const trustData = payload?.trust ?? {};
    trust.innerHTML = `
      <span>Engine: ${trustData.engine_version ?? "--"}</span>
      <span>Report Mode: ${trustData.report_mode ?? "--"}</span>
      <span>Updated: ${trustData.generated_at ?? "--"}</span>
    `;
  }
}

async function runBriefing(event) {
  event.preventDefault();
  if (uiState.running) return;

  const text = document.getElementById("case-text")?.value.trim() ?? "";
  const target = document.getElementById("case-target")?.value.trim() ?? "";
  const domain = document.getElementById("case-domain")?.value ?? "policy";
  if (!text || !target) {
    announceStatus("Input is incomplete. Please provide case text and target.");
    return;
  }

  const runBtn = document.getElementById("run-btn");
  if (runBtn) {
    runBtn.disabled = true;
    runBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running...';
  }

  uiState.running = true;
  setPipelineStep("semantic");
  initSemanticCards();
  scheduleProgressiveCardStart();
  announceStatus("Semantic experts started. Rendering progressive evidence cards.");

  try {
    const response = await fetch(`${API_BASE}/api/briefing-run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, target, domain }),
    });

    const payload = await response.json();
    if (!response.ok || !payload?.success) {
      throw new Error(payload?.error || "Pipeline execution failed.");
    }

    clearProgressTimers();
    renderSemanticEvidence(payload.semantic_evidence);

    setPipelineStep("activation");
    announceStatus("Semantic evidence completed. Activating groups.");
    const groups = computeActivationGroups(
      payload.semantic_evidence,
      payload.simulation_result?.initial_attitudes,
    );
    renderActivation(groups);
    renderEvidenceLinks(payload.evidence_activation);

    setPipelineStep("simulation");
    announceStatus("Group activation complete. Rendering simulation evolution.");
    renderExecutiveOverview(payload.executive_overview, payload.simulation_result);
    renderSimulationSummary(payload.simulation_result);
    renderTrendChart(payload.simulation_result?.trajectories ?? []);
    renderNetwork(payload.simulation_result?.trajectories ?? []);
    renderEvolutionHighlights(payload.evolution_highlights, payload.simulation_result?.trajectories ?? []);
    renderRoundTimeline(payload.simulation_result?.trajectories ?? []);

    setPipelineStep("report");
    announceStatus("Simulation completed, generating report.");
    renderStructuredReport(
      payload.report_recommendation,
      payload.report,
      payload.report_text,
      payload.conclusion_line,
    );
    renderReport(payload.report, payload.report_text);
    renderConvergence(payload.convergence);
    updateTopBars(payload);
    announceStatus("Report completed. Briefing output is ready for presentation.");
  } catch (error) {
    clearProgressTimers();
    announceStatus(`Pipeline failed: ${error.message}`);
    for (const spec of EXPERT_ORDER) {
      updateCardStatus(spec.key, "failed", "Failed to retrieve semantic result.");
    }
  } finally {
    uiState.running = false;
    if (runBtn) {
      runBtn.disabled = false;
      runBtn.innerHTML = '<i class="fas fa-play"></i> Start Analysis';
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initSemanticCards();
  resetPipeline();
  document.getElementById("briefing-form")?.addEventListener("submit", runBriefing);
});
