from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from serverfs_mcp.config import Settings
from serverfs_mcp.workdirs import WorkdirError, build_registry_from_env

_REPO_ROOT = Path(__file__).resolve().parents[1]
_LAUNCHER_PATH = _REPO_ROOT / "deployment" / "agent-bridge" / "run_macos_server.py"
_SPEC = importlib.util.spec_from_file_location("serverfs_macos_launcher", _LAUNCHER_PATH)
assert _SPEC is not None and _SPEC.loader is not None
macos_launcher = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(macos_launcher)


def test_native_mode_uses_direct_host_paths_and_no_disabled_sentinels(tmp_path: Path) -> None:
    projects = tmp_path / "Projects"
    projects.mkdir()

    registry = build_registry_from_env(
        {
            "SERVERFS_NATIVE_MODE": "true",
            "WORKDIR_01_ALIAS": "projects",
            "WORKDIR_01_PATH": str(projects),
        },
        Settings(),
    )

    assert registry.get("projects").container_path == projects
    assert len(registry) == 1


def test_native_mode_rejects_a_missing_path(tmp_path: Path) -> None:
    with pytest.raises(WorkdirError, match="existing absolute real directory"):
        build_registry_from_env(
            {
                "SERVERFS_NATIVE_MODE": "true",
                "WORKDIR_01_ALIAS": "projects",
                "WORKDIR_01_PATH": str(tmp_path / "missing"),
            },
            Settings(),
        )


def test_native_launcher_excludes_tunnel_and_provider_secrets() -> None:
    env = macos_launcher.server_environment(
        {
            "SERVERFS_NATIVE_MODE": "true",
            "SERVERFS_LOG_LEVEL": "INFO",
            "SERVERFS_AGENT_BRIDGE_ENABLED": "true",
            "SERVERFS_AGENT_BRIDGE_HOST_SOCKET_DIR": "/Users/tester/.local/share/bridge/socket",
            "SERVERFS_AGENT_LOCK_HOST_DIR": "/Users/tester/.local/share/bridge/locks",
            "SERVERFS_CODEX_HOME": "/private/codex-home",
            "SERVERFS_JEV_API_KEY": "sensitive-jev-value",
            "CONTROL_PLANE_API_KEY": "sensitive-tunnel-value",
            "WORKDIR_01_PATH": "/Users/tester/Projects",
        },
        {"PATH": "/usr/bin", "HOME": "/Users/tester"},
    )

    assert env["SERVERFS_NATIVE_MODE"] == "true"
    assert env["SERVERFS_LOG_LEVEL"] == "INFO"
    assert env["SERVERFS_AGENT_BRIDGE_ENABLED"] == "true"
    assert env["SERVERFS_AGENT_BRIDGE_SOCKET"] == (
        "/Users/tester/.local/share/bridge/socket/bridge.sock"
    )
    assert env["SERVERFS_AGENT_LOCK_DIR"] == "/Users/tester/.local/share/bridge/locks"
    assert env["WORKDIR_01_PATH"] == "/Users/tester/Projects"
    assert "SERVERFS_CODEX_HOME" not in env
    assert "SERVERFS_JEV_API_KEY" not in env
    assert "CONTROL_PLANE_API_KEY" not in env
