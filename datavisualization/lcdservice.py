from __future__ import annotations

import time

import smbus2

# PCF8574 I2C backpack bit positions
_BACKLIGHT = 0x08 # On bit
_ENABLE = 0b00000100 # Enable pin
_CMD = 0 # Command mode
_CHR = 1 # Character mode

_LINE1 = 0x80 # First line
_LINE2 = 0xC0 # Second line


class LCDService:
    """HD44780 16x2 LCD via PCF8574 I2C backpack."""

    def __init__(self, i2c_addr: int = 0x27, bus: int = 1) -> None:#Default I2C address and bus
        self.addr = i2c_addr# I2C address
        self._bus = smbus2.SMBus(bus)# I2C bus
        self._init()

    def _init(self) -> None:
        for byte in (0x33, 0x32, 0x06, 0x0C, 0x28, 0x01):#Initialize the LCD
            self._write_byte(byte, _CMD)#
        time.sleep(0.002)

    def _pulse_enable(self, data: int) -> None:
        self._bus.write_byte(self.addr, data | _ENABLE | _BACKLIGHT)#Pulse the enable pin
        time.sleep(0.0005)
        self._bus.write_byte(self.addr, (data & ~_ENABLE) | _BACKLIGHT)#Pulse the enable pin
        time.sleep(0.0001)

    def _write_byte(self, byte: int, mode: int) -> None:
        self._pulse_enable(mode | (byte & 0xF0))#Pulse the enable pin
        self._pulse_enable(mode | ((byte << 4) & 0xF0))#Pulse the enable pin

    def write(self, line1: str = "", line2: str = "") -> None:
        """Write up to 16 characters on each line."""
        self._write_byte(_LINE1, _CMD)#Write the first line
        for ch in line1[:16].ljust(16):
            self._write_byte(ord(ch), _CHR)#Write each character
        self._write_byte(_LINE2, _CMD)#Write the second line
        for ch in line2[:16].ljust(16):
            self._write_byte(ord(ch), _CHR)#Write each character

    def clear(self) -> None:
        self._write_byte(0x01, _CMD)#Clear the LCD
        time.sleep(0.002)

    def backlight(self, on: bool) -> None:
        self._bus.write_byte(self.addr, _BACKLIGHT if on else 0x00)#Turn the backlight on or off

    def cleanup(self) -> None:
        self.clear()#Clear the LCD
        self.backlight(False)#Turn the backlight off
        self._bus.close()#Close the I2C bus
