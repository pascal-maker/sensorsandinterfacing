import os
import time

os.environ.setdefault("RPI_LGPIO_CHIP", "0")

import RPi.GPIO as GPIO


class ShiftRegister:
    """74HC595 helper for Freenove display examples."""

    def __init__(self, data_pin=22, latch_pin=27, clock_pin=17):
        self.data_pin = data_pin
        self.latch_pin = latch_pin
        self.clock_pin = clock_pin

        GPIO.setup([self.data_pin, self.latch_pin, self.clock_pin], GPIO.OUT, initial=GPIO.LOW)

    def _pulse_clock(self):
        GPIO.output(self.clock_pin, GPIO.HIGH)
        time.sleep(0.00002)
        GPIO.output(self.clock_pin, GPIO.LOW)

    def _latch(self):
        GPIO.output(self.latch_pin, GPIO.HIGH)
        time.sleep(0.00002)
        GPIO.output(self.latch_pin, GPIO.LOW)

    def write_byte(self, value):
        value &= 0xFF
        for bit_index in range(7, -1, -1):
            GPIO.output(self.data_pin, GPIO.HIGH if value & (1 << bit_index) else GPIO.LOW)
            self._pulse_clock()

    def write_16_bits(self, value):
        self.write_byte((value >> 8) & 0xFF)
        self.write_byte(value & 0xFF)
        self._latch()

    def clear(self):
        self.write_16_bits(0x0000)
