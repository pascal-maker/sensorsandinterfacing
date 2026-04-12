import RPi.GPIO as GPIO   # library to control Raspberry Pi GPIO pins


class ShiftRegister:
    # class for controlling the 74HC595 shift register
    def __init__(self, data_pin=22, clock_pin=17, latch_pin=27):
        self.data_pin = data_pin      # DS = Serial Data pin
        self.clock_pin = clock_pin    # SHCP = Shift Clock pin
        self.latch_pin = latch_pin    # STCP = Latch / Storage Clock pin
        self._setup()                 # run GPIO setup immediately

    def _setup(self):
        GPIO.setmode(GPIO.BCM)                    # use BCM pin numbering
        GPIO.setup(self.data_pin, GPIO.OUT)       # data pin is output
        GPIO.setup(self.clock_pin, GPIO.OUT)      # shift clock pin is output
        GPIO.setup(self.latch_pin, GPIO.OUT)      # latch clock pin is output

        GPIO.output(self.data_pin, GPIO.LOW)      # start data pin LOW
        GPIO.output(self.clock_pin, GPIO.LOW)     # start shift clock LOW
        GPIO.output(self.latch_pin, GPIO.LOW)     # start latch clock LOW

    def write_one_bit(self, bit):
        # put the bit on the data pin
        GPIO.output(self.data_pin, GPIO.HIGH if bit else GPIO.LOW)

        # create a pulse on the shift clock
        # LOW -> HIGH is the rising edge
        # at that moment the shift register reads DS
        GPIO.output(self.clock_pin, GPIO.HIGH)
        GPIO.output(self.clock_pin, GPIO.LOW)

    def copy_to_storage_register(self):
        # create a pulse on the latch pin
        # this copies the internal shift register data to the outputs
        GPIO.output(self.latch_pin, GPIO.HIGH)
        GPIO.output(self.latch_pin, GPIO.LOW)

    def reset_storage_register(self):
        # clear both cascaded shift registers by sending 16 zeros
        self.shift_out_16bit(0)

    def write_byte(self, data_byte):
        # start with mask 10000000 so we check the leftmost bit first
        mask = 0b10000000

        # loop 8 times because 1 byte = 8 bits
        for _ in range(8):
            # check if the current masked bit is 1 or 0
            bit = (data_byte & mask) != 0

            # send that bit to the shift register
            self.write_one_bit(bit)

            # move mask one place to the right
            mask >>= 1

    def shift_out_16bit(self, value):
        # take the upper 8 bits
        high_byte = (value >> 8) & 0xFF

        # take the lower 8 bits
        low_byte = value & 0xFF

        # send both bytes one after another
        self.write_byte(high_byte)
        self.write_byte(low_byte)

        # latch the result so the LEDs update
        self.copy_to_storage_register()

    def clear(self):
        # easier name for clearing everything
        self.reset_storage_register()


class LedBarGraph:
    # class for controlling the 10-LED bar graph
    def __init__(self, shift_register):
        self.shift_register = shift_register   # store the shift register object

    def set_pattern(self, value, fill=False):
        # keep value between 0 and 10
        if value < 0:
            value = 0
        if value > 10:
            value = 10

        # if value is 0, no LEDs must be on
        if value == 0:
            pattern = 0

        # if fill is True, turn on all LEDs from 1 up to value
        elif fill:
            pattern = (1 << value) - 1

        # if fill is False, turn on only one LED
        else:
            pattern = 1 << (value - 1)

        # send the pattern to the 2 shift registers
        self.shift_register.shift_out_16bit(pattern)

    def clear(self):
        # turn all LEDs off
        self.shift_register.clear()


if __name__ == "__main__":
    try:
        # create the shift register object
        shift_reg = ShiftRegister()

        # create the LED bar object and give it the shift register
        led_bar = LedBarGraph(shift_reg)

        # keep asking the user for input
        while True:
            # ask for a number between 0 and 10
            number = int(input("Number 0-10: "))

            # ask whether fill mode should be used
            fill_text = input("Fill? (y/n): ").strip().lower()

            # fill becomes True only if the user typed y
            fill = fill_text == "y"

            # show the pattern on the LED bar
            led_bar.set_pattern(number, fill)

    except KeyboardInterrupt:
        # stop safely with Ctrl + C
        pass

    finally:
        # reset GPIO pins when the program ends
        GPIO.cleanup()