"""74HC595 serial-in, parallel-out shift-register driver."""

import time

import RPi.GPIO as GPIO


class ShiftRegister:
    def __init__(self, data_pin, clock_pin, latch_pin, pulse_delay=0.000001):
        self.data_pin = data_pin
        self.clock_pin = clock_pin
        self.latch_pin = latch_pin
        self.pulse_delay = pulse_delay
        GPIO.setup((data_pin, clock_pin, latch_pin), GPIO.OUT, initial=GPIO.LOW)

    def _pulse(self, pin):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(self.pulse_delay)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(self.pulse_delay)

    def shift_byte(self, value, msb_first=True, latch=True):
        positions = range(7, -1, -1) if msb_first else range(8)
        for position in positions:
            GPIO.output(self.data_pin, (value >> position) & 1)
            self._pulse(self.clock_pin)
        if latch:
            self._pulse(self.latch_pin)

    def clear(self):
        self.shift_byte(0)
