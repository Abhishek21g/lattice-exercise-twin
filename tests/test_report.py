from lattice_exercise_twin.doctor import doctor_run
from lattice_exercise_twin.paths import run_dir
from lattice_exercise_twin.plan import load_plan, save_plan
from lattice_exercise_twin.report import render_html, write_report
from lattice_exercise_twin.run import run_exercise


def test_report_html(workspace):
    plan = load_plan(workspace / "examples" / "platoon-mesh-3node.yaml")
    save_plan(plan)
    rid, _ = run_exercise(plan=plan, mock=True)
    m = doctor_run(rid)
    html = render_html(m)
    assert "verdict-block" in html
    paths = write_report(m, run_dir(rid), html_out=True)
    assert any(p.name == "report.html" for p in paths)
