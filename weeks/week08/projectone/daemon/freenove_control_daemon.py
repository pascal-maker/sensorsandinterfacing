#!/usr/bin/env python3
# Host-side control daemon.
#
# Problem: Docker containers are isolated — code inside a container cannot call
# systemctl, reboot the host, or stop other services directly.
#
# Solution: this daemon runs ON THE HOST (managed by freenove-control.service).
# It listens on a Unix socket. The Docker container sends a short command string;
# the daemon executes the corresponding system action on the host.
#
# The socket is owned by root:docker with mode 0660, so any process inside a
# Docker container running in the docker group can connect without needing root.
# The socket path is bind-mounted into the container via docker-compose.yml volumes.
from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
from contextlib import suppress
from pathlib import Path
from shlex import quote as shlex_quote

# Socket path — must match FREENOVE_CONTROL_SOCKET in the container environment
SOCKET_PATH  = Path(os.getenv("FREENOVE_CONTROL_SOCKET", "/run/freenove-control/control.sock"))
# The systemd service name the daemon can stop/restart on behalf of the container
SERVICE_NAME = os.getenv("FREENOVE_SERVICE_NAME", "gradio-demo.service")


def _run_detached(args: list[str], delay_seconds: float = 1.0) -> None:
    """Run a shell command in a completely detached child process.

    The delay gives the daemon time to send its response back to the caller
    before the system action (e.g. reboot) actually fires.
    """
    if delay_seconds > 0:
        # Wrap the command in a shell sleep so the daemon can reply first
        cmd = " ".join(shlex_quote(p) for p in args)
        args = ["/bin/sh", "-c", f"sleep {delay_seconds:.1f}; {cmd}"]
    subprocess.Popen(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,   # detach from this process's session so it survives daemon exit
    )


def _handle(command: str) -> str:
    """Dispatch a command string and return the response to send back."""
    normalized = command.strip().upper()

    if normalized == "PING":
        # Health check — no side effects
        return "OK pong"

    if normalized == "REBOOT":
        _run_detached(["systemctl", "reboot"])
        return "OK reboot requested"

    if normalized in {"SHUTDOWN", "POWEROFF"}:
        _run_detached(["systemctl", "poweroff"])
        return "OK shutdown requested"

    if normalized == "SERVICE_STOP":
        _run_detached(["systemctl", "stop", SERVICE_NAME])
        return f"OK stop requested for {SERVICE_NAME}"

    if normalized == "SERVICE_RESTART":
        _run_detached(["systemctl", "restart", SERVICE_NAME])
        return f"OK restart requested for {SERVICE_NAME}"

    return "ERR unsupported command"


def main() -> int:
    # Ensure the socket directory exists (created by systemd RuntimeDirectory= on service start)
    SOCKET_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Remove a stale socket file from a previous run (bind would fail otherwise)
    with suppress(FileNotFoundError):
        SOCKET_PATH.unlink()

    # Create and bind the Unix stream socket
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(str(SOCKET_PATH))
    os.chmod(SOCKET_PATH, 0o660)   # rw-rw---- so the docker group can connect
    server.listen(8)

    # Transfer ownership to root:docker so container processes (docker group) can connect
    try:
        import grp
        gid = grp.getgrnam("docker").gr_gid
        os.chown(SOCKET_PATH, 0, gid)
    except Exception:
        pass   # non-fatal: falls back to 0660 with root:root

    # Graceful shutdown on SIGTERM / SIGINT
    stop = False

    def _on_signal(signum, frame):  # type: ignore[no-untyped-def]
        nonlocal stop
        stop = True

    signal.signal(signal.SIGTERM, _on_signal)
    signal.signal(signal.SIGINT,  _on_signal)

    print(f"Listening on {SOCKET_PATH}", flush=True)

    # Main accept loop — one connection at a time, one command per connection
    while not stop:
        try:
            server.settimeout(1.0)   # wake up periodically to check the stop flag
            conn, _ = server.accept()
        except socket.timeout:
            continue

        with conn:
            data = conn.recv(256)       # commands are short strings
            if not data:
                continue
            response = _handle(data.decode("utf-8", "ignore"))
            conn.sendall((response + "\n").encode("utf-8"))

    # Clean up the socket file on exit
    with suppress(FileNotFoundError):
        SOCKET_PATH.unlink()
    return 0


if __name__ == "__main__":
    sys.exit(main())
