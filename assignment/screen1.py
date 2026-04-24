import smbus2 as smbus #used to communicate with the lcd
import threading
import time#used to add delays
import subprocess#used to run the linux command

I2C_ADDR = 0x27#address of the lcd
LCD_WIDTH = 16#width of the lcd 16 characters per line
LCD_CHR = 1#character mode send a normal character
LCD_CMD = 0#command mode send a lcd command
# These are all correct. RS being "register select" is the key concept — it
# tells the LCD whether the next byte is data to display or a command to
# execute. 
LCD_LINE_1 = 0x80#first line of the lcd
LCD_LINE_2 = 0xC0#second line of the lcd
# The LCD has internal memory (DDRAM) that maps to rows. Row 1 starts at memory
# position 0x80, row 2 at 0xC0. You send the address first, then characters get
# auto-incremented from there. These are standard and correct for a 16×2
# display.
#pin definitions

ENABLE = 0b00000100#enable pin to toggle the enable pin the lcd so it reads data
RS = 0b00000001#register select pin 0 command mode 1 character mode
#                                                                               
#Both correct. ENABLE is the bell you ring on every byte (explained earlier).  
#RS is OR'd into each byte before sending to tell the LCD what kind of data  
#follows.   
# 
bus = smbus.SMBus(1)#initialize the i2c bus

def lcd_toggle_enable(bits):#toggle the enable pin so the lcd reads the data
    time.sleep(0.0005)#wait a tiny bit
    bus.write_byte(I2C_ADDR, bits | ENABLE)#set enable high
    time.sleep(0.0005)#wait a tiny bit
    bus.write_byte(I2C_ADDR, bits & ~ENABLE)#set enable low
    time.sleep(0.0005)
#  This is the bell-ringing function you asked me to explain earlier — it sets
#  enable high, waits, then brings it low. Each pulse latches data on the falling
#  edge. The half-millisecond delays are critical (LCD is slow compared to Pi
#  CPU). Correct, no issues here.
#
def lcd_send_byte(bits, mode):#lcd only reads data when the enable line is pulsed
    high_bits = mode | (bits & 0xF0) | 0x08#send the upper 4 bits of the byte
    low_bits = mode | ((bits << 4) & 0xF0) | 0x08#send the lower 4 bits of the byte
# - & 0xF0 keeps only the upper nibble of each byte
# - << 4 shifts lower nibble into position to send it next
# - | 0x08 sets the backlight bit (if you remove this, display works but screen
# goes black — classic debugging trap)
#
# This is solid. It's a clean implementation of 4-bit mode. 
    bus.write_byte(I2C_ADDR, high_bits)#send the upper 4 bits of the byte
    lcd_toggle_enable(high_bits)#toggle the enable pin
    bus.write_byte(I2C_ADDR, low_bits)#send the lower 4 bits of the byte
    lcd_toggle_enable(low_bits)#toggle the enable pin

def lcd_init():#initialize the lcd
    lcd_send_byte(0x33, LCD_CMD)#function set 8 bit mode
    lcd_send_byte(0x32, LCD_CMD)#function set 8 bit mode
    lcd_send_byte(0x06, LCD_CMD)#entry mode set increment cursor
    lcd_send_byte(0x0C, LCD_CMD)#display on cursor off blink off
    lcd_send_byte(0x28, LCD_CMD)#function set 4 bit mode 2 lines 5x8 dots
    lcd_send_byte(0x01, LCD_CMD)#clear the lcd
    time.sleep(0.0005)
    #This is a standard initialization sequence for this type of HD44780-based
    #LCD in 4-bit mode. The half-second sleep after 0x01 is important because
    #clearing the display takes longer than other operations. Everything looks
    #correct.  Correct initialization sequence. The first two bytes (33 then 32) are the
    #spec-mandated way to go from 8-bit mode down to 4-bit — without them, the
    #display might not initialize properly.

def lcd_string(message, line):
    message = message.ljust(LCD_WIDTH, " ")#make sure the message is 16 characters long
    lcd_send_byte(line, LCD_CMD)#send the line to the lcd
    for ch in message[:LCD_WIDTH]:#iterate through the message and send each character to the lcd
        lcd_send_byte(ord(ch), LCD_CHR)#send the character to the lcd
#                                                                                
#  Correct. ljust pads with spaces so text always fills the full width (prevents 
#  leftover garbage from previous messages). The loop sends each character one at
#  a time via I2C nibbles. 
# 
def lcd_clear():#clear the lcd
    lcd_send_byte(0x01, LCD_CMD)#clear the lcd
    time.sleep(0.0005)

def get_ip_addresses():
    output = subprocess.check_output("ip a", shell=True, text=True)#run the linux command ip a
    wlan_ip = "Not Connected"#initialize the wlan ip to not connected
    eth_ip = "Not Connected"#initialize the eth ip to not connected
    current_adapter = ""#initialize the current adapter to empty
    for line in output.splitlines():#split the output into lines
        line = line.strip()#remove leading and trailing whitespace

        if "wlan0:" in line:#check if the line contains wlan0
            current_adapter = "wlan0"
        elif "eth0:" in line:#check if the line contains eth0
            current_adapter = "eth0"
        elif line.startswith(" inet "):#check if the line starts with inet finds ipv4 line
            ip_address = line.split()[1].split("/")[0]#extract only the ip
            if current_adapter == "wlan0":#save as WiFi ip
                wlan_ip = ip_address
            elif current_adapter == "eth0":#save as LAN ip
                eth_ip = ip_address
    return wlan_ip, eth_ip#return both values together

def wait_or_stop(stop_event, seconds):#wait for the given seconds or until the stop event is set
    steps = int(seconds / 0.1)#calculate the number of steps
    for _ in range(steps):#loop for the number of steps
        if stop_event.is_set():#check if the stop event is set
            return
        time.sleep(0.1)#wait a tiny bit

def run(stop_event):
    lcd_init()
    while not stop_event.is_set():
        wlan_ip, eth_ip = get_ip_addresses()#get the ip addresses
        lcd_clear()
        lcd_string("WiFi: ", LCD_LINE_1)#display WiFi on first line
        lcd_string(wlan_ip, LCD_LINE_2)#display WiFi ip on second line
        wait_or_stop(stop_event, 2)

        if stop_event.is_set():
            break

        lcd_clear()
        lcd_string("LAN: ", LCD_LINE_1)#display LAN on first line
        lcd_string(eth_ip, LCD_LINE_2)#display LAN ip on second line
        wait_or_stop(stop_event, 2)#wait for 2 seconds or until the stop event is set
    lcd_clear()

if __name__ == "__main__":
    stop_event = threading.Event()
    try:
        run(stop_event)
    except KeyboardInterrupt:
        stop_event.set()
        lcd_clear()
