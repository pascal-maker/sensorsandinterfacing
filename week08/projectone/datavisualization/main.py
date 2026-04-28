from __future__ import annotations

import atexit
import os
import threading

import gradio as gr#

from buttonservice import ButtonService#import the button service
from buzzerservice import ActiveBuzzerService, PassiveBuzzerService#import the buzzer service
from lcdservice import LCDService#import the lcd service

BUTTON_PIN      = int(os.getenv("FREENOVE_BUTTON_PIN",       "26"))#Default button pin
ACTIVE_BZ_PIN   = int(os.getenv("FREENOVE_ACTIVE_BUZZER_PIN", "12"))#Default active buzzer pin
PASSIVE_BZ_PIN  = int(os.getenv("FREENOVE_PASSIVE_BUZZER_PIN", "14"))#Default passive buzzer pin
LCD_ADDR        = int(os.getenv("FREENOVE_LCD_ADDR",          "0x27"), 16)#Default LCD address

_button: ButtonService | None = None#Button service instance
_active_bz: ActiveBuzzerService | None = None#Active buzzer service instance
_passive_bz: PassiveBuzzerService | None = None#Passive buzzer service instance
_lcd: LCDService | None = None#LCD service instance


def _get_button() -> ButtonService:#Get button service instance
    global _button#global button service instance
    if _button is None:#check if button service instance is None
        _button = ButtonService(BUTTON_PIN, debounce_seconds=0.05)#create button service instance
        atexit.register(_button.cleanup)#register button cleanup
    return _button


def _get_active_bz() -> ActiveBuzzerService:#Get active buzzer service instance
    global _active_bz#global active buzzer service instance
    if _active_bz is None:#check if active buzzer service instance is None
        _active_bz = ActiveBuzzerService(ACTIVE_BZ_PIN)#create active buzzer service instance
        atexit.register(_active_bz.cleanup)#register active buzzer cleanup
    return _active_bz


def _get_passive_bz() -> PassiveBuzzerService:#Get passive buzzer service instance
    global _passive_bz#global passive buzzer service instance
    if _passive_bz is None:#check if passive buzzer service instance is None
        _passive_bz = PassiveBuzzerService(PASSIVE_BZ_PIN)#create passive buzzer service instance
        atexit.register(_passive_bz.cleanup)#register passive buzzer cleanup
    return _passive_bz


def _get_lcd() -> LCDService:#Get LCD service instance
    global _lcd#global LCD service instance
    if _lcd is None:#check if LCD service instance is None
        _lcd = LCDService(i2c_addr=LCD_ADDR)#create LCD service instance
        atexit.register(_lcd.cleanup)#register LCD cleanup
    return _lcd


# --- Button ---

def read_button(last_state: bool | None) -> tuple[str, str, bool]:#Read button state
    btn = _get_button()#get button service instance
    pressed = btn.is_pressed()#check if button is pressed
    if last_state is not None and pressed == last_state:
        return gr.skip(), gr.skip(), last_state#skip if button state is the same as last state
    return ("Pressed" if pressed else "Released"), ("LOW" if pressed else "HIGH"), pressed#return button state


# --- Active buzzer ---

def active_bz_on() -> str:#Turn on active buzzer
    try:
        _get_active_bz().on()#turn on active buzzer
        return "ON"
    except Exception as exc:#handle exception
        return f"Error: {exc}"#return error message


def active_bz_off() -> str:#Turn off active buzzer
    try:
        _get_active_bz().off()#turn off active buzzer
        return "OFF"
    except Exception as exc:#handle exception
        return f"Error: {exc}"#return error message


def active_bz_beep(duration: float) -> str:#Beep active buzzer
    try:
        bz = _get_active_bz()#get active buzzer service instance
        threading.Thread(target=bz.beep, args=(duration,), daemon=True).start()
        return f"Beep {duration:.1f}s"
    except Exception as exc:#handle exception
        return f"Error: {exc}"#return error message


# --- Passive buzzer ---

def passive_bz_play(freq: float, duration: float, duty: float) -> str:#Play passive buzzer
    try:
        bz = _get_passive_bz()#get passive buzzer service instance
        threading.Thread(target=bz.play_tone, args=(freq, duration, duty), daemon=True).start()
        return f"Playing {freq:.0f} Hz for {duration:.1f}s"
    except Exception as exc:#handle exception
        return f"Error: {exc}"#return error message


def passive_bz_stop() -> str:#Stop passive buzzer
    try:
        _get_passive_bz().stop()#stop passive buzzer
        return "Stopped"
    except Exception as exc:#handle exception
        return f"Error: {exc}"#return error message


# --- LCD ---

def send_to_lcd(line1: str, line2: str) -> str:#Send to LCD
    try:
        _get_lcd().write(line1, line2)#send to LCD
        return "Sent to LCD"
    except Exception as exc:#handle exception
        return f"Error: {exc}"#return error message


def clear_lcd() -> str:#clear LCD
    try:
        _get_lcd().clear()#clear LCD
        return "Cleared"
    except Exception as exc:#handle exception
        return f"Error: {exc}"#return error message


# --- UI ---

with gr.Blocks(title="GPIO Data Visualization") as demo:
    gr.Markdown("# GPIO Data Visualization")#Markdown heading

    with gr.Tab("Button"):#Button tab
        gr.Markdown("## Button Input (GPIO26, pull-up)")#Markdown heading
        with gr.Row():#Row for button input
            gr.Textbox(label="Pin", value=f"GPIO{BUTTON_PIN}", interactive=False)#Text box for button pin
            btn_state_box  = gr.Textbox(label="State",      value="Reading...", interactive=False)#Text box for button state
            gpio_level_box = gr.Textbox(label="GPIO Level", value="Reading...", interactive=False)#Text box for GPIO level
        btn_last  = gr.State(value=None)#State for button
        btn_timer = gr.Timer(0.1)#Timer for button
        demo.load(read_button, inputs=btn_last, outputs=[btn_state_box, gpio_level_box, btn_last],#Load button
                  show_progress="hidden", queue=False)#Hide progress
        btn_timer.tick(read_button, inputs=btn_last, outputs=[btn_state_box, gpio_level_box, btn_last],#Tick button
                       show_progress="hidden", queue=False)#Hide progress

    with gr.Tab("Active Buzzer"):
        gr.Markdown(f"## Active Buzzer (GPIO{ACTIVE_BZ_PIN})\nHas its own oscillator — just switch it ON or OFF, or trigger a timed beep.")
        abz_status = gr.Textbox(label="Status", interactive=False)#Text box for active buzzer status
        with gr.Row():#Row for active buzzer
            gr.Button("ON",  variant="primary").click(active_bz_on,  outputs=abz_status)#Button to turn on active buzzer
            gr.Button("OFF", variant="stop"   ).click(active_bz_off, outputs=abz_status)#Button to turn off active buzzer
        with gr.Row():#Row for active buzzer
            beep_dur = gr.Slider(0.05, 2.0, value=0.2, step=0.05, label="Beep Duration (s)")#Slider for active buzzer duration
            gr.Button("Beep", variant="secondary").click(active_bz_beep, inputs=beep_dur, outputs=abz_status)

    with gr.Tab("Passive Buzzer"):
        gr.Markdown(f"## Passive Buzzer (GPIO{PASSIVE_BZ_PIN})\nNeeds a PWM signal — control pitch (frequency) and volume (duty cycle).")
        pbz_status = gr.Textbox(label="Status", interactive=False)#Text box for passive buzzer status
        with gr.Row():#Row for passive buzzer
            freq_slider  = gr.Slider(100,  4000, value=440, step=10,  label="Frequency (Hz)")#Slider for passive buzzer frequency
            dur_slider   = gr.Slider(0.1,  3.0,  value=0.5, step=0.1, label="Duration (s)")#Slider for passive buzzer duration
            duty_slider  = gr.Slider(1,    99,   value=50,  step=1,   label="Duty Cycle (%)")#Slider for passive buzzer duty cycle
        with gr.Row():#Row for passive buzzer
            gr.Button("Play",  variant="primary").click(passive_bz_play, inputs=[freq_slider, dur_slider, duty_slider], outputs=pbz_status)#Button to play passive buzzer
            gr.Button("Stop",  variant="stop"   ).click(passive_bz_stop, outputs=pbz_status)#Button to stop passive buzzer

    with gr.Tab("LCD"):
        gr.Markdown("## LCD Display (I2C, 16x2)")#Markdown heading
        line1_box = gr.Textbox(label="Line 1 (max 16 chars)", max_lines=1, placeholder="Hello World")#Text box for line 1 of LCD
        line2_box = gr.Textbox(label="Line 2 (max 16 chars)", max_lines=1, placeholder="Raspberry Pi")#Text box for line 2 of LCD
        lcd_status = gr.Textbox(label="Status", interactive=False)#Text box for LCD status
        with gr.Row():#Row for LCD
            gr.Button("Send to LCD", variant="primary").click(send_to_lcd, inputs=[line1_box, line2_box], outputs=lcd_status)#Button to send to LCD
            gr.Button("Clear LCD"                     ).click(clear_lcd,   outputs=lcd_status)#Button to clear LCD


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)#Launch demo
