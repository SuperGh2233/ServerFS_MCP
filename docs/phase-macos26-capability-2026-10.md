# macOS 26 Fork Capability Verification

**Date:** 2026-10-12
**Machine:** Apple Silicon Mac, native `arm64`
**OS:** macOS 26.6.2 (Darwin 25.6.0), `sysctl.proc_translated = 0`
**Python:** CPython 3.12.14 (`.venv`)
**Filesystem:** local APFS

This is the measured evidence for the fork's experimental macOS 26 gate. It
does not change the upstream v0.13.2 claim, which remains macOS 27.

| Primitive | Result |
| --- | --- |
| `os.open` with `O_NOFOLLOW` | PASS; symlink rejected as `SymlinkNotAllowedError` |
| Descriptor-relative traversal | PASS; nested directory and file opened through directory FDs |
| `fcopyfile(COPYFILE_METADATA)` | PASS; destination content stayed unchanged and mode `0604` plus xattr were preserved |
| `getpeereid` | PASS; AF_UNIX peer euid/egid matched the current user |
| `flock` | PASS; exclusive non-blocking lock acquired and released |
| `_CS_DARWIN_USER_TEMP_DIR` | PASS; returned private current-user runtime directory |
| Darwin AF_UNIX path budget | PASS; socket bound at 68 bytes, under the 103-byte limit |

The Darwin backend tests passed **49 passed** on this host, including the
macOS 26/27 gate, symlink refusal, metadata preservation and lifecycle paths.

The ServiceManagement companion also built and passed `plutil` and strict
codesign verification with the installed macOS 26.5 SDK:

```text
SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk \
  bash native/macos/service_manager/build.sh /tmp/serverfs-service-build-26
```

The default CommandLineTools SDK selection currently points at macOS 27.0,
whose Swift 6.4 module is newer than the installed Swift 6.3.3 compiler. That
toolchain mismatch is an environment issue; selecting the installed 26.5 SDK
produced a valid arm64 app bundle.
