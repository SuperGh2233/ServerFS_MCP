"""Child-process helper for macOS directory-FD cwd setup.

macOS cannot use /proc/self/fd/N as a subprocess cwd. This short-lived helper
inherits the already-validated directory FD, changes cwd with fchdir, closes
the inherited FD, then replaces itself with the requested executable.
"""

from __future__ import annotations

import os
import sys


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit("usage: fd_exec.py FD COMMAND [ARG ...]")
    directory_fd = int(sys.argv[1])
    command = sys.argv[2:]
    os.fchdir(directory_fd)
    os.close(directory_fd)
    os.execvpe(command[0], command, os.environ)


if __name__ == "__main__":
    main()
