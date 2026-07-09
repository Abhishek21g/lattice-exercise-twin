# Lattice Sandbox setup

Follow [Anduril developer docs](https://developer.anduril.com/guides/getting-started/set-up).

## 1. Request access

If you do not have a sandbox, request the **Lattice SDK developer program** from the developer portal.

## 2. Create environment

1. Log in at [developer.anduril.com](https://developer.anduril.com)
2. Create a sandbox environment
3. Copy **endpoint**, **client ID**, **client secret**
4. From [sandboxes user settings](https://sandboxes.developer.anduril.com/user-settings), copy **SANDBOXES_TOKEN**

## 3. Configure this project

```bash
cp docs/lattice-env.example ~/.config/lattice-exercise-twin/env
# edit values, then:
source ~/.config/lattice-exercise-twin/env
lattice-exercise-twin check-env
```

## 4. Quickstart publish (upstream)

See [Quickstart](https://developer.anduril.com/guides/getting-started/quickstart) — publish a surface vessel entity with curl.

## 5. Live mode (optional)

```bash
pip install -e ".[live]"
source ~/.config/lattice-exercise-twin/env
lattice-exercise-twin run --plan platoon-mesh-3node --live
```

Mock mode works **without** any credentials — use that for demos and CI.

## 6. PR track — sample app

Clone upstream auto-reconnaissance:

```bash
git clone https://github.com/anduril/sample-app-auto-reconnaissance.git
```

Exercise Twin models its **Entities stream → Investigate task** loop in mock simulation.
