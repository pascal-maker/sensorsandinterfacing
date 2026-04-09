import smbus
import time


class LCD:
    # -------------------------------------------------
    # CONSTANTS
    # -------------------------------------------------

    # I2C address of the LCD backpack (found with i2cdetect)
    LCD_ADDR = 0x27

    # Maximum characters per line
    LCD_WIDTH = 16

    # RS bit values
    # RS = 1 -> LCD interprets incoming byte as character/data
    LCD_CHR = 0x01

    # RS = 0 -> LCD interprets incoming byte as command/instruction
    LCD_CMD = 0x00

    # DDRAM addresses for the start of both lines
    LCD_LINE_1 = 0x80
    LCD_LINE_2 = 0xC0

    # Control bits of the PCF8574
    LCD_BACKLIGHT = 0x08   # bit 3 -> backlight on
    ENABLE = 0x04          # bit 2 -> E pin

    # Short delays needed by the LCD timing
    E_PULSE = 0.0002
    E_DELAY = 0.0002

    def __init__(self, i2c_addr=LCD_ADDR, bus_id=1):
        # Store the I2C address
        self.addr = i2c_addr

        # Open I2C bus 1
        self.bus = smbus.SMBus(bus_id)

        # Initialize LCD immediately
        self.lcd_init()

    def write_byte(self, bits):
        """
        Send one raw byte over I2C to the LCD backpack.
        The PCF8574 will map these bits to RS, RW, E, BT and D4-D7.
        """
        self.bus.write_byte(self.addr, bits)

    def send_byte_with_e_toggle(self, bits):
        """
        Send one nibble to the LCD by pulsing the E pin.

        The LCD reads the data when E is toggled.
        So we send:
        1. same bits with E HIGH
        2. short delay
        3. same bits with E LOW
        4. short delay
        """

        # Put data on bus and set E HIGH
        self.write_byte(bits | self.ENABLE)
        time.sleep(self.E_PULSE)

        # Put same data on bus and set E LOW
        self.write_byte(bits & ~self.ENABLE)
        time.sleep(self.E_DELAY)

    def set_data_bits(self, value, mode):
        """
        Send a full 8-bit value to the LCD in 4-bit mode.

        Because the LCD is in 4-bit mode, we must split the byte into:
        - Most Significant nibble
        - Least Significant nibble

        Both nibbles are placed on bits 4-7 of the I2C byte.
        Bits 0-3 are used for control:
        - bit 0 = RS
        - bit 1 = RW
        - bit 2 = E
        - bit 3 = Backlight
        """

        # Keep the upper 4 bits of the original byte
        # Also add:
        # - mode (RS bit)
        # - backlight on
        ms_nibble = (value & 0xF0) | mode | self.LCD_BACKLIGHT

        # Move lower 4 bits into the upper 4 positions
        # Also add:
        # - mode (RS bit)
        # - backlight on
        ls_nibble = ((value << 4) & 0xF0) | mode | self.LCD_BACKLIGHT

        # Send high nibble first
        self.send_byte_with_e_toggle(ms_nibble)

        # Then send low nibble
        self.send_byte_with_e_toggle(ls_nibble)

    def send_instruction(self, value):
        """
        Send an LCD command.
        RS = 0, so the LCD treats the byte as an instruction.
        """
        self.set_data_bits(value, self.LCD_CMD)

        # Clear display and return home need slightly more time
        if value in (0x01, 0x02):
            time.sleep(0.002)

    def send_character(self, value):
        """
        Send one character to the LCD.
        RS = 1, so the LCD treats the byte as data.

        If user passes a character like 'A',
        convert it to ASCII code with ord().
        """
        if isinstance(value, str):
            value = ord(value)

        self.set_data_bits(value, self.LCD_CHR)

    def lcd_init(self):
        """
        Initialize the LCD.

        Important theory:
        After power-up, the LCD expects 8-bit communication.
        But we want to use 4-bit mode.

        So we first force the LCD into a known state:
        0x30, 0x30, 0x30, 0x20

        After that, we can safely send normal instructions in 4-bit mode.
        """

        # Give LCD time after power-up
        time.sleep(0.05)

        # Force into known state / begin switch to 4-bit mode
        self.send_byte_with_e_toggle(0x30 | self.LCD_BACKLIGHT)
        time.sleep(0.005)

        self.send_byte_with_e_toggle(0x30 | self.LCD_BACKLIGHT)
        time.sleep(0.001)

        self.send_byte_with_e_toggle(0x30 | self.LCD_BACKLIGHT)
        time.sleep(0.001)

        # Put LCD into 4-bit mode
        self.send_byte_with_e_toggle(0x20 | self.LCD_BACKLIGHT)
        time.sleep(0.001)

        # Function set:
        # 0x28 = 4-bit mode, 2 lines, 5x8 font
        self.send_instruction(0x28)

        # Display ON/OFF control:
        # 0x0C = display on, cursor off, blink off
        self.send_instruction(0x0C)

        # Clear display
        self.send_instruction(0x01)

        # Entry mode:
        # 0x06 = cursor moves right after each char
        self.send_instruction(0x06)

    def clear(self):
        """
        Clear the LCD screen.
        """
        self.send_instruction(0x01)

    def send_string(self, message, line=None):
        """
        Send a string to one LCD line.

        First move the cursor to the selected line,
        then send characters one by one.
        """

        # Default to line 1 if no line was passed
        if line is None:
            line = self.LCD_LINE_1

        # Make sure message is text
        message = str(message)

        # Move cursor to start of chosen line
        self.send_instruction(line)

        # Send maximum 16 chars for one line
        for char in message[:16]:
            self.send_character(char)

    def send_long_string(self, message):
        """
        Send longer text across 2 lines.

        - First 16 chars go to line 1
        - Next 16 chars go to line 2
        """

        message = str(message)

        # Clear display first
        self.clear()

        # Send first 16 chars to line 1
        self.send_instruction(self.LCD_LINE_1)
        for char in message[:16]:
            self.send_character(char)

        # If more chars exist, continue on line 2
        if len(message) > 16:
            self.send_instruction(self.LCD_LINE_2)
            for char in message[16:32]:
                self.send_character(char)

    def display_control(self, display_on=True, cursor_on=False, blink_on=False):
        """
        Optional extra feature for assignment part m:
        control display/cursor/blink using bit operations.

        Base command = 0x08
        Add bits:
        - display on = 0x04
        - cursor on  = 0x02
        - blink on   = 0x01
        """
        command = 0x08

        if display_on:
            command |= 0x04
        if cursor_on:
            command |= 0x02
        if blink_on:
            command |= 0x01

        self.send_instruction(command)

    def close(self):
        """
        Close the I2C bus.
        """
        self.bus.close()


# -------------------------------------------------
# TEST PROGRAM
# -------------------------------------------------
if __name__ == "__main__":
    lcd = None

    try:
        # Create LCD object
        lcd = LCD()

        # First test: simple text
        lcd.send_string("Hello Pascal!", LCD.LCD_LINE_1)
        lcd.send_string("LCD works!", LCD.LCD_LINE_2)
        time.sleep(2)

        # Clear screen
        lcd.clear()
        time.sleep(1)

        # Second test: longer text over 2 lines
        lcd.send_long_string("This is a longer LCD message")
        time.sleep(3)

        # Third test: cursor options
        lcd.clear()
        lcd.send_string("Cursor ON", LCD.LCD_LINE_1)
        lcd.display_control(display_on=True, cursor_on=True, blink_on=False)
        time.sleep(2)

        lcd.clear()
        lcd.send_string("Blink ON", LCD.LCD_LINE_1)
        lcd.display_control(display_on=True, cursor_on=True, blink_on=True)
        time.sleep(2)

        # Restore default
        lcd.clear()
        lcd.display_control(display_on=True, cursor_on=False, blink_on=False)
        lcd.send_string("Done!", LCD.LCD_LINE_1)
        time.sleep(2)

    except KeyboardInterrupt:
        print("Program stopped by user.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if lcd is not None:
            lcd.close()
        print("LCD program ended.")