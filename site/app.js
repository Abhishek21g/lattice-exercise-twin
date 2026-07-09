const NODES = [
  { id: "tower-12", x: 80, y: 140, role: "sensor" },
  { id: "relay-3", x: 200, y: 80, role: "relay" },
  { id: "uav-orin-07", x: 320, y: 140, role: "edge" },
];
const LINKS = [
  ["tower-12", "relay-3"],
  ["relay-3", "uav-orin-07"],
];
const RELAY_DEATH_H = 14;

function drawMesh(relayOnline) {
  const svg = document.getElementById("mesh-svg");
  svg.innerHTML = "";
  const ns = "http://www.w3.org/2000/svg";

  const nodeMap = Object.fromEntries(NODES.map((n) => [n.id, n]));

  LINKS.forEach(([a, b]) => {
    const na = nodeMap[a];
    const nb = nodeMap[b];
    const up = relayOnline || (a !== "relay-3" && b !== "relay-3");
    const line = document.createElementNS(ns, "line");
    line.setAttribute("x1", na.x);
    line.setAttribute("y1", na.y);
    line.setAttribute("x2", nb.x);
    line.setAttribute("y2", nb.y);
    line.setAttribute("stroke", up ? "#4ade9a" : "#ff6b7a");
    line.setAttribute("stroke-width", up ? "2" : "1");
    line.setAttribute("stroke-dasharray", up ? "" : "6 4");
    svg.appendChild(line);
  });

  NODES.forEach((n) => {
    const online = n.id === "relay-3" ? relayOnline : true;
    const g = document.createElementNS(ns, "g");
    const circle = document.createElementNS(ns, "circle");
    circle.setAttribute("cx", n.x);
    circle.setAttribute("cy", n.y);
    circle.setAttribute("r", "28");
    circle.setAttribute("fill", online ? "#141e2b" : "#2a1014");
    circle.setAttribute("stroke", online ? "#7cb8ff" : "#ff6b7a");
    circle.setAttribute("stroke-width", "2");
    const label = document.createElementNS(ns, "text");
    label.setAttribute("x", n.x);
    label.setAttribute("y", n.y + 4);
    label.setAttribute("text-anchor", "middle");
    label.setAttribute("fill", "#e8eef6");
    label.setAttribute("font-size", "10");
    label.setAttribute("font-family", "IBM Plex Mono, monospace");
    label.textContent = n.id.split("-")[0];
    g.appendChild(circle);
    g.appendChild(label);
    svg.appendChild(g);
  });
}

function update(hour) {
  const relayOnline = hour < RELAY_DEATH_H;
  drawMesh(relayOnline);
  document.getElementById("time-label").textContent = `T+${hour}h`;
  const status = document.getElementById("sim-status");
  if (hour >= RELAY_DEATH_H) {
    status.className = "status block";
    status.textContent = "Relay-3 lost — entity stream gap — Investigate task blocked";
  } else {
    status.className = "status ok";
    status.textContent = "Mesh healthy — Investigate tasks assigning";
  }
}

const slider = document.getElementById("timeline");
slider.addEventListener("input", () => update(Number(slider.value)));
update(Number(slider.value));
