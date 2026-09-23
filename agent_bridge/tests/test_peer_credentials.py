from __future__ import annotations

import os
import socket
import threading

from serverfs_agent_bridge.peer_credentials import peer_uid_gid


def test_peer_uid_gid_reports_kernel_credentials_for_same_user(tmp_path) -> None:
    socket_path = tmp_path / "peer.sock"
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    listener.bind(str(socket_path))
    listener.listen(1)
    result: list[tuple[int, int]] = []

    def accept_peer() -> None:
        connection, _ = listener.accept()
        with connection:
            result.append(peer_uid_gid(connection))

    thread = threading.Thread(target=accept_peer, daemon=True)
    thread.start()
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        client.connect(str(socket_path))
    finally:
        client.close()
    thread.join(timeout=5)
    listener.close()

    assert not thread.is_alive()
    assert result == [(os.getuid(), os.getgid())]
