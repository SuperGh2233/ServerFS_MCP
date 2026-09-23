"""File-descriptor extended-attribute helpers for Linux and macOS."""

from __future__ import annotations

import ctypes
import ctypes.util
import errno
import os
import sys

_NO_ATTRIBUTE_ERRNOS = frozenset(
    value
    for value in (getattr(errno, "ENODATA", None), getattr(errno, "ENOATTR", None))
    if value is not None
)


def list_fd(fd: int) -> list[str]:
    """Return extended-attribute names attached to an open file descriptor."""
    if hasattr(os, "listxattr"):
        return list(os.listxattr(fd))
    if sys.platform == "darwin":
        raw = _darwin_list(fd)
        return [os.fsdecode(name) for name in raw.rstrip(b"\0").split(b"\0") if name]
    raise OSError(errno.ENOTSUP, "extended attributes are not supported")


def get_fd(fd: int, name: str) -> bytes:
    """Read one extended attribute from an open file descriptor."""
    if hasattr(os, "getxattr"):
        return bytes(os.getxattr(fd, name))
    if sys.platform == "darwin":
        encoded = os.fsencode(name)
        size = _darwin_get(fd, encoded, None, 0)
        buffer = ctypes.create_string_buffer(max(size, 1))
        actual = _darwin_get(fd, encoded, buffer, size)
        return buffer.raw[:actual]
    raise OSError(errno.ENOTSUP, "extended attributes are not supported")


def set_fd(fd: int, name: str, value: bytes) -> None:
    """Write one extended attribute to an open file descriptor."""
    if hasattr(os, "setxattr"):
        os.setxattr(fd, name, value)
        return
    if sys.platform == "darwin":
        encoded = os.fsencode(name)
        buffer = ctypes.create_string_buffer(value or b"\0")
        _darwin_set(fd, encoded, buffer, len(value))
        return
    raise OSError(errno.ENOTSUP, "extended attributes are not supported")


def set_path(path: os.PathLike[str] | str, name: str, value: bytes) -> None:
    """Write an xattr by opening the path without following symlinks."""
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        set_fd(fd, name, value)
    finally:
        os.close(fd)


def get_path(path: os.PathLike[str] | str, name: str) -> bytes:
    """Read an xattr by opening the path without following symlinks."""
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        return get_fd(fd, name)
    finally:
        os.close(fd)


if sys.platform == "darwin":
    _libc = ctypes.CDLL(ctypes.util.find_library("c") or None, use_errno=True)
    _libc.flistxattr.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32]
    _libc.flistxattr.restype = ctypes.c_ssize_t
    _libc.fgetxattr.argtypes = [
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.c_uint32,
    ]
    _libc.fgetxattr.restype = ctypes.c_ssize_t
    _libc.fsetxattr.argtypes = [
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.c_uint32,
    ]
    _libc.fsetxattr.restype = ctypes.c_int


def _darwin_list(fd: int) -> bytes:
    size = _libc.flistxattr(fd, None, 0, 0)
    if size < 0:
        _raise_errno("listxattr")
    buffer = ctypes.create_string_buffer(max(size, 1))
    actual = _libc.flistxattr(fd, buffer, size, 0)
    if actual < 0:
        _raise_errno("listxattr")
    return buffer.raw[:actual]


def _darwin_get(fd: int, name: bytes, buffer, size: int) -> int:
    actual = _libc.fgetxattr(fd, name, buffer, size, 0, 0)
    if actual < 0:
        _raise_errno("getxattr")
    return actual


def _darwin_set(fd: int, name: bytes, buffer, size: int) -> None:
    result = _libc.fsetxattr(fd, name, buffer, size, 0, 0)
    if result != 0:
        _raise_errno("setxattr")


def _raise_errno(operation: str) -> None:
    error = ctypes.get_errno() or errno.EIO
    raise OSError(error, f"{operation} failed")
