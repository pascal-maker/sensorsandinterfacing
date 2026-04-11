"""
Week 3 — Bit Operations
Classes: BCDReader, SerialReceiver
"""

import RPi.GPIO as GPIO
import time


class BCDReader:
    """
    Reads 4 buttons as a 4-bit BCD value.
    Button pins map to bit positions 0-3 (LSB first).
    Buttons are active-LOW (pulled up internally).
    """

    def __init__(self, pins):
        """
        pins: list of 4 GPIO pin numbers [bit0_pin, bit1_pin, bit2_pin, bit3_pin]
        """
        if len(pins) != 4:
            raise ValueError("BCDReader requires exactly 4 pins")
        self.pins = pins
        for pin in pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def read_bits(self):
        """Return a list of 4 bit values [b0, b1, b2, b3]."""
        return [int(not GPIO.input(pin)) for pin in self.pins]

    def read_value(self):
        """Return the integer BCD value (0–15) from the 4 buttons."""
        bits = self.read_bits()
        value = 0
        for i, bit in enumerate(bits):
            if bit:
                value |= 1 << i
        return value

    def print_state(self):
        bits = self.read_bits()
        for i, b in enumerate(bits):
            print(f"  bit {i} = {b}")
        print(f"  BCD value = {self.read_value()}\n")


class SerialReceiver:
    """
    Receives bytes serially (MSB first) over a single GPIO pin.
    Each bit is sampled every `bit_delay` seconds.
    """

    def __init__(self, rx_pin, bit_delay=0.5):
        self.rx_pin = rx_pin
        self.bit_delay = bit_delay
        GPIO.setup(rx_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def receive_byte(self):
        """Block and read 8 bits MSB-first, return as integer."""
        data = 0
        for _ in range(8):
            bit = GPIO.input(self.rx_pin)
            data = (data << 1) | bit
            time.sleep(self.bit_delay)
        return data

    def receive_byte_lsb(self):
        """Block and read 8 bits LSB-first, return as integer."""
        data = 0
        for i in range(8):
            bit = GPIO.input(self.rx_pin)
            if bit:
                data |= 1 << i
            time.sleep(self.bit_delay)
        return data


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)

    # BCD demo
    bcd = BCDReader(pins=[16, 20, 21, 26])
    print("--- BCD Reader (press buttons, CTRL+C to stop) ---")
    try:
        while True:
            bcd.print_state()
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
