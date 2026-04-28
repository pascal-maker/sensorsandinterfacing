# Buzzer page — controls for both the active buzzer (GPIO 12) and passive buzzer (GPIO 14).
#
# Active buzzer:  simple ON / OFF / timed beep.
#                 The buzzer contains its own oscillator so we only switch the pin HIGH/LOW.
#
# Passive buzzer: frequency + duration + duty-cycle sliders driving a PWM signal.
#                 The coil needs the PWM waveform to vibrate — the frequency IS the pitch.
#
# Tone playback runs in a daemon thread so the Gradio server stays responsive
# while the buzzer is playing (play_tone blocks for `duration` seconds).
from __future__ import annotations

import atexit
import os
import threading

import gradio as gr

from hardware.basic_buzzer import ActiveBuzzerService, PassiveBuzzerService

# Pins can be overridden at runtime via environment variables
_ACTIVE_PIN  = int(os.getenv("FREENOVE_ACTIVE_BUZZER_PIN",  "12"))
_PASSIVE_PIN = int(os.getenv("FREENOVE_PASSIVE_BUZZER_PIN", "14"))

# Lazy singletons — hardware is only initialised on first use
_active:  ActiveBuzzerService  | None = None
_passive: PassiveBuzzerService | None = None


def _get_active() -> ActiveBuzzerService:
    global _active
    if _active is None:
        _active = ActiveBuzzerService(_ACTIVE_PIN)
        atexit.register(_active.cleanup)
    return _active


def _get_passive() -> PassiveBuzzerService:
    global _passive
    if _passive is None:
        _passive = PassiveBuzzerService(_PASSIVE_PIN)
        atexit.register(_passive.cleanup)
    return _passive


# ------------------------------------------------------------------
# Active buzzer callbacks
# ------------------------------------------------------------------

def _active_on() -> str:
    try:
        _get_active().on()
        return "ON"
    except Exception as e:
        return f"Error: {e}"

def _active_off() -> str:
    try:
        _get_active().off()
        return "OFF"
    except Exception as e:
        return f"Error: {e}"

def _active_beep(duration: float) -> str:
    """Start a timed beep in a background thread so the UI stays responsive."""
    try:
        threading.Thread(target=_get_active().beep, args=(duration,), daemon=True).start()
        return f"Beep {duration:.2f}s"
    except Exception as e:
        return f"Error: {e}"


# ------------------------------------------------------------------
# Passive buzzer callbacks
# ------------------------------------------------------------------

def _passive_play(freq: float, duration: float, duty: float) -> str:
    """Start tone playback in a background thread."""
    try:
        threading.Thread(
            target=_get_passive().play_tone, args=(freq, duration, duty), daemon=True
        ).start()
        return f"Playing {freq:.0f} Hz for {duration:.1f}s"
    except Exception as e:
        return f"Error: {e}"

def _passive_stop() -> str:
    try:
        _get_passive().stop()
        return "Stopped"
    except Exception as e:
        return f"Error: {e}"


# ------------------------------------------------------------------
# UI
# ------------------------------------------------------------------

def create(demo: gr.Blocks) -> None:  # noqa: ARG001
    """Add the Active Buzzer and Passive Buzzer tabs to the shared Blocks app."""

    with gr.Tab("Active Buzzer"):
        gr.Markdown(
            f"## Active Buzzer (GPIO{_ACTIVE_PIN})\n"
            "Has its own oscillator — just switch it ON/OFF, or trigger a timed beep."
        )
        status = gr.Textbox(label="Status", interactive=False)
        with gr.Row():
            gr.Button("ON",  variant="primary").click(_active_on,  outputs=status)
            gr.Button("OFF", variant="stop"   ).click(_active_off, outputs=status)
        with gr.Row():
            dur = gr.Slider(0.05, 2.0, value=0.2, step=0.05, label="Beep Duration (s)")
            gr.Button("Beep", variant="secondary").click(_active_beep, inputs=dur, outputs=status)

    with gr.Tab("Passive Buzzer"):
        gr.Markdown(
            f"## Passive Buzzer (GPIO{_PASSIVE_PIN})\n"
            "Needs a PWM signal — frequency sets the pitch, duty cycle sets the drive strength."
        )
        pstatus = gr.Textbox(label="Status", interactive=False)
        with gr.Row():
            freq = gr.Slider(100,  4000, value=440, step=10,  label="Frequency (Hz)")
            dur2 = gr.Slider(0.1,  3.0,  value=0.5, step=0.1, label="Duration (s)")
            duty = gr.Slider(1,    99,   value=50,  step=1,   label="Duty Cycle (%)")
        with gr.Row():
            gr.Button("Play", variant="primary").click(_passive_play, inputs=[freq, dur2, duty], outputs=pstatus)
            gr.Button("Stop", variant="stop"   ).click(_passive_stop, outputs=pstatus)
