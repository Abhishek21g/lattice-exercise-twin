"""Optional live Lattice sandbox connectivity."""

from __future__ import annotations

import os
from typing import Any


REQUIRED_ENV = (
    "LATTICE_ENDPOINT",
    "LATTICE_CLIENT_ID",
    "LATTICE_CLIENT_SECRET",
)


def check_lattice_env() -> dict[str, str | None]:
    return {k: os.environ.get(k) for k in (*REQUIRED_ENV, "SANDBOXES_TOKEN")}


def missing_env(env: dict[str, str | None]) -> list[str]:
    return [k for k in REQUIRED_ENV if not env.get(k)]


def ping_sandbox(env: dict[str, str | None]) -> dict[str, Any]:
    miss = missing_env(env)
    if miss:
        return {"ok": False, "error": f"missing env: {miss}", "docs": "docs/LATTICE_SANDBOX_SETUP.md"}

    try:
        import urllib.error
        import urllib.request

        endpoint = env["LATTICE_ENDPOINT"]
        url = f"https://{endpoint}/api/v1/oauth/token"
        req = urllib.request.Request(url, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        if env.get("SANDBOXES_TOKEN"):
            req.add_header("Anduril-Sandbox-Authorization", f"Bearer {env['SANDBOXES_TOKEN']}")
        body = (
            f"grant_type=client_credentials&client_id={env['LATTICE_CLIENT_ID']}"
            f"&client_secret={env['LATTICE_CLIENT_SECRET']}"
        ).encode()
        with urllib.request.urlopen(req, data=body, timeout=15) as resp:
            return {"ok": resp.status == 200, "status": resp.status, "endpoint": endpoint}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "endpoint": env.get("LATTICE_ENDPOINT")}
    except Exception as exc:  # noqa: BLE001 — surface to CLI user
        return {"ok": False, "error": str(exc), "endpoint": env.get("LATTICE_ENDPOINT")}
