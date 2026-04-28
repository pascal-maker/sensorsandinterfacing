# LCDService — driver for a 16x2 HD44780 LCD connected via a PCF8574 I2C backpack.
#
# How the hardware works:
#   The HD44780 is a parallel LCD controller (4-bit mode used here).
#   The PCF8574 is an I2C I/O expander — it converts the single I2C bus into 8 GPIO pins
#   that are wired directly to the HD44780's data and control lines.
#   We send 4-bit "nibbles" in two pulses per byte because the PCF8574 only has 8 pins
#   and we use 4 of them for data, 1 for the enable strobe, 1 for RS (cmd vs char),
#   and 1 for the backlight transistor.
#
# Default I2C address: 0x27  (some backpacks use 0x3F — check with `i2cdetect -y 1`)
from __future__ import annotations

import time

import smbus2   # pure-Python I2C library, works without root on Pi OS

# PCF8574 bit positions wired to the HD44780
_BACKLIGHT = 0x08          # P3 — backlight transistor base
_ENABLE    = 0b00000100    # P2 — HD44780 Enable (latches data on falling edge)
_CMD       = 0             # RS = 0 → instruction register
_CHR       = 1             # RS = 1 → data register (write a character)

# DDRAM addresses for the start of each line on a 16x2 display
_LINE1 = 0x80
_LINE2 = 0xC0


class LCDService:
    """HD44780 16x2 LCD via PCF8574 I2C backpack."""

    def __init__(self, i2c_addr: int = 0x27, bus: int = 1) -> None:
        self.addr = i2c_addr
        self._bus = smbus2.SMBus(bus)   # bus 1 = /dev/i2c-1 (the standard Pi header bus)
        self._init()

    # ------------------------------------------------------------------
    # Initialisation sequence from the HD44780 datasheet
    # ------------------------------------------------------------------

    def _init(self) -> None:
        # Power-on reset sequence: send 0x33 then 0x32 to force 4-bit mode,
        # then configure: entry mode, display on, 2-line 4-bit, clear.
        for byte in (0x33, 0x32, 0x06, 0x0C, 0x28, 0x01):
            self._write_byte(byte, _CMD)
        time.sleep(0.002)   # clear command needs >1.5 ms

    # ------------------------------------------------------------------
    # Low-level I2C / nibble helpers
    # ------------------------------------------------------------------

    def _pulse_enable(self, data: int) -> None:
        """Toggle the Enable pin to latch one nibble into the HD44780."""
        self._bus.write_byte(self.addr, data | _ENABLE | _BACKLIGHT)   # EN high
        time.sleep(0.0005)
        self._bus.write_byte(self.addr, (data & ~_ENABLE) | _BACKLIGHT) # EN low — data latched
        time.sleep(0.0001)

    def _write_byte(self, byte: int, mode: int) -> None:
        """Send a full byte as two 4-bit nibbles (high nibble first)."""
        self._pulse_enable(mode | (byte & 0xF0))           # upper 4 bits
        self._pulse_enable(mode | ((byte << 4) & 0xF0))    # lower 4 bits

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def write(self, line1: str = "", line2: str = "") -> None:
        """Write up to 16 characters on each line. Pads with spaces to clear old text."""
        # Move cursor to start of line 1
        self._write_byte(_LINE1, _CMD)
        for ch in line1[:16].ljust(16):         # pad to 16 so previous chars are overwritten
            self._write_byte(ord(ch), _CHR)
        # Move cursor to start of line 2
        self._write_byte(_LINE2, _CMD)
        for ch in line2[:16].ljust(16):
            self._write_byte(ord(ch), _CHR)

    def clear(self) -> None:
        """Clear the display and return cursor to home position."""
        self._write_byte(0x01, _CMD)
        time.sleep(0.002)   # clear command is slow — datasheet requires >1.52 ms

    def backlight(self, on: bool) -> None:
        """Turn the backlight on or off without changing display content."""
        self._bus.write_byte(self.addr, _BACKLIGHT if on else 0x00)

    def cleanup(self) -> None:
        """Clear the display, turn off backlight, and close the I2C bus."""
        self.clear()
        self.backlight(False)
        self._bus.close()
