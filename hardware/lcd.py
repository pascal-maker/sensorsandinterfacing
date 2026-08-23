"""HD44780 16x2 LCD connected through a PCF8574 I2C backpack."""

import time

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus


class LCD:
    WIDTH = 16
    LINE_1 = 0x80
    LINE_2 = 0xC0
    DATA = 0x01
    COMMAND = 0x00
    BACKLIGHT = 0x08
    ENABLE = 0x04
    E_PULSE = 0.0002
    E_DELAY = 0.0002

    def __init__(self, address=0x27, bus_id=1, backlight=True):
        self.address = address
        self.bus = SMBus(bus_id)
        self.backlight_bit = self.BACKLIGHT if backlight else 0
        self.initialize()

    def _write(self, value):
        self.bus.write_byte(self.address, value)

    def _pulse_enable(self, value):
        self._write(value | self.ENABLE)
        time.sleep(self.E_PULSE)
        self._write(value & ~self.ENABLE)
        time.sleep(self.E_DELAY)

    def _send(self, value, mode):
        high = (value & 0xF0) | mode | self.backlight_bit
        low = ((value << 4) & 0xF0) | mode | self.backlight_bit
        self._pulse_enable(high)
        self._pulse_enable(low)

    def command(self, value):
        self._send(value, self.COMMAND)
        if value in (0x01, 0x02):
            time.sleep(0.002)

    def write_character(self, value):
        self._send(ord(value) if isinstance(value, str) else value, self.DATA)

    def initialize(self):
        time.sleep(0.05)
        for value, delay in ((0x30, 0.005), (0x30, 0.001), (0x30, 0.001)):
            self._pulse_enable(value | self.backlight_bit)
            time.sleep(delay)
        self._pulse_enable(0x20 | self.backlight_bit)
        self.command(0x28)
        self.command(0x0C)
        self.command(0x01)

    def set_display(self, display=True, cursor=False, blink=False):
        value = 0x08
        value |= 0x04 if display else 0
        value |= 0x02 if cursor else 0
        value |= 0x01 if blink else 0
        self.command(value)

    def set_backlight(self, enabled=True):
        self.backlight_bit = self.BACKLIGHT if enabled else 0
        self._write(self.backlight_bit)

    def write_line(self, message, line=1):
        address = self.LINE_1 if line == 1 else self.LINE_2
        self.command(address)
        for character in str(message)[:self.WIDTH].ljust(self.WIDTH):
            self.write_character(character)

    def write(self, line1="", line2=""):
        self.write_line(line1, 1)
        self.write_line(line2, 2)

    def clear(self):
        self.command(0x01)

    def close(self, clear=False, backlight_off=False):
        if clear:
            self.clear()
        if backlight_off:
            self.set_backlight(False)
        self.bus.close()

    cleanup = close
