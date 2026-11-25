# Fork-specific contributions

This repository is a personal fork of [NTLx/ServerFS_MCP](https://github.com/NTLx/ServerFS_MCP), based on upstream **v0.13.2**. The upstream project and its stable platform-support claims remain the source of truth for upstream behavior.

## Scope of this fork

The main fork-specific work is an **experimental macOS 26 capability gate**. It is not an upstream feature claim and does not replace the upstream macOS 27 support statement.

| Area | Fork-specific work | Evidence |
| --- | --- | --- |
| Darwin platform capability | macOS 26 detection and capability gating; Darwin-specific backend behavior | `src/serverfs_mcp/darwin_platform.py`, `darwin_backend.py` |
| Filesystem safety | Darwin libc and descriptor-relative I/O integration, native tunnel/platform adjustments | `darwin_libc.py`, `posix_fdio.py`, `native_tunnel.py` |
| CLI and diagnostics | Platform selection and doctor/capability reporting updates | `cli.py`, `doctor.py`, `backends.py` |
| Tests | Darwin backend regression coverage for the experimental gate and filesystem invariants | `tests/test_darwin_backend.py` |
| Acceptance evidence | macOS 26 capability report, macOS 27 CI-equivalence report, ServiceManagement feasibility probe | `docs/phase-macos26-capability-2026-10.md`, `docs/phase-i-macos-ci-local-equivalence-2026-10.md`, `docs/phase-v0.13.2-servicemanagement-probe-2026-10.md` |

## Measured validation

The macOS 26 capability report records an Apple Silicon arm64 host running macOS 26.6.2 (Darwin 25.6.0), native rather than Rosetta, with local APFS and CPython 3.12.14.

Measured primitives include:

- `O_NOFOLLOW` symlink rejection and descriptor-relative traversal;
- metadata-preserving `fcopyfile(COPYFILE_METADATA)`;
- AF_UNIX peer credential inspection and file locking;
- private user temporary-directory resolution;
- Darwin AF_UNIX socket path budget validation.

The report records **49 passing Darwin backend tests** on that host. The ServiceManagement companion also built and passed `plutil` and strict code-signature verification using the installed macOS 26.5 SDK.

A separate macOS 27 arm64 CI-equivalence report records all documented workflow steps passing on the acceptance machine.

## Explicit limitations

- macOS 26 support remains experimental and fork-specific.
- This work does not change upstream v0.13.2 support claims.
- A local acceptance run is not a claim that every hosted macOS runner, macOS point release, or distribution/signing path has been validated.
- External prebuilt app distribution, Developer ID signing/notarization, and reboot/login recovery remain separate release acceptance items.

## Upstream comparison

[Compare upstream v0.13.2 with this fork's main branch](https://github.com/NTLx/ServerFS_MCP/compare/v0.13.2...SuperGh2233:main).

This document separates fork-specific implementation and evidence from upstream functionality; it is not a claim of authorship over the upstream ServerFS MCP project.
