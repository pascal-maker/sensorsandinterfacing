import gradio as gr#import gradio library
import smbus

i2c = smbus.SMBus(1)#set i2c bus
ADC_ADDRESS = 0x48#set i2c address

# ADS7830 command bytes — same pattern as RGB script
# CH5: C2:C1:C0=110 → 1_110_01_00 = 0xE4
# CH6: C2:C1:C0=011 → 1_011_01_00 = 0xB4    the commands are instructions for the ADC chip to read the voltage from the pots
command_for_channel_5 = 0xE4  # AIN5 → Y-axis#the command to read the y axis from the ADC
command_for_channel_6 = 0xB4  # AIN6 → X-axis#the command to read the x axis from the ADC

pot_labels = ["X axis", "Y axis"]#the labels for the pots to display on the graph

def read_adc(command):#function to read the adc 
    i2c.write_byte(ADC_ADDRESS, command)#write the command to the ADC
    i2c.read_byte(ADC_ADDRESS)       # discard stale conversion  the first read after a write returns the previous conversion
    return i2c.read_byte(ADC_ADDRESS)#read the adc value return the value in 0-255 range

def update_bars():#update the bars
    x = read_adc(command_for_channel_6)  # X-axis on AIN6
    y = read_adc(command_for_channel_5)  # Y-axis on AIN5

    result = ""#the result string that will display the bars 
    bar_length = 20#the length of the bars
    for label, value in zip(pot_labels, [x, y]):#loop through the pots
        filled  = int((value / 255) * bar_length)#calculate the number of filled blocks
        bar     = "█" * filled + "░" * (bar_length - filled)#create the bar with filled and empty blocks
        percent = int(value / 255 * 100)#calculate the percentage
        result += f"**{label}:** |{bar}| {percent}%\n\n"
    return result

with gr.Blocks() as demo:#create the gradio interface
    gr.Markdown("## Realtime Joystick Monitor")#display the title
    text_display = gr.Markdown()#display the bars 
    timer = gr.Timer(value=0.5)#set the timer
    timer.tick(fn=update_bars, outputs=text_display)#call the update_bars function every 0.5 seconds

demo.launch()
