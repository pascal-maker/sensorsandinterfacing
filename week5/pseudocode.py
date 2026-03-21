import time

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus


class LCD:
    # ---------- LCD constants ----------
    LCD_WIDTH = 16

    LCD_CHR = 0x01   # RS = 1 -> character/data
    LCD_CMD = 0x00   # RS = 0 -> instruction/command

    LCD_LINE_1 = 0x80
    LCD_LINE_2 = 0xC0

    LCD_BACKLIGHT = 0x08   # bit 3
    ENABLE = 0x04          # bit 2

    E_PULSE = 0.0002
    E_DELAY = 0.0002

    def __init__(self, i2c_addr=0x27, bus_id=1):
        self.addr = i2c_addr
        self.bus = SMBus(bus_id)
        self.lcd_init()

    def write_byte(self, bits):
        self.bus.write_byte(self.addr, bits)

    def send_byte_with_e_toggle(self, bits):
        # Enable HIGH
        self.write_byte(bits | self.ENABLE)
        time.sleep(self.E_PULSE)

        # Enable LOW
        self.write_byte(bits & ~self.ENABLE)
        time.sleep(self.E_DELAY)

    def set_data_bits(self, value, mode):
        # split 8-bit value into 2 nibbles for 4-bit LCD mode
        ms_nibble = (value & 0xF0) | mode | self.LCD_BACKLIGHT
        ls_nibble = ((value << 4) & 0xF0) | mode | self.LCD_BACKLIGHT

        self.send_byte_with_e_toggle(ms_nibble)
        self.send_byte_with_e_toggle(ls_nibble)

    def send_instruction(self, value):
        self.set_data_bits(value, self.LCD_CMD)

        # clear display and home need extra delay
        if value in (0x01, 0x02):
            time.sleep(0.002)

    def send_character(self, value):
        if isinstance(value, str):
            value = ord(value)
        self.set_data_bits(value, self.LCD_CHR)

    def lcd_init(self):
        time.sleep(0.05)

        # force LCD into 4-bit mode
        self.send_byte_with_e_toggle(0x30 | self.LCD_BACKLIGHT)
        time.sleep(0.005)

        self.send_byte_with_e_toggle(0x30 | self.LCD_BACKLIGHT)
        time.sleep(0.001)

        self.send_byte_with_e_toggle(0x30 | self.LCD_BACKLIGHT)
        time.sleep(0.001)

        self.send_byte_with_e_toggle(0x20 | self.LCD_BACKLIGHT)
        time.sleep(0.001)

        # normal setup
        self.send_instruction(0x28)  # 4-bit, 2 lines, 5x8 font
        self.send_instruction(0x0C)  # display on, cursor off, blink off
        self.send_instruction(0x01)  # clear display
        self.send_instruction(0x06)  # cursor moves right

    def clear(self):
        self.send_instruction(0x01)

    def set_cursor_options(self, display_on=True, cursor_on=False, blink_on=False):
        # command format: 00001DCB
        cmd = 0x08
        if display_on:
            cmd |= 0x04
        if cursor_on:
            cmd |= 0x02
        if blink_on:
            cmd |= 0x01
        self.send_instruction(cmd)

    def send_string(self, message, line):
        self.send_instruction(line)

        message = str(message)
        message = message.ljust(self.LCD_WIDTH)[:self.LCD_WIDTH]

        for char in message:
            self.send_character(char)

    def show_text(self, text):
        text = str(text)
        line1 = text[:16]
        line2 = text[16:32]

        self.send_string(line1, self.LCD_LINE_1)
        self.send_string(line2, self.LCD_LINE_2)

    def close(self):
        self.bus.close()


def main():
    lcd = LCD(0x27)   # your LCD backpack address

    try:
        # test: ASCII 65 = A
        lcd.clear()
        lcd.send_character(65)
        time.sleep(2)

        while True:
            text = input("Enter text for the LCD (or type 'exit'): ").strip()

            if text.lower() == "exit":
                break

            cursor_on = input("Cursor on? (y/n): ").strip().lower() == "y"
            blink_on = input("Blink on? (y/n): ").strip().lower() == "y"

            lcd.set_cursor_options(display_on=True, cursor_on=cursor_on, blink_on=blink_on)
            lcd.clear()
            lcd.show_text(text)

            print("Text sent to LCD.\n")

    except KeyboardInterrupt:
        print("\nProgram stopped.")

    finally:
        lcd.clear()
        lcd.set_cursor_options(display_on=True, cursor_on=False, blink_on=False)
        lcd.close()


if __name__ == "__main__":
    main()