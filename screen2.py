import smbus
import time
import RPi.GPIO as GPIO

I2C_ADDR = 0x27#address of the lcd
LCD_WIDTH = 16#width of the lcd 16 characters per line
LD_CHR = 1#character mode send a normal character
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
def lcd_toggle_enable(bits):#toggle the enable pin so the lcd reads the data
    time.sleep(0.0005)#wait a tiny bit
    bus.write_byte(I2C_ADDR, bits | ENABLE)#set enable high
    time.sleep(0.0005)#wait a tiny bit
    bus.write_byte(I2C_ADDR, bits & ~ENABLE)#set enable low
    time.sleep(0.0005)#wait a tiny bit

def lcd_send_byte(bits, mode):#lcd only reads data   when the enable line is pulsed sets enable high waits a tiny bit sets enable low 
    high_bits = mode | (bits & 0xF0) | 0x08#send the upper 4 bits of the byte keep only the upper 4 bits
    low_bits = mode | ((bits << 4) & 0xF0) | 0x08#send the lower 4 bits of the byte moves the lower nibble to the upper position again add mode and backlight bit
    
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
        lcd_send_byte(ord(ch), LD_CHR)#send the character to the lcd

def lcd_clear():#clear the lcd
    lcd_send_byte(0x01, LCD_CMD)#clear the lcd
    time.sleep(0.0005)    


def read_button_bits():
    b1 = 1 if GPIO.input(BUTTON_1) == GPIO.LOW else 0#read the button state
    b2 = 1 if GPIO.input(BUTTON_2) == GPIO.LOW else 0#read the button state
    b3 = 1 if GPIO.input(BUTTON_3) == GPIO.LOW else 0#read the button state
    b4 = 1 if GPIO.input(BUTTON_4) == GPIO.LOW else 0#read the button state
    return b1, b2, b3, b4

def make_nibble(b1,b2,b3,b4):#make a nibble from the button states
    value = (b1 << 3) | (b2 << 2) | (b3 << 1) | b4#make a nibble from the button states
    return value

def format_screen(value):#format the value to be displayed on the lcd
    binary_text = f"0b{value:04b}"#format the value to be displayed on the lcd
    hex_text = f"0x{value:01x}"#format the value to be displayed on the lcd
    line1 = f"{binary_text} {hex_text.rjust(16-len(binary_text))}"#format the value to be displayed on the lcd
    line2 = str(value).rjust(16)#format the value to be displayed on the lcd
    return line1, line2#return the formatted values

#setup the buttons
GPIO.setmode(GPIO.BCM)#set the mode to bcm
GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setup the button as an input with a pull up resistor
GPIO.setup(BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setup the button as an input with a pull up resistor
GPIO.setup(BUTTON_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setup the button as an input with a pull up resistor
GPIO.setup(BUTTON_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setup the button as an input with a pull up resistor


lcd_init()
last_value = -1#initialize the last value to -1
try:
    while True:#keep running forver until stopped
        b1, b2, b3, b4 = read_button_bits()
        value = make_nibble(b1,b2,b3,b4)
        if value != last_value:#check if the value has changed
            line1, line2 = format_screen(value)#format the value to be displayed on the lcd
            lcd_clear()
            lcd_string(line1, LCD_LINE_1)#display the formatted value on the lcd
            lcd_string(line2, LCD_LINE_2)#display the formatted value on the lcd
            print(f" Buttons: {b1} {b2} {b3} {b4} Value: {value}")#print the button states and the value
            last_value = value#update the last value
            time.sleep(0.1)#wait a tiny bit
except KeyboardInterrupt:
    lcd_clear()
    print("\nStopped")#print stopped
    GPIO.cleanup()#cleanup the gpio pins
    

"This exercise demonstrates the relationship between physical inputs (GPIO buttons) and data representation. By reading four buttons as individual bits, we construct a 4-bit nibble using bitwise left-shift operations. The resulting integer is then dynamically formatted into Binary (0b0000), Hexadecimal (0x0), and Decimal formats. This data is transmitted via the I2C protocol to a 16x2 LCD, providing real-time visual feedback of how binary state changes affect different numbering systems."