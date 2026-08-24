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

def ads7830_command(channel):#send a command to the adc reads this anolog channel
    return 0x84 | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)#rearrange the bits of the channel number into the format required by the ADS7830 take channel number rearrange bits creates adc command byte
#creates the correct command byte for the ADC so the rapberry pi can tell the adc which analog channel must be read.
def read_adc(channel):#read the value from the adc anolog channel
    cmd = ads7830_command(channel)#build the command adc byte
    bus.write_byte(ADC_ADDR, cmd)#send the command to the adc to start the conversion
    time.sleep(0.01)#wait a tiny bit for the adc to process the command
    return bus.read_byte(ADC_ADDR)#read the value from the adc gets the digital value from the adc usually between 0 and 255.

def make_bar(value):#make a bar graph create fake lcd bar graph
    blocks = int((value/255)*16)  #calculate the number of blocks to display convert joystick value into 0-> 16 blocks because lcd width is 16 characters long
    return "#" * blocks + "-" * (16-blocks)#return the bar so 16 # characters for full value 0 for value 0 8 # and 8 - for half value etc...
    
def wait_or_stop(stop_event,seconds):#waits for a specific amount of time or until the stop event is set so safely.
    steps = int(seconds/0.1)#calculate the number of steps to wait
    for _ in range(steps):#loop through the steps
        if stop_event.is_set():#check if the stop event is set
            return
        time.sleep(0.1)#wait a tiny bit
def run(stop_event):
    lcd_init()#initialize the lcd
    while not stop_event.is_set():#keeps running until the stop event is set
        x_val = read_adc(X_CHANNEL)#read the current X-axis joystick value and store it in x_val

        line1 = make_bar(x_val)#make a bar graph the raw joystick value and turn it into a fake lcd bar graph
        line2 = f"VRX=> {x_val}"#format the value to be displayed on the lcd make a textstring showing the actual decimal value

        lcd_string(line1, LCD_LINE_1)#display the formatted value on the lcd
        lcd_string(line2, LCD_LINE_2)#display the formatted value on the lcd

        wait_or_stop(stop_event,0.1)#wait a tiny bit

    lcd_clear()#clear the lcd


if __name__ == "__main__":#this code allows the program to be run directly
    import threading#imports the threading module so we can use threads

    stop_event = threading.Event()#create a stop event to stop the loop

    try:
        run(stop_event)#start the run function
    except KeyboardInterrupt:#if the user presses ctrl+c
        stop_event.set()#stop the run function
        lcd_clear()#clear the lcd