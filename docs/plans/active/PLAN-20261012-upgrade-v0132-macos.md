# REQ/PLAN: Upgrade the local Mac deployment to ServerFS v0.13.2

## Problem and business outcome

The local `mac-adapt` checkout is based on v0.7 and needs the current upstream
ServerFS release plus a verified native macOS run path.

## Scope

- Replace the checkout contents with upstream `main` at v0.13.2 and carry a
  small fork-only macOS 26 gate extension.
- Preserve the pre-upgrade uncommitted local work in Git stash.
- Install the two locked Python environments and run the repository quality gates.
- Exercise the supported native CLI diagnostics and manual stdio path where this
  host permits it.

## Non-goals

- Claim upstream macOS support outside the measured boundary. The fork's
  macOS 26 wording must remain experimental and local to this checkout.
- Publish, push, tag, or release anything on GitHub.
- Put credentials in tracked files or documentation.

## Current evidence and constraints

- Upstream archive commit: `567f1c2f94ff62f58710992557a6a63313ba370e`.
- Upstream version: `0.13.2`.
- Host architecture: `arm64`.
- Host OS: macOS `26.6.2`; upstream v0.13 declares macOS 27 arm64 only. This
  fork now has a separate macOS 26 capability record.
- The host has no system `uv`; the Codex-bundled Python 3.12.14 is used to
  install uv and create the project environments.

## Implementation sequence

1. Stash the pre-upgrade worktree, including untracked files.
2. Synchronize the worktree to the upstream v0.13.2 archive and commit it locally.
3. Run formatting, lint, and unit tests.
4. Run native `doctor`/manual checks without bypassing the platform gate.
5. Extend the measured gate only after the Darwin capability probe passes.
6. Record toolchain and service-manager limitations and leave the checkout
   reproducible.

## Risks and rollback

- The upstream Mac service installer was designed around macOS 27 evidence.
  Rollback is the local commit before the fork gate change plus `stash@{0}`.
- Existing local changes are recoverable with `git stash apply stash@{0}`.

## Acceptance criteria

- The checkout reports ServerFS `0.13.2` and has the upstream native Mac files.
- Root and Agent Bridge locked environments install successfully.
- Ruff and pytest results are recorded.
- The native gate passes on this Apple Silicon macOS 26.6.2 host only after the
  measured checks recorded in `docs/phase-macos26-capability-2026-10.md`.
- Unsupported architectures, Rosetta, macOS 25-or-earlier and macOS 28+ still
  fail closed.

## Verification evidence

- `uv sync --frozen` completed for the root project with Python 3.12.14.
- `uv sync --project agent_bridge --frozen` completed for the Bridge with the
  locked Claude and Qoder SDKs.
- Root Ruff check passed; root format check reported 318 files already formatted.
- Agent Bridge tests passed: 337 passed, 39 skipped.
- `docker build --tag serverfs-mcp:mac-adapt-v0.13.2 .` passed and the image
  reports ServerFS `0.13.2`.
- Linux container smoke started the v0.13.2 HTTP server and rejected an invalid
  Host header as expected.
- macOS `.venv/bin/serverfs --version` reports `0.13.2`; `service status` and
  `doctor --config serverfs.toml.example` run through the macOS 26 gate. The
  example config intentionally reports missing Windows placeholder roots. A
  no-credential install correctly fails closed because
  `CONTROL_PLANE_TUNNEL_ID` is absent.
- Darwin targeted tests pass: `49 passed`.
- The macOS 26 capability evidence is recorded in
  `docs/phase-macos26-capability-2026-10.md`.
- Root Ruff, format check and pytest pass. Agent Bridge Ruff, format check and
  pytest pass from `agent_bridge/` (`337 passed, 39 skipped`).
- A wheel was built successfully with `pip wheel . --no-deps` and reports
  version `0.13.2`.
- The ServiceManagement companion builds and passes strict codesign when
  `SDKROOT` selects the installed macOS 26.5 SDK. The default CLT SDK is
  macOS 27.0 and is incompatible with the installed Swift 6.3.3 compiler;
  this is a local toolchain mismatch, not a runtime gate failure.
- `docker compose config` and the site build are **Not verified** here:
  Docker is not installed and the site dependencies were not available.

## Status and next action

The source upgrade and experimental macOS 26 adaptation are complete. Real
Login Items approval and reboot/login recovery remain operator acceptance steps
outside automated verification.
