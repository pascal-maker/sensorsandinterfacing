import time#Imports the time library

try:#The try block is used to catch any errors that may occur
    from smbus2 import SMBus#Imports the SMBus library from smbus2
except ImportError:#If the import fails, it will import the SMBus library from smbus
    from smbus import SMBus


class LCD:#Creates the LCD class
    # ---------- LCD constants ----------
    LCD_WIDTH = 16 #The width of the LCD

    LCD_CHR = 0x01   # RS = 1 -> character/data
    LCD_CMD = 0x00   # RS = 0 -> instruction/command

    LCD_LINE_1 = 0x80 #The first line of the LCD
    LCD_LINE_2 = 0xC0 #The second line of the LCD

    LCD_BACKLIGHT = 0x08   # bit 3
    ENABLE = 0x04          # bit 2

    E_PULSE = 0.0002 #Pulse width of the enable pin
    E_DELAY = 0.0002 #Delay between the enable pin and the data pins

    def __init__(self, i2c_addr=0x27, bus_id=1): #Initializes the LCD
        self.addr = i2c_addr #The I2C address of the LCD
        self.bus = SMBus(bus_id) #The bus ID of the LCD
        self.lcd_init()

    def write_byte(self, bits): #Writes a byte to the LCD
        self.bus.write_byte(self.addr, bits) #Writes the byte to the LCD

    def send_byte_with_e_toggle(self, bits): #Sends a byte to the LCD with the enable pin toggled
        # Enable HIGH
        self.write_byte(bits | self.ENABLE) #Toggles the enable pin HIGH
        time.sleep(self.E_PULSE)#Waits for the pulse width of the enable pin

        # Enable LOW
        self.write_byte(bits & ~self.ENABLE)#Toggles the enable pin LOW
        time.sleep(self.E_DELAY)#Waits for the delay between the enable pin and the data pins

    def set_data_bits(self, value, mode): #Sets the data bits of the LCD
        # split 8-bit value into 2 nibbles for 4-bit LCD mode
        ms_nibble = (value & 0xF0) | mode | self.LCD_BACKLIGHT #splits the value into 2 nibbles
        ls_nibble = ((value << 4) & 0xF0) | mode | self.LCD_BACKLIGHT #splits the value into 2 nibbles

        self.send_byte_with_e_toggle(ms_nibble) #Sends the most significant nibble
        self.send_byte_with_e_toggle(ls_nibble) #Sends the least significant nibble

    def send_instruction(self, value): #Sends an instruction to the LCD
        self.set_data_bits(value, self.LCD_CMD) #Sets the data bits for the instruction

        # clear display and home need extra delay
        if value in (0x01, 0x02): #If the value is 0x01 or 0x02, wait for 0.002 seconds
            time.sleep(0.002)

    def send_character(self, value): #Sends a character to the LCD
        if isinstance(value, str): #Checks if the value is a string
            value = ord(value) #Converts the value to an ASCII value
        self.set_data_bits(value, self.LCD_CHR) #Sets the data bits for the character

    def lcd_init(self): #Initializes the LCD
        time.sleep(0.05)

        # force LCD into 4-bit mode
        self.send_byte_with_e_toggle(0x30 | self.LCD_BACKLIGHT)#Forces the LCD into 4-bit mode
        time.sleep(0.005)#Waits for 0.005 seconds

        self.send_byte_with_e_toggle(0x30 | self.LCD_BACKLIGHT)#Forces the LCD into 4-bit mode
        time.sleep(0.001)#Waits for 0.001 seconds

        self.send_byte_with_e_toggle(0x30 | self.LCD_BACKLIGHT)#Forces the LCD into 4-bit mode
        time.sleep(0.001)#Waits for 0.001 seconds

        self.send_byte_with_e_toggle(0x20 | self.LCD_BACKLIGHT)#Sends the least significant nibble

        # normal setup
        self.send_instruction(0x28)  # 4-bit, 2 lines, 5x8 font
        self.send_instruction(0x0C)  # display on, cursor off, blink off
        self.send_instruction(0x01)  # clear display
        self.send_instruction(0x06)  # cursor moves right

    def clear(self): #Clears the LCD
        self.send_instruction(0x01) #Clears the LCD

    def set_cursor_options(self, display_on=True, cursor_on=False, blink_on=False): #Sets the cursor options
        # command format: 00001DCB
        cmd = 0x08 #Sets the cursor options
        if display_on:
            cmd |= 0x04 #Sets the display on
        if cursor_on:
            cmd |= 0x02 #Sets the cursor on
        if blink_on:
            cmd |= 0x01 #Sets the blink on
        self.send_instruction(cmd) #Sends the instruction to the LCD

    def send_string(self, message, line): #Sends a string to the LCD
        self.send_instruction(line) #Sends the instruction to the LCD

        message = str(message) #Converts the message to a string
        message = message.ljust(self.LCD_WIDTH)[:self.LCD_WIDTH] #L Justifies the message

        for char in message: #Iterates through the message
            self.send_character(char) #Sends the character to the LCD

    def show_text(self, text): #Shows text on the LCD
        text = str(text) #Converts the text to a string
        line1 = text[:16] #Takes the first 16 characters of the text
        line2 = text[16:32] #Takes the next 16 characters of the text

        self.send_string(line1, self.LCD_LINE_1) #Sends the first line of text to the LCD
        self.send_string(line2, self.LCD_LINE_2) #Sends the second line of text to the LCD

    def close(self): #Closes the LCD
        self.bus.close() #Closes the bus


def main():
    lcd = LCD(0x27)   # your LCD backpack address

    try:
        # test: ASCII 65 = A
        lcd.clear() #Clears the LCD
        lcd.send_character(65) #Sends the character A to the LCD
        time.sleep(2) #Waits for 2 seconds

        while True:
            text = input("Enter text for the LCD (or type 'exit'): ").strip()

            if text.lower() == "exit": #Checks if the text is 'exit'
                break

            cursor_on = input("Cursor on? (y/n): ").strip().lower() == "y" #Checks if the cursor is on
            blink_on = input("Blink on? (y/n): ").strip().lower() == "y" #Checks if the blink is on

            lcd.set_cursor_options(display_on=True, cursor_on=cursor_on, blink_on=blink_on) #Sets the cursor options
            lcd.clear() #Clears the LCD
            lcd.show_text(text) #Shows the text on the LCD

            print("Text sent to LCD.\n") #Prints the text sent to the LCD

    except KeyboardInterrupt:
        print("\nProgram stopped.")

    finally:
        lcd.clear() #Clears the LCD
        lcd.set_cursor_options(display_on=True, cursor_on=False, blink_on=False) #Sets the cursor options
        lcd.close() #Closes the LCD


if __name__ == "__main__":
    main()