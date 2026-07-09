(function () {
  const FAILURE_HOUR = 14;
  const TOTAL_HOURS = 72;

  const modes = {
    failure: {
      hint: "Relay-3 goes offline at hour 14. Entity updates stop. Investigate tasks block.",
      failureHour: FAILURE_HOUR,
      meshStatus: "T+14H · RELAY-3 OFFLINE",
    },
    golden: {
      hint: "All three nodes stay online. Investigate tasks assign every hour for 72 hours.",
      failureHour: null,
      meshStatus: "T+72H · ALL NODES HEALTHY",
    },
  };

  let currentMode = "failure";

  function taskCountAtHour(h, failureHour) {
    if (failureHour !== null && h >= failureHour) return 0;
    return 1;
  }

  function buildTimelineData(failureHour) {
    const points = [];
    for (let h = 0; h <= TOTAL_HOURS; h++) {
      points.push({ hour: h, tasks: taskCountAtHour(h, failureHour) });
    }
    return points;
  }

  function drawTimeline(canvas, failureHour) {
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
    ctx.fillStyle = "#8b909a";
    ctx.font = "11px IBM Plex Mono, monospace";
    ctx.fillText("Tasks/hr", 4, pad.t + 8);

    const data = buildTimelineData(failureHour);
    const maxY = 1.2;

    ctx.strokeStyle = "rgba(237,234,233,0.08)";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
      const y = pad.t + (plotH * i) / 4;
      ctx.beginPath();
      ctx.moveTo(pad.l, y);
      ctx.lineTo(w - pad.r, y);
      ctx.stroke();
    }

    if (failureHour !== null) {
      const fx = pad.l + (failureHour / TOTAL_HOURS) * plotW;
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
    data.forEach((pt, i) => {
      const x = pad.l + (pt.hour / TOTAL_HOURS) * plotW;
      const y = pad.t + plotH - (pt.tasks / maxY) * plotH;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.strokeStyle = failureHour !== null ? "#6eb5ff" : "#3ec97a";
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.fillStyle = "#8b909a";
    ctx.font = "10px IBM Plex Mono, monospace";
    [0, 24, 48, 72].forEach((hr) => {
      const x = pad.l + (hr / TOTAL_HOURS) * plotW;
      ctx.fillText("T+" + hr, x - 8, h - 10);
    });
  }

  function renderMesh(container, failureHour, hour) {
    const relayDead = failureHour !== null && hour >= failureHour;
    const sensorOk = true;
    const relayOk = !relayDead;
    const uavOk = !relayDead;

    const color = (ok) => (ok ? "#3ec97a" : "#f0544a");
    const stroke = (ok) => (ok ? "rgba(62,201,122,0.4)" : "rgba(240,84,74,0.4)");

    container.innerHTML = `
      <svg viewBox="0 0 420 200" width="420" height="200" aria-label="Mesh topology">
        <line x1="80" y1="100" x2="210" y2="100" stroke="${relayOk ? 'rgba(110,181,255,0.5)' : 'rgba(240,84,74,0.25)'}" stroke-width="2" stroke-dasharray="${relayOk ? '0' : '6 4'}"/>
        <line x1="210" y1="100" x2="340" y2="100" stroke="${relayOk ? 'rgba(110,181,255,0.5)' : 'rgba(240,84,74,0.25)'}" stroke-width="2" stroke-dasharray="${relayOk ? '0' : '6 4'}"/>
        <circle cx="80" cy="100" r="36" fill="var(--surface)" stroke="${stroke(sensorOk)}" stroke-width="2"/>
        <circle cx="80" cy="100" r="8" fill="${color(sensorOk)}"/>
        <text x="80" y="155" text-anchor="middle" fill="#8b909a" font-size="11" font-family="Inter,sans-serif">Sensor</text>
        <circle cx="210" cy="100" r="36" fill="var(--surface)" stroke="${stroke(relayOk)}" stroke-width="2"/>
        <circle cx="210" cy="100" r="8" fill="${color(relayOk)}"/>
        <text x="210" y="155" text-anchor="middle" fill="#8b909a" font-size="11" font-family="Inter,sans-serif">Relay-3</text>
        <circle cx="340" cy="100" r="36" fill="var(--surface)" stroke="${stroke(uavOk)}" stroke-width="2"/>
        <circle cx="340" cy="100" r="8" fill="${color(uavOk)}"/>
        <text x="340" y="155" text-anchor="middle" fill="#8b909a" font-size="11" font-family="Inter,sans-serif">Edge UAV</text>
        ${relayDead ? '<text x="210" y="55" text-anchor="middle" fill="#f0544a" font-size="12" font-family="Inter,sans-serif">Partitioned</text>' : ''}
      </svg>`;
  }

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
    if (canvas) drawTimeline(canvas, cfg.failureHour);

    const mesh = document.getElementById("mesh-viz");
    if (mesh) renderMesh(mesh, cfg.failureHour, cfg.failureHour ?? TOTAL_HOURS);

    renderHeatmap(cfg.failureHour, mode);
  }

  function renderHeatmap(failureHour, mode) {
    const el = document.getElementById("heatmap");
    if (!el) return;
    const runner =
      mode === "golden" ? "run/ci-golden-mesh.html" : "run/relay-death-t14.html";
    el.innerHTML = "";
    for (let h = 0; h < TOTAL_HOURS; h++) {
      const bad = failureHour !== null && h >= failureHour;
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

  document.querySelectorAll(".mode-tabs button").forEach((btn) => {
    btn.addEventListener("click", () => setMode(btn.dataset.mode));
  });

  setMode("failure");

  window.addEventListener("resize", () => {
    const cfg = modes[currentMode];
    const canvas = document.getElementById("timeline-chart");
    if (canvas) drawTimeline(canvas, cfg.failureHour);
  });
})();
