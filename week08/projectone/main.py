# Entry point for the GPIO Data Visualization dashboard.
# Imports each page module and registers its tab into the shared Gradio Blocks app.
from __future__ import annotations

import gradio as gr

# Each page module exposes a create(demo) function that adds its own Tab to the app
from interface.pages import button, buzzer, lcd, system

# gr.Blocks is Gradio's low-level layout API — lets us compose multiple tabs freely
with gr.Blocks(title="GPIO Data Visualization") as demo:
    gr.Markdown("# GPIO Data Visualization")

    # Each call adds one or more tabs to the shared Blocks context
    button.create(demo)   # Button input tab
    buzzer.create(demo)   # Active + Passive buzzer tabs
    lcd.create(demo)      # LCD display tab
    system.create(demo)   # System control tab (reboot / shutdown via daemon)

if __name__ == "__main__":
    # Bind to all interfaces so the dashboard is reachable from the network, not just localhost
    demo.launch(server_name="0.0.0.0", server_port=7860)
