import RPi.GPIO as GPIO


class ShiftRegister:
    def __init__(self, data_pin=22, clock_pin=17, latch_pin=27):
        self.data_pin = data_pin      # DS = data pin
        self.clock_pin = clock_pin    # SHCP = shift clock
        self.latch_pin = latch_pin    # STCP = latch clock
        self._setup()                 # initialize GPIO

    def _setup(self):
        GPIO.setmode(GPIO.BCM)                    # use BCM pin numbering
        GPIO.setup(self.data_pin, GPIO.OUT)       # DS as output
        GPIO.setup(self.clock_pin, GPIO.OUT)      # SHCP as output
        GPIO.setup(self.latch_pin, GPIO.OUT)      # STCP as output

        GPIO.output(self.data_pin, GPIO.LOW)      # start LOW
        GPIO.output(self.clock_pin, GPIO.LOW)
        GPIO.output(self.latch_pin, GPIO.LOW)

    def write_one_bit(self, bit):
        GPIO.output(self.data_pin, GPIO.HIGH if bit else GPIO.LOW)  # put bit on DS
        GPIO.output(self.clock_pin, GPIO.HIGH)                      # rising edge → shift
        GPIO.output(self.clock_pin, GPIO.LOW)                       # back to LOW

    def copy_to_storage_register(self):
        GPIO.output(self.latch_pin, GPIO.HIGH)  # rising edge → update outputs
        GPIO.output(self.latch_pin, GPIO.LOW)

    def reset_storage_register(self):
        self.shift_out_16bit(0)  # send all 0 → all LEDs off

    def write_byte(self, data_byte):
        mask = 0b10000000                 # start from MSB (leftmost bit)
        for _ in range(8):                # 8 bits
            bit = (data_byte & mask) != 0 # extract current bit
            self.write_one_bit(bit)       # send bit
            mask >>= 1                   # move mask right

    def shift_out_16bit(self, value):
        high_byte = (value >> 8) & 0xFF   # upper 8 bits
        low_byte = value & 0xFF           # lower 8 bits

        self.write_byte(high_byte)        # send first byte
        self.write_byte(low_byte)         # send second byte
        self.copy_to_storage_register()   # latch → show on LEDs

    def clear(self):
        self.reset_storage_register()     # clear all LEDs


class LedBarGraph:
    def __init__(self, shift_register):
        self.shift_register = shift_register  # use shift register

    def set_pattern(self, value, fill=False):
        if value < 0:
            value = 0          # clamp min
        if value > 10:
            value = 10         # clamp max

        if value == 0:
            pattern = 0        # all LEDs off
        elif fill:
            pattern = (1 << value) - 1   # fill LEDs (e.g. 3 → 111)
        else:
            pattern = 1 << (value - 1)   # single LED (e.g. 3 → 100)

        self.shift_register.shift_out_16bit(pattern)  # send to LEDs

    def clear(self):
        self.shift_register.clear()  # turn off LEDs


if __name__ == "__main__":
    try:
        shift_reg = ShiftRegister()         # create shift register
        led_bar = LedBarGraph(shift_reg)    # create LED bar

        while True:
            number = int(input("Number 0-10: "))        # ask LED number
            fill_text = input("Fill? (y/n): ").strip().lower()
            fill = fill_text == "y"                     # True if 'y'

            led_bar.set_pattern(number, fill)          # show pattern

    except KeyboardInterrupt:
        pass

    finally:
        GPIO.cleanup()  # reset GPIO