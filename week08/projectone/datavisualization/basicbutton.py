from __future__ import annotations#

import atexit
import os

import gradio as gr

from buttonservice import ButtonService


DEFAULT_BUTTON_PIN = int(os.getenv("FREENOVE_BUTTON_PIN", "26"))
BUTTON: ButtonService | None = None
BUTTON_CLEANUP_REGISTERED = False


def get_button_service() -> ButtonService:
    global BUTTON, BUTTON_CLEANUP_REGISTERED

    if BUTTON is None:
        BUTTON = ButtonService(DEFAULT_BUTTON_PIN, debounce_seconds=0.05)
    if not BUTTON_CLEANUP_REGISTERED:
        atexit.register(BUTTON.cleanup)
        BUTTON_CLEANUP_REGISTERED = True
    return BUTTON


def read_button_state(last_state: bool | None) -> tuple[str, str, bool]:
    button = get_button_service()
    is_pressed = button.is_pressed()

    if last_state is not None and is_pressed == last_state:
        return gr.skip(), gr.skip(), last_state

    button_state = "Pressed" if is_pressed else "Released"
    gpio_level = "LOW" if is_pressed else "HIGH"
    return button_state, gpio_level, is_pressed


with gr.Blocks(title="GPIO Lab 1") as demo:
    gr.Markdown("## Button Input")
    gr.Markdown("GPIO26 uses pull-up wiring, so a pressed button reads LOW.")
    with gr.Row():
        button_pin = gr.Textbox(
            label="Button Pin",
            value=f"GPIO{DEFAULT_BUTTON_PIN}",
            interactive=False,
        )
        button_state = gr.Textbox(
            label="Button State",
            value="Reading...",
            interactive=False,
        )
        gpio_level = gr.Textbox(
            label="GPIO Level",
            value="Reading...",
            interactive=False,
        )
    button_last_state = gr.State(value=None)
    button_timer = gr.Timer(0.1)

    demo.load(
        read_button_state,
        inputs=button_last_state,
        outputs=[button_state, gpio_level, button_last_state],
        show_progress="hidden",
        queue=False,
    )
    button_timer.tick(
        read_button_state,
        inputs=button_last_state,
        outputs=[button_state, gpio_level, button_last_state],
        show_progress="hidden",
        queue=False,
    )


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
    )