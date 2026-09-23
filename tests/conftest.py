"""Shared fixtures: temp workdir tree with slot sentinels, registry, settings."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

import pytest

from serverfs_mcp.config import Settings
from serverfs_mcp.workdirs import SLOT_COUNT, Workdir, WorkdirRegistry, build_registry


@pytest.fixture()
def tmp_path(tmp_path_factory: pytest.TempPathFactory):
    """Use short macOS temp paths so AF_UNIX socket tests fit sun_path."""
    if sys.platform == "darwin":
        root = Path(tempfile.mkdtemp(prefix="sfs-", dir="/tmp"))
    else:
        root = tmp_path_factory.mktemp("tmp")
    yield root
    if sys.platform == "darwin":
        shutil.rmtree(root, ignore_errors=True)


@pytest.fixture()
def workdir_root(tmp_path: Path) -> Path:
    """A workdir root with slot 01 mounted as a real tree, others disabled."""
    root = tmp_path / "workdirs"
    root.mkdir()
    real = root / "01"
    real.mkdir()
    for slot in range(2, SLOT_COUNT + 1):
        d = root / f"{slot:02d}"
        d.mkdir()
        (d / ".serverfs-disabled").touch()
    return root


@pytest.fixture()
def registry(workdir_root: Path) -> WorkdirRegistry:
    return build_registry(
        {1: "test", **{s: "" for s in range(2, SLOT_COUNT + 1)}},
        {1: "A test workdir", **{s: "" for s in range(2, SLOT_COUNT + 1)}},
        workdir_root=workdir_root,
    )


@pytest.fixture()
def workdir(registry) -> Workdir:
    wd = registry.get("test")
    assert wd is not None
    return wd


@pytest.fixture()
def settings() -> Settings:
    return Settings()
