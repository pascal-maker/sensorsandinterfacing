import smbus2 as smbus
import time
import RPi.GPIO as GPIO

I2C_ADDR = 0x27#address of the lcd
LCD_WIDTH = 16#width of the lcd 16 characters per line
LCD_CHR = 1#character mode send a normal character
LCD_CMD = 0#command mode send a lcd command

LCD_LINE_1 = 0x80#first line of the lcd
LCD_LINE_2 = 0xC0#second line of the lcd

ENABLE = 0b00000100#enable pin to toggle the enable pin the lcd so it reads data
RS = 0b00000001#register select pin 0 command mode 1 character mode

BUTTON_1 = 20
BUTTON_2 = 21
BUTTON_3 = 16
BUTTON_4 = 26

bus = smbus.SMBus(1)#initialize the i2c bus

#setup the buttons

def setup_buttons():
    GPIO.setmode(GPIO.BCM)#set the mode to bcm
    GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setup the button as an input with a pull up resistor
    GPIO.setup(BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setup the button as an input with a pull up resistor
    GPIO.setup(BUTTON_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setup the button as an input with a pull up resistor
    GPIO.setup(BUTTON_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setup the button as an input with a pull up resistor

def lcd_toggle_enable(bits):#toggle the enable pin so the lcd reads the data
    time.sleep(0.0005)#wait a tiny bit
    bus.write_byte(I2C_ADDR, bits | ENABLE)#set enable high
    time.sleep(0.0005)#wait a tiny bit
    bus.write_byte(I2C_ADDR, bits & ~ENABLE)#set enable low
    time.sleep(0.0005)  


def lcd_send_byte(bits, mode):#lcd only reads data when the enable line is pulsed sets enable high waits a tiny bit sets enable low 
    high_bits = mode | (bits & 0xF0) | 0x08#send the upper 4 bits of the byte keep only the upper 4 bits
    low_bits = mode | ((bits << 4) & 0xF0) | 0x08#send the lower 4 bits of the byte moves the lower nibble to the upper position again add mode and backlight bit
    
    bus.write_byte(I2C_ADDR, high_bits)#send the upper 4 bits of the byte
    lcd_toggle_enable(high_bits)#toggle the enable pin
    bus.write_byte(I2C_ADDR, low_bits)#send the lower 4 bits of the byte
    lcd_toggle_enable(low_bits)#toggle the enable pin

def lcd_init():#initialize the lcd
    lcd_send_byte(0x33, LCD_CMD)#send the function set command
    lcd_send_byte(0x32, LCD_CMD)#send the function set command
    lcd_send_byte(0x06, LCD_CMD)#send the entry mode set command
    lcd_send_byte(0x0C, LCD_CMD)#send the display on/off control command
    lcd_send_byte(0x01, LCD_CMD)#send the clear display command
    time.sleep(0.002)#wait a tiny bit    


def lcd_string(message, line):#send a string to the lcd
    message = message.ljust(LCD_WIDTH)#pad the message with spaces to the width of the lcd
    lcd_send_byte(line, LCD_CMD)#send the line address command
    for i in range(LCD_WIDTH):#loop through the message
        lcd_send_byte(ord(message[i]), LCD_CHR)#send the character

def lcd_clear():#clear the lcd
    lcd_send_byte(0x01, LCD_CMD)#send the clear display command
    time.sleep(0.002)#wait a tiny bit    
#read buttons as a nibble

def read_buttons_bits():
    b1 =   1 if GPIO.input(BUTTON_1) == GPIO.LOW else 0#if the button is pressed the value will be low so we return 1 else we return 0
    b2 =   1 if GPIO.input(BUTTON_2) == GPIO.LOW else 0#if the button is pressed the value will be low so we return 1 else we return 0
    b3 =   1 if GPIO.input(BUTTON_3) == GPIO.LOW else 0#if the button is pressed the value will be low so we return 1 else we return 0
    b4 =   1 if GPIO.input(BUTTON_4) == GPIO.LOW else 0#if the button is pressed the value will be low so we return 1 else we return 0
    return b1, b2, b3, b4
    
def make_nibble(b1,b2,b3,b4):#takes the 4 bits and makes a nibble from them
    value = (b1 << 3) | (b2 << 2) | (b3 << 1) | b4#shifts the bits to the left and adds them together
    return value#returns the nibble

def format_screen(value):#takes the nibble and formats it to be displayed on the lcd
    binary_text = f"0b{value:04b}"#formats the nibble to binary
    hex_text = f"0x{value:01x}"#formats the nibble to hex
    line1 = binary_text + hex_text.rjust(16-len(binary_text))#formats the line 1
    line2 = str(value).rjust(16)#formats the line 2
    return line1, line2#returns the formatted lines
   
def run(stop_event):#main run function that takes the stop event as an argument
    lcd_init()#initialize the lcd
    setup_buttons()#setup the buttons
    last_value = -1#sets the last value to -1 forces lcd to update at startup

    while not stop_event.is_set():#keeps running until the stop event is set
        b1, b2, b3, b4 = read_buttons_bits()#reads the button bits
        value = make_nibble(b1, b2, b3, b4)#makes a nibble from the button bits

        if value != last_value:#checks if the value has changed
            line1, line2 = format_screen(value)#formats the screen
            lcd_clear()

            lcd_string(line1, LCD_LINE_1)#displays the first line
            lcd_string(line2, LCD_LINE_2)#displays the second line
            print(f"Button states (b1 to b4): {b1} {b2} {b3} {b4}  Value: {value}")#prints the button states and the value

            last_value = value#sets the last value to the current value

            time.sleep(0.1)#waits a tiny bit

if __name__ == "__main__":#main function that is called when the script is run
    import threading#imports the threading library
    stop_event = threading.Event()#creates an event to stop the thread
    try:
        run(stop_event)#runs the run function
    except KeyboardInterrupt:#when the user presses ctrl+c
        stop_event.set()#sets the stop event
        lcd_clear()#clears the lcd
   
