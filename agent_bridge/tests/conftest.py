from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.fixture()
def tmp_path(tmp_path_factory: pytest.TempPathFactory):
    """Keep macOS Unix-domain socket test paths below sun_path's limit."""
    if sys.platform == "darwin":
        root = Path(tempfile.mkdtemp(prefix="sfb-", dir="/tmp"))
    else:
        root = tmp_path_factory.mktemp("tmp")
    yield root
    if sys.platform == "darwin":
        shutil.rmtree(root, ignore_errors=True)
