import RPi.GPIO as GPIO
import smbus2
import time

# -----------------------------
# GPIO CONSTANTS
# -----------------------------

BUTTON = 20
BUZZER = 12

# -----------------------------
# PCF8591 SETUP
# -----------------------------

I2C_ADDRESS = 0x48
bus = smbus2.SMBus(1)

# -----------------------------
# SHIFT REGISTER CLASS
# -----------------------------

class ShiftRegister:

    def __init__(self, data_pin=22, clock_pin=17, latch_pin=27):

        self.data_pin = data_pin
        self.clock_pin = clock_pin
        self.latch_pin = latch_pin

        self.setup()

    def setup(self):

        GPIO.setup(self.data_pin, GPIO.OUT)
        GPIO.setup(self.clock_pin, GPIO.OUT)
        GPIO.setup(self.latch_pin, GPIO.OUT)

    def write_one_bit(self, bit):

        GPIO.output(self.data_pin, bit)

        GPIO.output(self.clock_pin, GPIO.HIGH)
        GPIO.output(self.clock_pin, GPIO.LOW)

    def copy_to_storage_register(self):

        GPIO.output(self.latch_pin, GPIO.HIGH)
        GPIO.output(self.latch_pin, GPIO.LOW)

    def write_byte(self, value):

        for i in range(7, -1, -1):

            bit = (value >> i) & 1
            self.write_one_bit(bit)

    def shift_out_16bit(self, value):

        high_byte = (value >> 8) & 0xFF
        low_byte = value & 0xFF

        self.write_byte(high_byte)
        self.write_byte(low_byte)

        self.copy_to_storage_register()

    def clear(self):

        self.shift_out_16bit(0)

# -----------------------------
# LED BAR CLASS
# -----------------------------

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

# -----------------------------
# ADC READ FUNCTION
# -----------------------------

def read_channel(channel):

    bus.write_byte(I2C_ADDRESS, 0x40 | (channel & 0x03))
    bus.read_byte(I2C_ADDRESS)       # dummy read (previous conversion)
    return bus.read_byte(I2C_ADDRESS) # 0-255

# -----------------------------
# GLOBAL FILL MODE
# -----------------------------

fill_mode = False

# -----------------------------
# BUTTON INTERRUPT
# -----------------------------

def toggle_fill(channel):

    global fill_mode

    fill_mode = not fill_mode

    print("Fill mode:", fill_mode)

# -----------------------------
# MAIN PROGRAM
# -----------------------------

GPIO.setmode(GPIO.BCM)

GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(
    BUTTON,
    GPIO.FALLING,
    callback=toggle_fill,
    bouncetime=300
)

GPIO.setup(BUZZER, GPIO.OUT)

buzzer_pwm = GPIO.PWM(BUZZER, 100)

buzzer_pwm.start(50)

shift_reg = ShiftRegister()

led_bar = LedBarGraph(shift_reg)

try:

    while True:

        # read potentiometer on A2
        analog_value = read_channel(2)

        # scale to 1-10
        led_value = int((analog_value / 255) * 10)

        if led_value == 0:
            led_value = 1

        # display on LED bar
        led_bar.set_pattern(led_value, fill_mode)

        # scale frequency
        frequency = 100 + int((analog_value / 255) * 1000)

        buzzer_pwm.ChangeFrequency(frequency)

        time.sleep(0.05)

except KeyboardInterrupt:

    pass

finally:

    # stop buzzer
    buzzer_pwm.stop()

    # clear LEDs
    shift_reg.clear()

    GPIO.cleanup()
