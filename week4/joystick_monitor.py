import gradio as gr
import smbus

i2c = smbus.SMBus(1)
ADC_ADDRESS = 0x48

# ADS7830 command bytes — same pattern as RGB script
# CH5: C2:C1:C0=110 → 1_110_01_00 = 0xE4
# CH6: C2:C1:C0=011 → 1_011_01_00 = 0xB4
command_for_channel_5 = 0xE4  # AIN5 → Y-axis
command_for_channel_6 = 0xB4  # AIN6 → X-axis

pot_labels = ["X axis", "Y axis"]

def read_adc(command):
    i2c.write_byte(ADC_ADDRESS, command)
    i2c.read_byte(ADC_ADDRESS)       # discard stale conversion
    return i2c.read_byte(ADC_ADDRESS)

def update_bars():
    x = read_adc(command_for_channel_6)  # X-axis on AIN6
    y = read_adc(command_for_channel_5)  # Y-axis on AIN5

    result = ""
    bar_length = 20
    for label, value in zip(pot_labels, [x, y]):
        filled  = int((value / 255) * bar_length)
        bar     = "█" * filled + "░" * (bar_length - filled)
        percent = int(value / 255 * 100)
        result += f"**{label}:** |{bar}| {percent}%\n\n"
    return result

with gr.Blocks() as demo:
    gr.Markdown("## Realtime Joystick Monitor")
    text_display = gr.Markdown()
    timer = gr.Timer(value=0.5)
    timer.tick(fn=update_bars, outputs=text_display)

demo.launch()
