import RPi.GPIO as GPIO
import time


class ShiftRegister:
    def __init__(self, data_pin=22, clock_pin=17, latch_pin=27):#
        self.data_pin = data_pin
        self.clock_pin = clock_pin
        self.latch_pin = latch_pin
        self._setup()

    def _setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.data_pin, GPIO.OUT)
        GPIO.setup(self.clock_pin, GPIO.OUT)
        GPIO.setup(self.latch_pin, GPIO.OUT)

        GPIO.output(self.data_pin, 0)
        GPIO.output(self.clock_pin, 0)
        GPIO.output(self.latch_pin, 0)

    def write_one_bit(self, bit):
        GPIO.output(self.data_pin, GPIO.HIGH if bit else GPIO.LOW)
        GPIO.output(self.clock_pin, GPIO.HIGH)
        GPIO.output(self.clock_pin, GPIO.LOW)

    def storage_pulse(self):
        GPIO.output(self.latch_pin, GPIO.HIGH)
        GPIO.output(self.latch_pin, GPIO.LOW)

    def write_byte(self, data_byte):
        mask = 0b10000000
        for _ in range(8):
            bit = (data_byte & mask) != 0
            self.write_one_bit(bit)
            mask >>= 1

    def shift_out_16bit(self, value):
        high_byte = (value >> 8) & 0xFF
        low_byte = value & 0xFF

        self.write_byte(high_byte)
        self.write_byte(low_byte)
        self.storage_pulse()

    def clear(self):
        self.shift_out_16bit(0)


class LedBarGraph:
    def __init__(self, shift_register):
        self.shift_register = shift_register

    def set_pattern(self, value, fill=False):
        if value < 0:
            value = 0
        if value > 10:
            value = 10

        if value == 0:
            pattern = 0
        elif fill:
            pattern = (1 << value) - 1
        else:
            pattern = 1 << (value - 1)

        self.shift_register.shift_out_16bit(pattern)

    def clear(self):
        self.shift_register.clear()


if __name__ == "__main__":
    try:
        shift_reg = ShiftRegister()
        led_bar = LedBarGraph(shift_reg)

        while True:
            number = int(input("Number 0-10: "))
            fill_text = input("Fill? (y/n): ").strip().lower()
            fill = fill_text == "y"

            led_bar.set_pattern(number, fill)

    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()