import os

os.environ.setdefault("RPI_LGPIO_CHIP", "0")

import RPi.GPIO as GPIO


class BCDInput:
    """Read a 4-bit BCD/thumbwheel input as a decimal value."""

    def __init__(self, pins=(16, 20, 21, 26), active_low=True):
        self.pins = tuple(pins)
        self.active_low = active_low
        GPIO.setup(self.pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def read_bits(self):
        bits = []
        for pin in self.pins:
            raw = GPIO.input(pin)
            bits.append(1 - raw if self.active_low else raw)
        return bits

    def read_value(self):
        value = 0
        for bit_index, bit in enumerate(self.read_bits()):
            value |= bit << bit_index
        return value

    def wait_for_change(self, previous_value):
        value = self.read_value()
        return value if value != previous_value else previous_value
