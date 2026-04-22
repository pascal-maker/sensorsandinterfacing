import smbus
import time

#LCD constants
I2C_ADDR = 0x27#address of the lcd
LCD_WIDTH = 16#width of the lcd 16 characters per line
LCD_CHR = 1#character mode send a normal character
LCD_CMD = 0#command mode send a lcd command

LCD_LINE_1 = 0x80#first line of the lcd
LCD_LINE_2 = 0xC0#second line of the lcd

ENABLE = 0b00000100#enable pin to toggle the enable pin the lcd so it reads data
RS = 0b00000001#register select pin 0 command mode 1 character mode
ADC_ADDR = 0x48#address of the adc
X_CHANNEL = 5#joystick x channel



bus = smbus.SMBus(1)#initialize the i2c bus

def lcd_toggle_enable(bits):#toggle the enable pin so the lcd reads the data
    time.sleep(0.0005)#wait a tiny bit
    bus.write_byte(I2C_ADDR, bits | ENABLE)#set enable high
    time.sleep(0.0005)#wait a tiny bit
    bus.write_byte(I2C_ADDR, bits & ~ENABLE)#set enable low
    time.sleep(0.0005)#wait a tiny bit

def lcd_send_byte(bits, mode):#send a byte to the lcd
    high_bits = mode | (bits & 0xF0) | 0x08#split the byte into two nibbles
    low_bits = mode | ((bits << 4) & 0xF0) | 0x08#split the byte into two nibbles
    bus.write_byte(I2C_ADDR, high_bits)#send the upper 4 bits of the byte
    lcd_toggle_enable(high_bits)#toggle the enable pin
    bus.write_byte(I2C_ADDR, low_bits)#send the lower 4 bits of the byte
    lcd_toggle_enable(low_bits)#toggle the enable pin
    

def lcd_init():#initialize the lcd set 4 bit mode turn display on set 2 lines clear the display
    lcd_send_byte(0x33, LCD_CMD)#function set 8 bit mode
    lcd_send_byte(0x32, LCD_CMD)#function set 8 bit mode
    lcd_send_byte(0x06, LCD_CMD)#entry mode set increment cursor
    lcd_send_byte(0x0C, LCD_CMD)#display on cursor off blink off
    lcd_send_byte(0x28, LCD_CMD)#function set 4 bit mode 2 lines 5x8 dots
    lcd_send_byte(0x01, LCD_CMD)#clear the lcd
    time.sleep(0.0005)    

def lcd_string(message, line):#make sure the message is 16 characters long
    message = message.ljust(LCD_WIDTH, " ")# make sure the message is 16 characters long
    lcd_send_byte(line, LCD_CMD)#send the line to the lcd
    for ch in message[:LCD_WIDTH]:#iterate through the message and send each character to the lcd
        lcd_send_byte(ord(ch), LCD_CHR)#send the character to the lcd

def lcd_clear():#clear the lcd
    lcd_send_byte(0x01, LCD_CMD)#clear the lcd
    time.sleep(0.0005)    

def ads7830_command(channel):#send a command to the adc
    return 0x84 | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)#rearraing th ebtis of the chnanel number intot he fromat requried by the ADS7830
#creates the correct coommadn byte fdor the ADC so the rapberry pu can tell the adc whichbanolog channel msut eb read.
def read_adc(channel):#read the value from the adc
    cmd = ads7830_command(channel)#send the command to the adc
    bus.write_byte(ADC_ADDR, cmd)#send the command to the adc
    time.sleep(0.01)#wait a tiny bit
    return bus.read_byte(ADC_ADDR)#read the value from the adc

def make_bar(value):#make a bar graph
    blocks = int((value/255)*16)  #calculate the number of blocks to display
    return "#" * blocks + "-" * (16-blocks)#return the bar
def wait_or_stop(stop_event,seconds):
    steps = int(seconds/0.1)
    for _ in range(steps):
        if stop_event.is_set():
            return
        time.sleep(0.1)
def run(stop_event):
    lcd_init()
    while not stop_event.is_set():
        x_val = read_adc(X_CHANNEL)#read the current X-axis joystick value and store it in x_val depening on mapping lefy -> mayble low value center around milddle right maybe high value
        line1 = make_bar(x_val)#make a bar graph the raw avlue joystick value and tuern tonto a afke elcd abr graph
        line2 = f"VRX=> {x_val}"#format the value to be displayed on the lcd make a textstrign showing rhe actuald ecminal value
        lcd_string(line1, LCD_LINE_1)#display the formatted value on the lcd
        lcd_string(line2, LCD_LINE_2)#display the formatted value on the lcd
        time.sleep(0.1)#wait a tiny bit
    lcd_clear()

    