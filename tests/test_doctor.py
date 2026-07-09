from lattice_exercise_twin.doctor import doctor_run
from lattice_exercise_twin.plan import load_plan, save_plan
from lattice_exercise_twin.run import run_exercise


def test_doctor_blocks_relay(workspace):
    plan = load_plan(workspace / "examples" / "platoon-mesh-3node.yaml")
    save_plan(plan)
    rid, _ = run_exercise(plan=plan, mock=True)
    m = doctor_run(rid)
    assert m["doctor"]["verdict"] == "block"


def test_doctor_golden_scenario(workspace):
    plan = load_plan(workspace / "examples" / "platoon-mesh-3node.yaml")
    save_plan(plan)
    rid, _ = run_exercise(
        plan=plan,
        mock=True,
        scenario=workspace / "examples" / "scenarios" / "ci-golden-mesh",
    )
    m = doctor_run(rid)
    assert m["doctor"]["verdict"] == "deploy"
