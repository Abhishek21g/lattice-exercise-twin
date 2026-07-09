from lattice_exercise_twin.live import check_lattice_env, missing_env


def test_missing_env_detected(monkeypatch):
    monkeypatch.delenv("LATTICE_ENDPOINT", raising=False)
    monkeypatch.delenv("LATTICE_CLIENT_ID", raising=False)
    env = check_lattice_env()
    assert "LATTICE_ENDPOINT" in missing_env(env)
