# Button page — live GPIO input monitor.
#
# Uses a gr.Timer that fires every 100 ms to poll the ButtonService.
# gr.skip() is returned when the state hasn't changed so Gradio doesn't
# push a redundant update to the browser — keeps network traffic minimal.
from __future__ import annotations

import atexit
import os

import gradio as gr

from hardware.basic_button import ButtonService

# Pin can be overridden at runtime via environment variable
_PIN = int(os.getenv("FREENOVE_BUTTON_PIN", "26"))

# Lazy singleton — GPIO is only initialised when the first request arrives,
# not at import time, so importing this module never touches hardware.
_service: ButtonService | None = None


def _get() -> ButtonService:
    global _service
    if _service is None:
        _service = ButtonService(_PIN, debounce_seconds=0.05)
        atexit.register(_service.cleanup)   # release GPIO cleanly on exit
    return _service


def _read(last: bool | None) -> tuple[str, str, bool]:
    """Poll the button and return updated UI values (or gr.skip() if unchanged)."""
    pressed = _get().is_pressed()
    if last is not None and pressed == last:
        # State unchanged — tell Gradio to skip the update (no re-render)
        return gr.skip(), gr.skip(), last
    return ("Pressed" if pressed else "Released"), ("LOW" if pressed else "HIGH"), pressed


def create(demo: gr.Blocks) -> None:
    """Add the Button tab to the shared Blocks app."""
    with gr.Tab("Button"):
        gr.Markdown(
            f"## Button Input (GPIO{_PIN}, pull-up)\n"
            "Reads LOW when pressed — GPIO uses a pull-up resistor so the line is HIGH by default."
        )
        with gr.Row():
            gr.Textbox(label="Pin",        value=f"GPIO{_PIN}", interactive=False)
            state_box = gr.Textbox(label="State",      value="Reading...", interactive=False)
            level_box = gr.Textbox(label="GPIO Level", value="Reading...", interactive=False)

        last  = gr.State(value=None)   # stores last known pressed state between ticks
        timer = gr.Timer(0.1)          # fires every 100 ms

        # Fire once on page load to show an immediate reading
        demo.load(_read, inputs=last, outputs=[state_box, level_box, last],
                  show_progress="hidden", queue=False)
        # Then keep polling every 100 ms
        timer.tick(_read, inputs=last, outputs=[state_box, level_box, last],
                   show_progress="hidden", queue=False)
