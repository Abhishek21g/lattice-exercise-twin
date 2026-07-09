from lattice_exercise_twin.simulate import haversine_miles, load_scenario, simulate_exercise


def test_haversine_close_points():
    d = haversine_miles({"lat": 33.69, "lon": -117.92}, {"lat": 33.70, "lon": -117.91})
    assert d < 5


def test_relay_death_blocks(relay_scenario, base_plan):
    probe = simulate_exercise(plan=base_plan, scenario=relay_scenario)
    assert probe["first_block_hour"] == 14.0
    assert probe["block_reason"] == "mesh_partition_blocks_investigate_task"


def test_golden_no_block(golden_scenario, base_plan):
    probe = simulate_exercise(plan=base_plan, scenario=golden_scenario)
    assert probe.get("first_block_hour") is None
    assert probe["tasks_created"] >= 3
