import smbus#used to communicate with the lcd
import time#used to add delays
import subprocess#used to run the linux command

I2C_ADDR = 0x27#address of the lcd
LCD_WIDTH = 16#width of the lcd 16 characters per line
LD_CHR = 1#character mode send a normal character
LCD_CMD = 0#command mode send a lcd command

LCD_LINE_1 = 0x80#first line of the lcd
LCD_LINE_2 = 0xC0#second line of the lcd

ENABLE = 0b00000100#enable pin to toggle the enable pin the lcd so it reads data
RS = 0b00000001#register select pin 0 command mode 1 character mode

bus = smbus.SMBus(1)#initialize the i2c bus

def lcd_toggle_enable(bits):#toggle the enable pin so the lcd reads the data
    time.sleep(0.0005)#wait a tiny bit
    bus.write_byte(I2C_ADDR, bits | ENABLE)#set enable high
    time.sleep(0.0005)#wait a tiny bit
    bus.write_byte(I2C_ADDR, bits & ~ENABLE)#set enable low
    time.sleep(0.0005)

def lcd_send_byte(bits, mode):#lcd only reads data   when the enable line is pulsed sets enable high waits a tiny bit sets enable low 
    high_bits = mode | (bits & 0xF0) | 0x08#send the upper 4 bits of the byte keep only the upper 4 bits
    low_bits = mode | ((bits << 4) & 0xF0) | 0x08#send the lower 4 bits of the byte moves the lower nibble to the upper position again add mode and backlight bit
    
    bus.write_byte(I2C_ADDR, high_bits)#send the upper 4 bits of the byte
    lcd_toggle_enable(high_bits)#toggle the enable pin
    bus.write_byte(I2C_ADDR, low_bits)#send the lower 4 bits of the byte
    lcd_toggle_enable(low_bits)#toggle the enable pin read the nibble now

def lcd_init():#initialize the lcd set 4 bit mode turn display on set 2 lines clear the display
    lcd_send_byte(0x33, LCD_CMD)#function set 8 bit mode
    lcd_send_byte(0x32, LCD_CMD)#function set 8 bit mode
    lcd_send_byte(0x06, LCD_CMD)#entry mode set increment cursor
    lcd_send_byte(0x0C, LCD_CMD)#display on cursor off blink off
    lcd_send_byte(0x28, LCD_CMD)#function set 4 bit mode 2 lines 5x8 dots
    lcd_send_byte(0x01, LCD_CMD)
    time.sleep(0.0005)

def lcd_string(message, line):
    message = message.ljust(LCD_WIDTH, " ")# make sure the message is 16 characters long
    lcd_send_byte(line, LCD_CMD)#send the line to the lcd
    for ch in message[:LCD_WIDTH]:#iterate through the message and send each character to the lcd
        lcd_send_byte(ord(ch), LD_CHR)#send the character to the lcd
def lcd_clear():#clear the lcd
    lcd_send_byte(0x01, LCD_CMD)#clear the lcd
    time.sleep(0.0005)    

def get_ip_addresses():
    output = subprocess.check_output("ip a", shell=True,text=True)#run the linux command ip a and stores all terminal output in a string
    wlan_ip = "Not Connected"#initialize the wlan ip to not connected
    eth_ip = "Not Connected"#initialize the eth ip to not connected
    current_adapter = ""#initialize the current adapter to empty
    for line in output.splitlines():#split the output into lines
        line = line.strip()#remove leading and trailing whitespace
        
        if "wlan0:" in line:#check if the line contains wlan0 if we enter the WiFi section remember that the ip address is in the next line
            current_adapter = "wlan0"
        elif "eth0:" in line:#check if the line contains eth0 if we enter the LAN section remember that the ip address is in the next line
            current_adapter = "eth0"
        elif line.startswith("inet"):#check if the line starts with inet finds ipv4 line
            ip_address = line.split()[1].split("/")[0]#split the line by spaces and get the second element which is the ip address extracts only the ip
            if current_adapter == "wlan0":#check if the current adapter is wlan0 save as WiFi ip
                wlan_ip = ip_address
            elif current_adapter == "eth0":#check if the current adapter is eth0 save as LAN ip
                eth_ip = ip_address
    return wlan_ip, eth_ip# return both values together
lcd_init()
try:
    while True:#keep running forver until stopped
         wlan_ip, eth_ip = get_ip_addresses()#get the ip addresses both
         lcd_clear()
         lcd_string("WiFi: ", LCD_LINE_1)#display WiFi on first line 
         lcd_string(wlan_ip, LCD_LINE_2)#display WiFi ip on second line
         time.sleep(2)
         lcd_clear()
         lcd_string("LAN: ", LCD_LINE_1)#display LAN on first line
         lcd_string(eth_ip, LCD_LINE_2)#display LAN ip on second line
         time.sleep(2)
except KeyboardInterrupt:
    lcd_clear()
    print("\nStopped")
    