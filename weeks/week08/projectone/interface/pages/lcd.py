# LCD page — sends text to the I2C LCD display.
#
# The HD44780 16x2 LCD is driven via a PCF8574 I2C backpack (address 0x27).
# Each line accepts up to 16 characters; longer strings are silently truncated.
# The service pads shorter strings with spaces so old characters are overwritten.
from __future__ import annotations

import atexit
import os

import gradio as gr

from hardware.basic_lcd import LCDService

# I2C address can be overridden if your backpack is soldered to 0x3F instead
_ADDR = int(os.getenv("FREENOVE_LCD_ADDR", "0x27"), 16)

# Lazy singleton — I2C bus is only opened on first use
_service: LCDService | None = None


def _get() -> LCDService:
    global _service
    if _service is None:
        _service = LCDService(i2c_addr=_ADDR)
        atexit.register(_service.cleanup)   # clear display and close bus on exit
    return _service


def _send(line1: str, line2: str) -> str:
    try:
        _get().write(line1, line2)
        return "Sent to LCD"
    except Exception as e:
        return f"Error: {e}"


def _clear() -> str:
    try:
        _get().clear()
        return "Cleared"
    except Exception as e:
        return f"Error: {e}"


def create(demo: gr.Blocks) -> None:  # noqa: ARG001
    """Add the LCD tab to the shared Blocks app."""
    with gr.Tab("LCD"):
        gr.Markdown(
            "## LCD Display (I2C, 16x2)\n"
            "I2C address 0x27 — HD44780 controller with PCF8574 backpack. "
            "Run `i2cdetect -y 1` if your display doesn't respond."
        )
        line1  = gr.Textbox(label="Line 1 (max 16 chars)", max_lines=1, placeholder="Hello World")
        line2  = gr.Textbox(label="Line 2 (max 16 chars)", max_lines=1, placeholder="Raspberry Pi")
        status = gr.Textbox(label="Status", interactive=False)
        with gr.Row():
            gr.Button("Send to LCD", variant="primary").click(_send,  inputs=[line1, line2], outputs=status)
            gr.Button("Clear LCD"                     ).click(_clear, outputs=status)
