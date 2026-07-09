from lattice_exercise_twin.rules import check_exercise_block, check_stream_gaps, run_doctor_rules


def test_block_finding():
    findings = check_exercise_block({"first_block_hour": 14, "block_reason": "mesh_partition"})
    assert findings[0]["severity"] == "critical"


def test_relay_doctor_blocks(relay_scenario, base_plan):
    from lattice_exercise_twin.simulate import simulate_exercise

    probe = simulate_exercise(plan=base_plan, scenario=relay_scenario)
    findings, verdict = run_doctor_rules(probe=probe, plan=base_plan, golden_probe=None)
    assert verdict == "block"
    assert any("T+14" in f["title"] for f in findings)


def test_golden_doctor_deploys(golden_scenario, base_plan):
    from lattice_exercise_twin.simulate import simulate_exercise

    probe = simulate_exercise(plan=base_plan, scenario=golden_scenario)
    _, verdict = run_doctor_rules(probe=probe, plan=base_plan, golden_probe=None)
    assert verdict == "deploy"
