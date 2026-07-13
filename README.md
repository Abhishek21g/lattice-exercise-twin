# Lattice Exercise Twin

**Plan → run → doctor → report** for Lattice mesh exercise fate — catch entity stream gaps and Investigate task failure **before** live exercise hours.

> Your sandbox integration passes — the exercise still dies when Relay-3 drops at hour 14.

**Site:** [enaguthi.com/lattice-exercise-twin/site/](https://enaguthi.com/lattice-exercise-twin/site/)  
**Reference:** [sample-app-auto-reconnaissance](https://github.com/anduril/sample-app-auto-reconnaissance) (Entities → Investigate task)

Independent demo using public Lattice SDK concepts. Not affiliated with Anduril.

---

## Quick start (mock — no credentials)

```bash
git clone https://github.com/Abhishek21g/lattice-exercise-twin
cd lattice-exercise-twin && pip install -e ".[dev]"

lattice-exercise-twin plan examples/platoon-mesh-3node.yaml
lattice-exercise-twin run --plan platoon-mesh-3node   # mock by default
lattice-exercise-twin doctor latest    # → BLOCK at T+14h
lattice-exercise-twin report latest --html
lattice-exercise-twin sync-site latest # refresh site/data from plan scenarios
```

`run --live` only pings Lattice sandbox auth — full exercise fate is **mock** until sandbox entity/task playback is wired. See [docs/LATTICE_SANDBOX_SETUP.md](docs/LATTICE_SANDBOX_SETUP.md).

---

## Lattice sandbox (live upgrade)

See [docs/LATTICE_SANDBOX_SETUP.md](docs/LATTICE_SANDBOX_SETUP.md).

```bash
cp docs/lattice-env.example ~/.config/lattice-exercise-twin/env
# fill in credentials from developer.anduril.com
source ~/.config/lattice-exercise-twin/env
lattice-exercise-twin check-env
pip install -e ".[live]"
lattice-exercise-twin run --plan platoon-mesh-3node --live
```

---

## Commands

| Command | Purpose |
|---------|---------|
| `plan <yaml>` | Exercise mesh topology + duration → `out/plans/` |
| `run [--plan NAME] [--scenario PATH]` | Mock mesh fate sim (default) or `--live` sandbox ping |
| `doctor [run_id]` | Block/review/deploy from stream gap + task rules |
| `report [--html]` | Mission receipt (self-contained HTML) |
| `sync-site [run_id]` | Export plan scenarios → `site/data/` (relay-death + golden) |
| `check-env` | Verify `LATTICE_*` env vars |

---

## Scenarios

| Scenario | Result |
|----------|--------|
| `relay-death-t14` | BLOCK at T+14h — relay loss partitions mesh |
| `ci-golden-mesh` | deploy — continuous Investigate tasks |

---

## PR track (optional)

Extend [sample-app-auto-reconnaissance](https://github.com/anduril/sample-app-auto-reconnaissance) with failure injection or propose `sample-app-exercise-preflight` upstream.

---

## License

MIT
