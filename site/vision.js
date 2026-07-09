(function () {
  const SURFACE = "#16161a";
  const FAILURE_HOUR = 14;
  const TOTAL_HOURS = 72;

  const hints = {
    sandbox: "All nodes online. Investigate task assigns every hour. CI is green.",
    field: "Relay-3 offline at hour 14. Entity stream stops. Investigate tasks block.",
  };

  function renderDiagram(broken) {
    const relayOk = !broken;
    const color = (ok) => (ok ? "#3ec97a" : "#f0544a");
    const stroke = (ok) => (ok ? "rgba(62,201,122,0.45)" : "rgba(240,84,74,0.45)");
    const link = relayOk ? "rgba(110,181,255,0.55)" : "rgba(240,84,74,0.25)";
    const dash = relayOk ? "0" : "6 4";

    return `
      <svg viewBox="0 0 520 220" width="520" height="220" role="img" aria-label="Three-node mesh diagram">
        <line x1="100" y1="110" x2="260" y2="110" stroke="${link}" stroke-width="2.5" stroke-dasharray="${dash}"/>
        <line x1="260" y1="110" x2="420" y2="110" stroke="${link}" stroke-width="2.5" stroke-dasharray="${dash}"/>
        <circle cx="100" cy="110" r="42" fill="${SURFACE}" stroke="${stroke(true)}" stroke-width="2"/>
        <circle cx="100" cy="110" r="10" fill="${color(true)}"/>
        <text x="100" y="175" text-anchor="middle" fill="#b4b8c0" font-size="13" font-family="Inter,sans-serif">Sensor</text>
        <circle cx="260" cy="110" r="42" fill="${SURFACE}" stroke="${stroke(relayOk)}" stroke-width="2"/>
        <circle cx="260" cy="110" r="10" fill="${color(relayOk)}"/>
        <text x="260" y="175" text-anchor="middle" fill="#b4b8c0" font-size="13" font-family="Inter,sans-serif">Relay-3</text>
        <circle cx="420" cy="110" r="42" fill="${SURFACE}" stroke="${stroke(relayOk)}" stroke-width="2"/>
        <circle cx="420" cy="110" r="10" fill="${color(relayOk)}"/>
        <text x="420" y="175" text-anchor="middle" fill="#b4b8c0" font-size="13" font-family="Inter,sans-serif">Edge UAV</text>
        ${broken ? '<text x="260" y="55" text-anchor="middle" fill="#f0544a" font-size="13" font-family="Inter,sans-serif">Relay offline · stream stopped</text>' : '<text x="260" y="55" text-anchor="middle" fill="#3ec97a" font-size="13" font-family="Inter,sans-serif">All links healthy</text>'}
        <text x="260" y="205" text-anchor="middle" fill="#8b909a" font-size="11" font-family="IBM Plex Mono,monospace">${broken ? "Investigate: BLOCKED" : "Investigate: assigning"}</text>
      </svg>`;
  }

  function buildTimeline() {
    const el = document.getElementById("mini-timeline");
    if (!el) return;
    el.innerHTML = "";
    for (let h = 0; h < TOTAL_HOURS; h++) {
      const span = document.createElement("span");
      if (h >= FAILURE_HOUR) span.className = "bad";
      el.appendChild(span);
    }
  }

  let stepIdx = 0;
  let stepTimer;

  function animateSteps(broken) {
    clearInterval(stepTimer);
    const steps = document.querySelectorAll(".flow-step");
    stepIdx = 0;
    steps.forEach((s, i) => s.classList.toggle("active", i === 0));

    stepTimer = setInterval(() => {
      stepIdx = (stepIdx + 1) % 4;
      steps.forEach((s, i) => {
        s.classList.toggle("active", i === stepIdx);
        if (broken && stepIdx >= 2) {
          s.style.opacity = i <= 1 ? "1" : "0.35";
        } else {
          s.style.opacity = "1";
        }
      });
    }, 1400);
  }

  function setView(view) {
    const broken = view === "field";
    document.querySelectorAll("#compare-tabs button").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.view === view);
    });

    const hint = document.getElementById("compare-hint");
    if (hint) hint.textContent = hints[view];

    const diagram = document.getElementById("flow-diagram");
    if (diagram) diagram.innerHTML = renderDiagram(broken);

    const status = document.getElementById("flow-status");
    if (status) {
      status.textContent = broken
        ? "T+14H · RELAY-3 OFFLINE · INVESTIGATE BLOCKED"
        : "ALL NODES ONLINE · TASKS ASSIGNING";
    }

    const sandbox = document.getElementById("card-sandbox");
    const field = document.getElementById("card-field");
    if (sandbox) sandbox.style.opacity = broken ? "0.55" : "1";
    if (field) field.style.opacity = broken ? "1" : "0.55";

    animateSteps(broken);
  }

  document.querySelectorAll("#compare-tabs button").forEach((btn) => {
    btn.addEventListener("click", () => setView(btn.dataset.view));
  });

  buildTimeline();
  setView("sandbox");
})();
