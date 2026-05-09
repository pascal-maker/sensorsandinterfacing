import smbus
import time
import threading#import threading to run the code in a separate thread 

# LCD constants
I2C_ADDR = 0x27#address of the lcd
LCD_WIDTH = 16#width of the lcd 16 characters per line
LCD_CHR = 1#character mode send a normal character
LCD_CMD = 0#command mode send a command

LCD_LINE_1 = 0x80#the first line of the lcd
LCD_LINE_2 = 0xC0#the second line of the lcd

ENABLE = 0b00000100#enable pin

# ADC constants
ADC_ADDR = 0x48#address of the adc
Y_CHANNEL = 4#joystick y channel the pontentiometer is wired to channel 4 of the adc

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
    time.sleep(0.002)#wait a tiny bit


def lcd_string(message, line):#make sure the message is 16 characters long
    message = message.ljust(LCD_WIDTH, " ")# make sure the message is 16 characters long
    lcd_send_byte(line, LCD_CMD)#send the line to the lcd

    for ch in message[:LCD_WIDTH]:#iterate through the message and send each character to the lcd
        lcd_send_byte(ord(ch), LCD_CHR)#send the character to the lcd


def lcd_clear():
    lcd_send_byte(0x01, LCD_CMD)#clear the lcd
    time.sleep(0.002)


def ads7830_command(channel):
    return 0x84 | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)#rearranges the bits of the chnanel number intot he fromat requried by the ADS7830


def read_adc(channel):
    cmd = ads7830_command(channel)#send the command to the adc
    bus.write_byte(ADC_ADDR, cmd)#send the command to the adc
    time.sleep(0.01)#wait a tiny bit
    return bus.read_byte(ADC_ADDR)#read the value from the adc


def make_bar(value):
    blocks = int((value / 255) * 16)#calculate the number of blocks to display
    return "#" * blocks + "-" * (16 - blocks)#create the bar


def wait_or_stop(stop_event, seconds):
    steps = int(seconds / 0.1)#calculate the number of steps

    for _ in range(steps):
        if stop_event.is_set():#if the stop event is set return
            return
        time.sleep(0.1)#wait a tiny bit


def run(stop_event):#run the screen
    lcd_init()

    while not stop_event.is_set():#run the screen until the stop event is set
        y_val = read_adc(Y_CHANNEL)#read the current y-axis joystick value and store it in y_val

        line1 = make_bar(y_val)#make a bar graph the raw avlue joystick value and turn it into a series of # and - symbols
        line2 = f"VRY=> {y_val}"#format the value to be displayed on the lcd make a textstring showing the decimal value

        lcd_string(line1, LCD_LINE_1)#send the first line to the lcd
        lcd_string(line2, LCD_LINE_2)#send the second line to the lcd

        wait_or_stop(stop_event, 0.1)#wait a tiny bit before checking again

    lcd_clear()


if __name__ == "__main__":#this is the main part of the code that will run when the script is executed
    stop_event = threading.Event()#create an event to stop the thread

    try:
        run(stop_event)#run the screen
    except KeyboardInterrupt:#if the user presses ctrl+c
        stop_event.set()
        lcd_clear()