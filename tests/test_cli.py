from lattice_exercise_twin.cli import main


def test_cli_flow(workspace):
    assert main(["plan", "examples/platoon-mesh-3node.yaml"]) == 0
    assert main(["run", "--plan", "platoon-mesh-3node"]) == 0
    assert main(["doctor", "latest"]) == 1
    assert main(["report", "latest", "--html"]) == 0


def test_check_env_missing(monkeypatch):
    monkeypatch.delenv("LATTICE_ENDPOINT", raising=False)
    assert main(["check-env"]) == 1
