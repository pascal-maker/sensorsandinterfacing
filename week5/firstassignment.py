import smbus
import time


class LCD:
    # I2C address of the LCD backpack (PCF8574)
    LCD_ADDR = 0x27

    # Maximum number of characters per LCD line
    LCD_WIDTH = 16

    # RS bit values
    # RS = 1 means we are sending character/data
    LCD_CHR = 0x01

    # RS = 0 means we are sending a command/instruction
    LCD_CMD = 0x00

    # DDRAM addresses for the start of each line
    LCD_LINE_1 = 0x80
    LCD_LINE_2 = 0xC0

    # Control bits on the PCF8574
    LCD_BACKLIGHT = 0x08   # bit 3 = backlight on
    ENABLE = 0x04          # bit 2 = Enable pin

    # Small LCD timing delays
    E_PULSE = 0.0002
    E_DELAY = 0.0002

    def __init__(self, i2c_addr=LCD_ADDR, bus_id=1):
        # Store the I2C address of the LCD backpack
        self.addr = i2c_addr

        # Open the I2C bus (bus 1 on most Raspberry Pi boards)
        self.bus = smbus.SMBus(bus_id)

        # Initialize the LCD immediately when the object is created
        self.lcd_init()

    def write_byte(self, bits):
        # Send one raw byte over I2C to the LCD backpack
        self.bus.write_byte(self.addr, bits)

    def send_byte_with_e_toggle(self, bits):
        # The LCD only reads the data when the Enable pin is pulsed

        # Send the byte with Enable HIGH
        self.write_byte(bits | self.ENABLE)

        # Short pulse duration
        time.sleep(self.E_PULSE)

        # Send the same byte again with Enable LOW
        self.write_byte(bits & ~self.ENABLE)

        # Small delay after the pulse
        time.sleep(self.E_DELAY)

    def set_data_bits(self, value, mode):
        # In 4-bit mode, one full byte must be split into:
        # - Most significant nibble
        # - Least significant nibble

        # Keep the upper 4 bits of value in bits 4-7
        ms_nibble = (value & 0xF0) | mode | self.LCD_BACKLIGHT

        # Move the lower 4 bits into bits 4-7
        ls_nibble = ((value << 4) & 0xF0) | mode | self.LCD_BACKLIGHT

        # Send the high nibble first
        self.send_byte_with_e_toggle(ms_nibble)

        # Then send the low nibble
        self.send_byte_with_e_toggle(ls_nibble)

    def send_instruction(self, value):
        # Send a command to the LCD (RS = 0)
        self.set_data_bits(value, self.LCD_CMD)

        # Clear display (0x01) and return home (0x02)
        # need a slightly longer delay
        if value in (0x01, 0x02):
            time.sleep(0.002)

    def send_character(self, value):
        # If the input is a character like 'A',
        # convert it to its ASCII number with ord()
        if isinstance(value, str):
            value = ord(value)

        # Send character/data to the LCD (RS = 1)
        self.set_data_bits(value, self.LCD_CHR)

    def lcd_init(self):
        # Wait a bit after power-up so the LCD is ready
        time.sleep(0.05)

        # Force the LCD into 4-bit mode
        # This is needed because the LCD may start in an unknown state

        self.send_byte_with_e_toggle(0x30 | self.LCD_BACKLIGHT)
        time.sleep(0.005)

        self.send_byte_with_e_toggle(0x30 | self.LCD_BACKLIGHT)
        time.sleep(0.001)

        self.send_byte_with_e_toggle(0x30 | self.LCD_BACKLIGHT)
        time.sleep(0.001)

        self.send_byte_with_e_toggle(0x20 | self.LCD_BACKLIGHT)
        time.sleep(0.001)

        # Normal LCD setup sequence

        # 0x28 = 4-bit mode, 2 lines, 5x8 font
        self.send_instruction(0x28)

        # 0x0C = display on, cursor off, blink off
        self.send_instruction(0x0C)

        # 0x01 = clear display
        self.send_instruction(0x01)

        # 0x06 = cursor moves right after each character
        self.send_instruction(0x06)

    def clear(self):
        # Clear the display
        self.send_instruction(0x01)

    def send_string(self, message, line=None):
        # If no line is given, default to line 1
        if line is None:
            line = self.LCD_LINE_1

        # Make sure message is treated as text
        message = str(message)

        # Move the cursor to the requested line
        self.send_instruction(line)

        # Send up to 16 characters on the chosen line
        for char in message[:16]:
            self.send_character(char)

    def send_long_string(self, message):
        # Helper method for text that may span 2 lines

        # Make sure message is text
        message = str(message)

        # Clear the display first
        self.clear()

        # Go to line 1 and send the first 16 characters
        self.send_instruction(self.LCD_LINE_1)
        for char in message[:16]:
            self.send_character(char)

        # If there is more text, continue on line 2
        if len(message) > 16:
            self.send_instruction(self.LCD_LINE_2)
            for char in message[16:32]:
                self.send_character(char)

    def close(self):
        # Close the I2C bus when finished
        self.bus.close()


# Test program
if __name__ == "__main__":
    try:
        # Create the LCD object
        lcd = LCD()

        # Show text on the first line
        lcd.send_string("Hello Pascal!", LCD.LCD_LINE_1)
        time.sleep(2)

        # Show text on the second line
        lcd.send_string("LCD works!", LCD.LCD_LINE_2)
        time.sleep(2)

        # Clear the screen
        lcd.clear()
        time.sleep(1)

        # Show a longer text across 2 lines
        lcd.send_long_string("This is a longer LCD message")
        time.sleep(3)

    except KeyboardInterrupt:
        # Stop cleanly if the user presses Ctrl+C
        print("Program stopped by user.")

    finally:
        # Close the I2C bus before exiting
        lcd.close()
        print("LCD program ended.")