(function () {
  const SURFACE = "#16161a";

  function taskAt(hourly, h) {
    if (!hourly || !hourly.length) return h < 14 ? 1 : 0;
    return hourly[h] ?? 0;
  }

  function applyLatestMeta(latest, failure) {
    const badge = document.getElementById("run-badge");
    if (badge && latest?.run_id) {
      badge.textContent = `Live data · ${latest.run_id}`;
    }
    const tasksEl = document.getElementById("stat-tasks");
    if (tasksEl && failure?.tasks_total != null) {
      tasksEl.textContent = String(failure.tasks_total);
    }
    const verdictEl = document.getElementById("stat-verdict");
    if (verdictEl && failure?.verdict) {
      verdictEl.textContent = failure.verdict.toUpperCase();
      verdictEl.style.color = failure.verdict === "block" ? "var(--danger)" : "var(--ok)";
    }
  }

  function buildModes(failure, golden) {
    const total = failure?.duration_hours ?? 72;
    return {
      failure: {
        hint: `Relay-3 goes offline at hour ${failure?.failure_hour ?? 14}. Entity updates stop. Investigate tasks block.`,
        failureHour: failure?.failure_hour ?? 14,
        meshStatus: `T+${failure?.failure_hour ?? 14}H · RELAY-3 OFFLINE`,
        hourly: failure?.hourly_investigate_tasks,
        total,
      },
      golden: {
        hint: `All three nodes stay online. ${golden?.tasks_total ?? 73} Investigate tasks over ${golden?.duration_hours ?? 72}h.`,
        failureHour: null,
        meshStatus: "T+72H · ALL NODES HEALTHY",
        hourly: golden?.hourly_investigate_tasks,
        total: golden?.duration_hours ?? 72,
      },
    };
  }

  function drawTimeline(canvas, cfg) {
    const failureHour = cfg.failureHour;
    const total = cfg.total;
    const hourly = cfg.hourly;
    const maxTasks = Math.max(1, ...(hourly || [1]));

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = 260 * dpr;
    const ctx = canvas.getContext("2d");
    ctx.scale(dpr, dpr);
    const w = rect.width;
    const h = 260;
    const pad = { l: 44, r: 16, t: 20, b: 36 };
    const plotW = w - pad.l - pad.r;
    const plotH = h - pad.t - pad.b;

    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = SURFACE;
    ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = "#8b909a";
    ctx.font = "11px IBM Plex Mono, monospace";
    ctx.fillText("Tasks/hr", 4, pad.t + 8);

    ctx.strokeStyle = "rgba(237,234,233,0.08)";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
      const y = pad.t + (plotH * i) / 4;
      ctx.beginPath();
      ctx.moveTo(pad.l, y);
      ctx.lineTo(w - pad.r, y);
      ctx.stroke();
    }

    if (failureHour != null) {
      const fx = pad.l + (failureHour / total) * plotW;
      ctx.fillStyle = "rgba(240,84,74,0.08)";
      ctx.fillRect(fx, pad.t, w - pad.r - fx, plotH);
      ctx.strokeStyle = "rgba(240,84,74,0.5)";
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(fx, pad.t);
      ctx.lineTo(fx, pad.t + plotH);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = "#f0544a";
      ctx.font = "10px Inter, sans-serif";
      ctx.fillText("Relay dies", fx + 6, pad.t + 14);
    }

    ctx.beginPath();
    for (let hr = 0; hr <= total; hr++) {
      const tasks = taskAt(hourly, hr);
      const x = pad.l + (hr / total) * plotW;
      const y = pad.t + plotH - (tasks / (maxTasks * 1.2)) * plotH;
      if (hr === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.strokeStyle = failureHour != null ? "#6eb5ff" : "#3ec97a";
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.fillStyle = "#8b909a";
    ctx.font = "10px IBM Plex Mono, monospace";
    [0, 24, 48, 72].forEach((hr) => {
      const x = pad.l + (hr / total) * plotW;
      ctx.fillText("T+" + hr, x - 8, h - 10);
    });
  }

  function renderMesh(container, failureHour, hour, offlineNode) {
    const relayDead = failureHour != null && hour >= failureHour;
    const color = (ok) => (ok ? "#3ec97a" : "#f0544a");
    const stroke = (ok) => (ok ? "rgba(62,201,122,0.4)" : "rgba(240,84,74,0.4)");
    const relayOk = !relayDead;
    const uavOk = !relayDead;

    container.innerHTML = `
      <svg viewBox="0 0 420 200" width="420" height="200" aria-label="Mesh topology">
        <line x1="80" y1="100" x2="210" y2="100" stroke="${relayOk ? "rgba(110,181,255,0.5)" : "rgba(240,84,74,0.25)"}" stroke-width="2" stroke-dasharray="${relayOk ? "0" : "6 4"}"/>
        <line x1="210" y1="100" x2="340" y2="100" stroke="${relayOk ? "rgba(110,181,255,0.5)" : "rgba(240,84,74,0.25)"}" stroke-width="2" stroke-dasharray="${relayOk ? "0" : "6 4"}"/>
        <circle cx="80" cy="100" r="36" fill="${SURFACE}" stroke="${stroke(true)}" stroke-width="2"/>
        <circle cx="80" cy="100" r="8" fill="${color(true)}"/>
        <text x="80" y="155" text-anchor="middle" fill="#8b909a" font-size="11">Sensor</text>
        <circle cx="210" cy="100" r="36" fill="${SURFACE}" stroke="${stroke(relayOk)}" stroke-width="2"/>
        <circle cx="210" cy="100" r="8" fill="${color(relayOk)}"/>
        <text x="210" y="155" text-anchor="middle" fill="#8b909a" font-size="11">${offlineNode || "Relay-3"}</text>
        <circle cx="340" cy="100" r="36" fill="${SURFACE}" stroke="${stroke(uavOk)}" stroke-width="2"/>
        <circle cx="340" cy="100" r="8" fill="${color(uavOk)}"/>
        <text x="340" y="155" text-anchor="middle" fill="#8b909a" font-size="11">Edge UAV</text>
        ${relayDead ? '<text x="210" y="55" text-anchor="middle" fill="#f0544a" font-size="12">Partitioned</text>' : ""}
      </svg>`;
  }

  function renderHeatmap(failureHour, mode, total) {
    const el = document.getElementById("heatmap");
    if (!el) return;
    const runner = mode === "golden" ? "run/ci-golden-mesh.html" : "run/relay-death-t14.html";
    el.innerHTML = "";
    for (let h = 0; h < total; h++) {
      const bad = failureHour != null && h >= failureHour;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.title = "T+" + h + "h";
      btn.className = bad ? "bad" : "";
      btn.addEventListener("click", () => {
        window.location.href = runner + "#h" + h;
      });
      el.appendChild(btn);
    }
  }

  let modes = {};
  let currentMode = "failure";
  let offlineNode = "relay-3";

  function setMode(mode) {
    currentMode = mode;
    const cfg = modes[mode];
    document.querySelectorAll(".mode-tabs button").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.mode === mode);
    });
    const hint = document.getElementById("mode-hint");
    if (hint) hint.textContent = cfg.hint;
    const status = document.getElementById("mesh-status-text");
    if (status) status.textContent = cfg.meshStatus;

    const canvas = document.getElementById("timeline-chart");
    if (canvas) drawTimeline(canvas, cfg);

    const mesh = document.getElementById("mesh-viz");
    if (mesh) renderMesh(mesh, cfg.failureHour, cfg.failureHour ?? cfg.total, offlineNode);

    renderHeatmap(cfg.failureHour, mode, cfg.total);
  }

  document.querySelectorAll(".mode-tabs button").forEach((btn) => {
    btn.addEventListener("click", () => setMode(btn.dataset.mode));
  });

  async function init() {
    let failure = null;
    let golden = null;
    let latest = null;
    try {
      [failure, golden, latest] = await Promise.all([
        window.LatticeSiteData.loadScenario("relay-death-t14"),
        window.LatticeSiteData.loadScenario("ci-golden-mesh"),
        window.LatticeSiteData.loadLatest(),
      ]);
      offlineNode = failure?.mesh?.offline_node || "relay-3";
    } catch (err) {
      console.warn("Using fallback demo data:", err);
      failure = { failure_hour: 14, duration_hours: 72, hourly_investigate_tasks: [], tasks_total: 14, verdict: "block" };
      golden = { failure_hour: null, duration_hours: 72, tasks_total: 73, verdict: "deploy" };
    }

    modes = buildModes(failure, golden);
    applyLatestMeta(latest, failure);
    setMode("failure");

    window.addEventListener("resize", () => {
      drawTimeline(document.getElementById("timeline-chart"), modes[currentMode]);
    });
  }

  init();
})();
