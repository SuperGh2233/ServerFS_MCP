"""Read authenticated Unix-domain peer credentials on Linux and macOS."""

from __future__ import annotations

import ctypes
import errno
import socket
import struct
import sys


class PeerCredentialsUnavailable(OSError):
    """The host kernel could not provide credentials for a local socket peer."""


def peer_uid_gid(sock: socket.socket) -> tuple[int, int]:
    """Return the kernel-reported UID/GID of a connected Unix socket peer.

    Linux exposes ``SO_PEERCRED``. macOS exposes the equivalent ``getpeereid(2)``
    call but Python does not wrap it on all supported versions.
    """
    if hasattr(socket, "SO_PEERCRED"):
        try:
            raw = sock.getsockopt(
                socket.SOL_SOCKET,
                socket.SO_PEERCRED,
                struct.calcsize("3i"),
            )
        except OSError as exc:
            raise PeerCredentialsUnavailable(exc.errno, "peer credentials unavailable") from exc
        _pid, uid, gid = struct.unpack("3i", raw)
        return uid, gid

    if sys.platform == "darwin":
        return _darwin_peer_uid_gid(sock.fileno())

    raise PeerCredentialsUnavailable(errno.ENOTSUP, "peer credentials unavailable")


def _darwin_peer_uid_gid(fd: int) -> tuple[int, int]:
    libc = ctypes.CDLL(None, use_errno=True)
    try:
        getpeereid = libc.getpeereid
    except AttributeError as exc:
        raise PeerCredentialsUnavailable(errno.ENOTSUP, "peer credentials unavailable") from exc
    getpeereid.argtypes = [
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_uint),
        ctypes.POINTER(ctypes.c_uint),
    ]
    getpeereid.restype = ctypes.c_int
    uid = ctypes.c_uint()
    gid = ctypes.c_uint()
    if getpeereid(fd, ctypes.byref(uid), ctypes.byref(gid)) != 0:
        error = ctypes.get_errno() or errno.EIO
        raise PeerCredentialsUnavailable(error, "peer credentials unavailable")
    return uid.value, gid.value
