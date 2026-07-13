"""HTML and Markdown reports."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

_INLINE_CSS = """
:root {
  --bg: #0f1419;
  --fg: #e7ecf1;
  --muted: #9aa8b5;
  --accent: #5ec8a8;
  --bad: #e07a7a;
  --ok: #7ecf9a;
  --card: #1a222b;
}
body.report-page {
  margin: 0;
  font-family: ui-sans-serif, system-ui, sans-serif;
  background: var(--bg);
  color: var(--fg);
}
.shell { max-width: 720px; margin: 0 auto; padding: 2rem 1.25rem 3rem; }
.eyebrow { color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; font-size: 0.75rem; }
h1 { font-size: 1.75rem; margin: 0.35rem 0 0.5rem; }
.lede { color: var(--muted); }
.block-at { color: var(--bad); font-weight: 600; }
.verdict-block { color: var(--bad); }
.verdict-deploy { color: var(--ok); }
.verdict-review { color: #e0b35c; }
.mesh-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.75rem;
  margin: 1.5rem 0;
}
.node {
  background: var(--card);
  border-radius: 8px;
  padding: 0.85rem 1rem;
  border: 1px solid #2a3540;
}
.node.ok { border-color: #2f5a40; }
.node.bad { border-color: #5a2f2f; }
.node span { display: block; font-weight: 600; }
.node small { color: var(--muted); }
.findings { display: grid; gap: 0.75rem; }
.finding {
  background: var(--card);
  border-radius: 8px;
  padding: 0.9rem 1rem;
  border-left: 3px solid #4a5560;
}
.finding.critical { border-left-color: var(--bad); }
.finding.warning { border-left-color: #e0b35c; }
.finding h4 { margin: 0 0 0.35rem; font-size: 0.95rem; }
.finding p { margin: 0; color: var(--muted); font-size: 0.9rem; }
.pass { color: var(--ok); }
"""


def render_summary_md(manifest: dict[str, Any]) -> str:
    doc = manifest.get("doctor") or {}
    plan = manifest.get("plan", {})
    probe = manifest.get("probe", {})
    verdict = doc.get("verdict", "pending").upper()
    block_h = probe.get("first_block_hour")
    lines = [
        "# Lattice Exercise Twin — Mission Receipt",
        "",
        f"- **Run:** `{manifest.get('run_id')}`",
        f"- **Verdict:** **{verdict}**",
        f"- **Exercise:** {plan.get('name')}",
        f"- **Duration:** {plan.get('duration_hours')}h",
    ]
    if block_h is not None:
        lines.append(f"- **First block:** T+{block_h}h — {probe.get('block_reason')}")
    lines.extend(["", "## Findings", ""])
    for f in doc.get("findings") or []:
        lines.append(f"- **[{f['severity']}]** {f['title']}: {f['detail']}")
    lines.extend(["", "---", manifest.get("disclaimer", "")])
    return "\n".join(lines) + "\n"


def render_html(manifest: dict[str, Any]) -> str:
    doc = manifest.get("doctor") or {}
    plan = manifest.get("plan", {})
    probe = manifest.get("probe", {})
    verdict = doc.get("verdict", "pending")
    findings = doc.get("findings") or []
    block_h = probe.get("first_block_hour")
    mesh = plan.get("mesh") or {}

    nodes_html = ""
    online_set = set(probe.get("final_nodes_online") or [])
    for n in mesh.get("nodes") or []:
        nid = n["id"]
        online = nid in online_set
        cls = "ok" if online else "bad"
        nodes_html += (
            f'<div class="node {cls}"><span>{html.escape(nid)}</span>'
            f'<small>{html.escape(n.get("role", ""))}</small></div>'
        )

    finding_html = "\n".join(
        f"""<article class="finding {f['severity']}">
          <h4>{html.escape(f['title'])}</h4>
          <p>{html.escape(f['detail'])}</p>
        </article>"""
        for f in findings
    ) or '<p class="pass">All doctor rules passed.</p>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Exercise receipt — {html.escape(verdict.upper())}</title>
  <style>{_INLINE_CSS}</style>
</head>
<body class="report-page">
  <div class="shell">
    <header>
      <p class="eyebrow">Mission receipt · {html.escape(manifest.get('run_id',''))}</p>
      <h1>Verdict: <span class="verdict-{verdict}">{html.escape(verdict.upper())}</span></h1>
      <p class="lede">{html.escape(plan.get('name',''))} · {plan.get('duration_hours',72)}h exercise</p>
      {'<p class="block-at">Blocked at T+' + html.escape(str(block_h)) + 'h</p>' if block_h is not None else ''}
    </header>
    <section class="mesh-grid">{nodes_html}</section>
    <section class="findings">{finding_html}</section>
  </div>
</body>
</html>"""


def write_report(manifest: dict[str, Any], run_dir: Path, *, html_out: bool = False) -> list[Path]:
    written: list[Path] = []
    summary = run_dir / "summary.md"
    summary.write_text(render_summary_md(manifest))
    written.append(summary)
    if html_out:
        report = run_dir / "report.html"
        report.write_text(render_html(manifest))
        written.append(report)
    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    written.append(manifest_path)
    return written
