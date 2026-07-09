"""HTML and Markdown reports."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


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
    offline = set(probe.get("final_nodes_online") or [])
    for n in mesh.get("nodes") or []:
        nid = n["id"]
        online = nid in offline
        cls = "ok" if online else "bad"
        nodes_html += f'<div class="node {cls}"><span>{html.escape(nid)}</span><small>{html.escape(n.get("role",""))}</small></div>'

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
  <link rel="stylesheet" href="../styles.css">
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
