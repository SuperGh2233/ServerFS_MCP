#!/usr/bin/env python3
"""Start native macOS ServerFS with only its non-secret .env settings."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENT_DEPLOYMENT = REPO_ROOT / "deployment" / "agent-bridge"
sys.path.insert(0, str(AGENT_DEPLOYMENT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from render_config import load_env_file  # noqa: E402

from serverfs_mcp.workdirs import WorkdirError, native_mode_enabled  # noqa: E402

_HOST_ENV_KEYS = ("HOME", "LANG", "LC_ALL", "PATH", "TMPDIR")
_PROVIDER_ONLY_KEYS = (
    "SERVERFS_AGENT_BRIDGE_HOST_SOCKET_DIR",
    "SERVERFS_AGENT_PEER_GID",
    "SERVERFS_AGENT_PEER_UID",
    "SERVERFS_AGENT_BRIDGE_STATE_DIR",
    "SERVERFS_AGENT_LOCK_HOST_DIR",
    "SERVERFS_CLAUDE_",
    "SERVERFS_CODEX_",
    "SERVERFS_JEV_API_KEY",
)


def server_environment(values: dict[str, str], host_environment: dict[str, str]) -> dict[str, str]:
    """Build a minimal ServerFS process environment, excluding provider secrets."""
    if not native_mode_enabled(values):
        raise WorkdirError("set SERVERFS_NATIVE_MODE=true before using the macOS launcher")
    result = {key: host_environment[key] for key in _HOST_ENV_KEYS if host_environment.get(key)}
    for key, value in values.items():
        if key.startswith("WORKDIR_") or key.startswith("SERVERFS_") or key == "TZ":
            if any(key == item or key.startswith(item) for item in _PROVIDER_ONLY_KEYS):
                continue
            result[key] = value
    result["SERVERFS_NATIVE_MODE"] = "true"
    if result.get("SERVERFS_AGENT_BRIDGE_ENABLED", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }:
        socket_dir = values.get("SERVERFS_AGENT_BRIDGE_HOST_SOCKET_DIR", "").strip()
        lock_dir = values.get("SERVERFS_AGENT_LOCK_HOST_DIR", "").strip()
        if not socket_dir or not lock_dir:
            raise WorkdirError(
                "native Agent Bridge mode requires SERVERFS_AGENT_BRIDGE_HOST_SOCKET_DIR "
                "and SERVERFS_AGENT_LOCK_HOST_DIR"
            )
        result["SERVERFS_AGENT_BRIDGE_SOCKET"] = str(Path(socket_dir).expanduser() / "bridge.sock")
        result["SERVERFS_AGENT_LOCK_DIR"] = str(Path(lock_dir).expanduser())
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=REPO_ROOT / ".env")
    args = parser.parse_args()
    values = load_env_file(args.env_file)
    host_environment = dict(os.environ)
    server_env = server_environment(values, host_environment)
    os.environ.clear()
    os.environ.update(server_env)
    from serverfs_mcp.main import main as server_main

    return server_main()


if __name__ == "__main__":
    raise SystemExit(main())
