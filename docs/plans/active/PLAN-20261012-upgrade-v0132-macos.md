# REQ/PLAN: Upgrade the local Mac deployment to ServerFS v0.13.2

## Problem and business outcome

The local `mac-adapt` checkout is based on v0.7 and needs the current upstream
ServerFS release plus a verified native macOS run path.

## Scope

- Replace the checkout contents with upstream `main` at v0.13.2.
- Preserve the pre-upgrade uncommitted local work in Git stash.
- Install the two locked Python environments and run the repository quality gates.
- Exercise the supported native CLI diagnostics and manual stdio path where this
  host permits it.

## Non-goals

- Claim persistent macOS support outside the upstream measured boundary.
- Publish, push, tag, or release anything on GitHub.
- Put credentials in tracked files or documentation.

## Current evidence and constraints

- Upstream archive commit: `567f1c2f94ff62f58710992557a6a63313ba370e`.
- Upstream version: `0.13.2`.
- Host architecture: `arm64`.
- Host OS: macOS `26.6.2`; upstream v0.13 declares macOS 27 arm64 only.
- The host has no system `uv`; the Codex-bundled Python 3.12.14 is used to
  install uv and create the project environments.

## Implementation sequence

1. Stash the pre-upgrade worktree, including untracked files.
2. Synchronize the worktree to the upstream v0.13.2 archive and commit it locally.
3. Run formatting, lint, and unit tests.
4. Run native `doctor`/manual checks without bypassing the platform gate.
5. Record any platform-bound limitation and leave the checkout reproducible.

## Risks and rollback

- The upstream Mac service installer may reject macOS 26 by design. Rollback is
  the local commit before `e321fb7` plus `stash@{0}`.
- Existing local changes are recoverable with `git stash apply stash@{0}`.

## Acceptance criteria

- The checkout reports ServerFS `0.13.2` and has the upstream native Mac files.
- Root and Agent Bridge locked environments install successfully.
- Ruff and pytest results are recorded.
- A native run attempt either passes or reports the exact upstream platform gate;
  no unsupported bypass is introduced.

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
- macOS `serverfs service status`, `serverfs agent-bridge status`, and
  `serverfs doctor --config serverfs.toml.example` ran. Doctor reported the
  measured host limitation: macOS 26.6.2 is outside the upstream macOS 27 gate.
- The full root pytest run on this host cannot execute the Darwin backend under
  the declared boundary: 881 passed, 367 skipped, 256 failed, 20 errors, with
  failures rooted in `NATIVE_PLATFORM_UNSUPPORTED: macOS version is not 27.x`.

## Status and next action

Completed for the supported upgrade and the available host checks. Native
persistent Mac service verification remains blocked by the upstream macOS 27
platform gate; run `serverfs service install` on an Apple Silicon macOS 27 host
to complete that final live check.
