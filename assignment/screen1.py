import smbus
import time
import subprocess

#LCD SETTINGS
#I2C address of the LCD
I2C_ADDR = 0x27
#LCD has 16 characters per line
LCD_WIDTH = 16
#LCD mode 
#sending normal character
LCD_CHR = 1
#sending LCD command
LCD_CMD = 0
#LCD line addresses
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
#LCD control bits
#enable bit
ENABLE = 0b00000100
#register select bit
RS = 0b00000001

#JOYSTICK BUTTON SETTINGS
#The joystick button is connected to GPIO7
JOY_BUTTON = 7
#We start on screen 1
current_screen = 1
#This flag tells us if we need to redraw the LCD
#In the beginning it is True, because we want to show screen 1 immediately
screen_changed = True

#I2C BUS
#Open I2C bus 1 on the Raspberry Pi
bus = smbus.SMBus(1)

#LCD FUNCTIONS
#Send a short pulse on the ENABLE bit
#The LCD only reads data when ENABLE is pulsed
def lcd_toggle_enable(bits):
    #small delay before pulse
    time.sleep(0.0005)
    #set ENABLE high
    bus.write_byte(I2C_ADDR, bits | ENABLE)
    #small delay while ENABLE is high
    time.sleep(0.0005)
    #set ENABLE low again
    bus.write_byte(I2C_ADDR, bits & ~ENABLE)
    #small delay after pulse
    time.sleep(0.0005)

#Send one byte to the LCD
#Because the LCD works in 4-bit mode,
#we send the byte in 2 parts:
#- high nibble
#- low nibble
def lcd_send_byte(bits, mode):
    #Take upper 4 bits
    #Add mode (command or character)
    #Add backlight bit (0x08)
    high_bits = mode | (bits & 0xF0) | 0x08
    #Shift lower 4 bits to the left
    #Add mode and backlight bit
    low_bits = mode | ((bits << 4) & 0xF0) | 0x08
    #Send upper 4 bits first
    bus.write_byte(I2C_ADDR, high_bits)
    lcd_toggle_enable(high_bits)
    #Then send lower 4 bits
    bus.write_byte(I2C_ADDR, low_bits)
    lcd_toggle_enable(low_bits)

#Initialize the LCD in 4-bit mode
#These commands are standard startup commands for the LCD
def lcd_init():
    lcd_send_byte(0x33, LCD_CMD)   #initialize
    lcd_send_byte(0x32, LCD_CMD)   #set to 4-bit mode
    lcd_send_byte(0x06, LCD_CMD)   #cursor move direction
    lcd_send_byte(0x0C, LCD_CMD)   #display on, cursor off
    lcd_send_byte(0x28, LCD_CMD)   #2 lines, 5x8 font
    lcd_send_byte(0x01, LCD_CMD)   #clear display
    #give LCD a little time
    time.sleep(0.005)

#Print a string on one LCD line
#The message is padded with spaces so old text disappears
def lcd_string(message, line):
    #Make sure the text is exactly 16 chars
    #If shorter, fill with spaces
    message = message.ljust(LCD_WIDTH, " ")
    #Send the line address (line 1 or line 2)
    lcd_send_byte(line, LCD_CMD)
    #Send every character one by one
    for ch in message[:LCD_WIDTH]:
        lcd_send_byte(ord(ch), LCD_CHR)

#Clear the LCD screen
def lcd_clear():
    lcd_send_byte(0x01, LCD_CMD)
    time.sleep(0.005)

#funtion to get ip address
def get_ip_addresses():
    try:
        output = subprocess.check_output("ip a", shell=True,text=True)#get ip address
        wlan_ip = "Not connected"#default value
        eth_ip = "Not connected"#default value
        current_adapter = ""
        for line in output.splitlines():#split output into lines
            line = line.strip()
            if "wlan0:" in line:#check if wlan0 is in line
                current_adapter = "wlan0"
            elif "eth0:" in line:#check if eth0 is in line
                current_adapter = "eth0"

            elif line.startswith("inet "):#check if line starts with inet
                ip_address = line.split()[1].split("/")[0]#get ip address
                if current_adapter == "wlan0":#check if wlan0
                    wlan_ip = ip_address
                elif current_adapter == "eth0":#check if eth0
                    eth_ip = ip_address    
        return wlan_ip, eth_ip
    except Exception as e:#handle exception
        print(e)
        return "Error", "Error"
     
#main program
lcd_init()
try:
    while True:
        wlan_ip,eth_ip = get_ip_addresses()
        #show wifi IP
        lcd_clear()
        lcd_string("WIFI", LCD_LINE_1)
        lcd_string(wlan_ip, LCD_LINE_2)
        time.sleep(2)
        #show lan IP
        lcd_clear()
        lcd_string("LAN", LCD_LINE_1)
        lcd_string(eth_ip, LCD_LINE_2)
        time.sleep(2)
except KeyboardInterrupt:
    #clear lcd when stopping
    lcd_clear()
    print("\nStopped")        