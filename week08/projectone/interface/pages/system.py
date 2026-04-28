# System control page — sends commands to the host daemon over a Unix socket.
#
# Why a Unix socket?
#   The Gradio app runs inside Docker, which is isolated from the host OS.
#   Docker containers cannot call systemctl or reboot the host directly.
#   Instead, a small daemon runs on the HOST and listens on a Unix socket.
#   The socket file is bind-mounted into the container (see docker-compose.yml volumes).
#   Sending a command string over the socket tells the daemon to run the action.
#
# Supported commands: PING, REBOOT, SHUTDOWN, SERVICE_STOP, SERVICE_RESTART
from __future__ import annotations

import os
import socket

import gradio as gr

# Must match the path the daemon is bound to and the volume mount in docker-compose.yml
SOCKET_PATH = os.getenv("FREENOVE_CONTROL_SOCKET", "/run/freenove-control/control.sock")


def _send(command: str) -> str:
    """Open a short-lived connection to the daemon, send command, return the response."""
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.settimeout(3.0)              # don't hang if the daemon is unresponsive
            s.connect(SOCKET_PATH)
            s.sendall(command.encode("utf-8"))
            return s.recv(256).decode("utf-8").strip()
    except FileNotFoundError:
        # Socket doesn't exist — daemon is not running
        return "Error: daemon socket not found — is freenove-control.service running?"
    except Exception as exc:
        return f"Error: {exc}"


def create(demo: gr.Blocks) -> None:  # noqa: ARG001
    """Add the System tab to the shared Blocks app."""
    with gr.Tab("System"):
        gr.Markdown(
            "## System Control\n"
            "Sends commands to the host daemon over a Unix socket at "
            f"`{SOCKET_PATH}`."
        )
        response = gr.Textbox(label="Daemon Response", interactive=False)
        with gr.Row():
            # Ping is a safe health-check — no side effects
            gr.Button("Ping"           ).click(lambda: _send("PING"),            outputs=response)
            gr.Button("Restart Service").click(lambda: _send("SERVICE_RESTART"), outputs=response)
        with gr.Row():
            # Destructive actions — marked red with variant="stop"
            gr.Button("Reboot Pi",   variant="stop").click(lambda: _send("REBOOT"),   outputs=response)
            gr.Button("Shutdown Pi", variant="stop").click(lambda: _send("SHUTDOWN"),  outputs=response)
