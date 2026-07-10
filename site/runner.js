(function () {
  const SURFACE = "#16161a";
  const config = window.RUNNER_CONFIG || { id: "relay-death-t14" };

  let TOTAL = 72;
  let FAIL = 14;
  let hourly = [];
  let offlineNode = "relay-3";
  let hour = 0;

  function taskAt(h) {
    if (hourly.length) return hourly[h] ?? 0;
    if (FAIL !== null && h >= FAIL) return 0;
    return 1;
  }

  function renderMesh(container, h) {
    const relayDead = FAIL !== null && h >= FAIL;
    const color = (ok) => (ok ? "#3ec97a" : "#f0544a");
    const stroke = (ok) => (ok ? "rgba(62,201,122,0.4)" : "rgba(240,84,74,0.4)");
    const relayOk = !relayDead;
    container.innerHTML = `
      <svg viewBox="0 0 480 240" width="100%" height="240">
        <line x1="90" y1="120" x2="240" y2="120" stroke="${relayOk ? "rgba(110,181,255,0.55)" : "rgba(240,84,74,0.2)"}" stroke-width="2" stroke-dasharray="${relayOk ? "0" : "6 4"}"/>
        <line x1="240" y1="120" x2="390" y2="120" stroke="${relayOk ? "rgba(110,181,255,0.55)" : "rgba(240,84,74,0.2)"}" stroke-width="2" stroke-dasharray="${relayOk ? "0" : "6 4"}"/>
        <circle cx="90" cy="120" r="40" fill="${SURFACE}" stroke="${stroke(true)}" stroke-width="2"/>
        <circle cx="90" cy="120" r="10" fill="${color(true)}"/>
        <text x="90" y="185" text-anchor="middle" fill="#8b909a" font-size="12">Sensor tower</text>
        <circle cx="240" cy="120" r="40" fill="${SURFACE}" stroke="${stroke(relayOk)}" stroke-width="2"/>
        <circle cx="240" cy="120" r="10" fill="${color(relayOk)}"/>
        <text x="240" y="185" text-anchor="middle" fill="#8b909a" font-size="12">${offlineNode}</text>
        <circle cx="390" cy="120" r="40" fill="${SURFACE}" stroke="${stroke(relayOk)}" stroke-width="2"/>
        <circle cx="390" cy="120" r="10" fill="${color(relayOk)}"/>
        <text x="390" y="185" text-anchor="middle" fill="#8b909a" font-size="12">Edge UAV</text>
        ${relayDead ? '<text x="240" y="75" text-anchor="middle" fill="#f0544a" font-size="13">Mission flow stopped</text>' : ""}
      </svg>`;
  }

  function drawMiniChart(canvas, h) {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = 120 * dpr;
    const ctx = canvas.getContext("2d");
    ctx.scale(dpr, dpr);
    const w = rect.width;
    const pad = { l: 8, r: 8, t: 8, b: 20 };
    const plotW = w - pad.l - pad.r;
    const plotH = 120 - pad.t - pad.b;
    const maxY = Math.max(1, ...hourly, 1);

    ctx.clearRect(0, 0, w, 120);
    ctx.fillStyle = SURFACE;
    ctx.fillRect(0, 0, w, 120);
    ctx.beginPath();
    for (let i = 0; i <= TOTAL; i++) {
      const x = pad.l + (i / TOTAL) * plotW;
      const y = pad.t + plotH - (taskAt(i) / (maxY * 1.2)) * plotH;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.strokeStyle = FAIL !== null ? "#6eb5ff" : "#3ec97a";
    ctx.lineWidth = 2;
    ctx.stroke();

    const cx = pad.l + (h / TOTAL) * plotW;
    ctx.strokeStyle = "#edeae9";
    ctx.beginPath();
    ctx.moveTo(cx, pad.t);
    ctx.lineTo(cx, pad.t + plotH);
    ctx.stroke();
  }

  function updateSteps(h) {
    document.querySelectorAll(".steps li").forEach((li, i) => {
      const trigger = Number(li.dataset.hour);
      li.classList.remove("active", "done", "fail");
      if (h >= trigger) {
        if (li.dataset.fail === "true") li.classList.add("fail");
        else li.classList.add("done");
      }
      if (Math.abs(h - trigger) < 2 || (i === 0 && h < 2)) li.classList.add("active");
    });
  }

  function updateReceipt(h) {
    const box = document.getElementById("receipt");
    const verdict = document.getElementById("verdict-text");
    const detail = document.getElementById("receipt-detail");
    if (!box) return;

    if (FAIL !== null && h >= FAIL) {
      box.className = "receipt-box block";
      if (verdict) { verdict.className = "verdict-big block"; verdict.textContent = "BLOCK"; }
      if (detail) detail.textContent = `At T+${h}h: ${offlineNode} offline — Investigate task cannot assign.`;
    } else if (FAIL === null) {
      box.className = "receipt-box pass";
      if (verdict) { verdict.className = "verdict-big pass"; verdict.textContent = "DEPLOY"; }
      if (detail) detail.textContent = `At T+${h}h: mesh healthy — ${taskAt(h)} Investigate task/hr.`;
    } else {
      box.className = "receipt-box";
      if (verdict) { verdict.className = "verdict-big"; verdict.textContent = "…"; verdict.style.color = "var(--muted)"; }
      if (detail) detail.textContent = `At T+${h}h: exercise running — ${taskAt(h)} Investigate task/hr.`;
    }
  }

  function setHour(h) {
    hour = Math.max(0, Math.min(TOTAL, h));
    const slider = document.getElementById("hour-slider");
    if (slider) { slider.max = TOTAL; slider.value = hour; }
    const readout = document.getElementById("time-readout");
    if (readout) readout.textContent = "T+" + hour + "h";
    const mesh = document.getElementById("runner-mesh");
    if (mesh) renderMesh(mesh, hour);
    const chart = document.getElementById("runner-chart");
    if (chart) drawMiniChart(chart, hour);
    updateSteps(hour);
    updateReceipt(hour);
  }

  function bindControls() {
    document.getElementById("hour-slider")?.addEventListener("input", (e) => {
      setHour(Number(e.target.value));
    });
    document.querySelectorAll(".steps li").forEach((li) => {
      li.addEventListener("click", () => setHour(Number(li.dataset.hour)));
    });
    document.getElementById("btn-play")?.addEventListener("click", () => {
      let t = 0;
      const id = setInterval(() => {
        setHour(t);
        t += 1;
        if (t > TOTAL) clearInterval(id);
      }, 400);
    });
  }

  async function init() {
    try {
      const data = await window.LatticeSiteData.loadScenario(config.id);
      TOTAL = data.duration_hours ?? 72;
      FAIL = data.failure_hour;
      hourly = data.hourly_investigate_tasks || [];
      offlineNode = data.mesh?.offline_node || "relay-3";
      const runBadge = document.getElementById("run-badge");
      if (runBadge && data.run_id) runBadge.textContent = `Live data · ${data.run_id}`;
    } catch (err) {
      console.warn("Runner fallback data:", err);
      TOTAL = config.totalHours ?? 72;
      FAIL = config.failureHour ?? 14;
    }

    bindControls();
    setHour(FAIL !== null ? 0 : TOTAL);

    const hash = window.location.hash.match(/^#h(\d+)$/);
    if (hash) setHour(Number(hash[1]));
  }

  init();
})();
