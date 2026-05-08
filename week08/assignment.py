# Import GPIO library for Raspberry Pi pins
import RPi.GPIO as GPIO

# Import smbus2 library for I2C communication
import smbus2

# Import time library for delays
import time

# -----------------------------
# GPIO CONSTANTS
# -----------------------------

# Push button connected to GPIO 20
BUTTON = 20#

# Buzzer connected to GPIO 12
BUZZER = 12

# -----------------------------
# PCF8591 SETUP
# -----------------------------

# I2C address of the PCF8591 ADC chip
I2C_ADDRESS = 0x48

# Open I2C bus 1
bus = smbus2.SMBus(1)

# -----------------------------
# SHIFT REGISTER CLASS
# -----------------------------

class ShiftRegister:

    # Constructor
    # Default GPIO pins:
    # data_pin  -> sends bits
    # clock_pin -> tells register to read bit
    # latch_pin -> copies shifted bits to outputs
    def __init__(self, data_pin=22, clock_pin=17, latch_pin=27):

        self.data_pin = data_pin
        self.clock_pin = clock_pin
        self.latch_pin = latch_pin

        # Call setup function automatically
        self.setup()

    # Configure pins as OUTPUT
    def setup(self):

        GPIO.setup(self.data_pin, GPIO.OUT)
        GPIO.setup(self.clock_pin, GPIO.OUT)
        GPIO.setup(self.latch_pin, GPIO.OUT)

    # Send ONE bit into shift register
    def write_one_bit(self, bit):

        # Put 0 or 1 on data pin
        GPIO.output(self.data_pin, bit)

        # Clock pulse:
        # HIGH then LOW shifts bit into register
        GPIO.output(self.clock_pin, GPIO.HIGH)
        GPIO.output(self.clock_pin, GPIO.LOW)

    # Copy shifted data to output pins
    # Without latch, LEDs won't update visibly
    def copy_to_storage_register(self):

        GPIO.output(self.latch_pin, GPIO.HIGH)
        GPIO.output(self.latch_pin, GPIO.LOW)

    # Send 8 bits one by one
    def write_byte(self, value):

        # Loop from bit 7 down to bit 0
        # MSB -> LSB
        for i in range(7, -1, -1):

            # Shift bits right and isolate current bit
            bit = (value >> i) & 1

            # Send bit to shift register
            self.write_one_bit(bit)

    # Send 16-bit value
    # Useful when using 2 chained shift registers
    def shift_out_16bit(self, value):

        # Extract upper 8 bits
        high_byte = (value >> 8) & 0xFF

        # Extract lower 8 bits
        low_byte = value & 0xFF

        # Send both bytes
        self.write_byte(high_byte)
        self.write_byte(low_byte)

        # Update outputs
        self.copy_to_storage_register()

    # Turn off all LEDs
    def clear(self):

        self.shift_out_16bit(0)

# -----------------------------
# LED BAR CLASS
# -----------------------------

class LedBarGraph:

    def __init__(self, shift_register):

        # Store shift register object
        self.shift_register = shift_register

    # value = number from 0-10
    # fill = True  -> fill LEDs
    # fill = False -> only one LED
    def set_pattern(self, value, fill=False):

        # Prevent values below 0
        if value < 0:
            value = 0

        # Prevent values above 10
        if value > 10:
            value = 10

        # If value = 0 -> all LEDs off
        if value == 0:
            pattern = 0

        # Fill mode:
        # Example value=4
        # 00001111
        elif fill:
            pattern = (1 << value) - 1

        # Single LED mode:
        # Example value=4
        # 00001000
        else:
            pattern = 1 << (value - 1)

        # Send pattern to shift register
        self.shift_register.shift_out_16bit(pattern)

# -----------------------------
# ADC READ FUNCTION
# -----------------------------

# ADS7830 command table
COMMANDS = [
    0x84,  # CH0
    0xC4,  # CH1
    0x94,  # CH2
    0xD4,  # CH3
    0xA4,  # CH4
    0xE4,  # CH5
    0xB4,  # CH6
    0xF4   # CH7
]

def read_channel(channel):# read potentiometer on ADC channel A2

    command = COMMANDS[channel]# read potentiometer on ADC channel A2

    bus.write_byte(I2C_ADDRESS, command)# read potentiometer on ADC channel A2

    return bus.read_byte(I2C_ADDRESS)# read potentiometer on ADC channel A2

# -----------------------------
# GLOBAL FILL MODE
# -----------------------------

# False = single LED mode
# True  = fill LED mode
fill_mode = False

# -----------------------------
# BUTTON INTERRUPT
# -----------------------------

# This function runs automatically
# when button interrupt happens
def toggle_fill(channel):#

    global fill_mode# fill mode toggling

    # Toggle True/False
    fill_mode = not fill_mode# fill mode toggling

    print("Fill mode:", fill_mode)# fill mode toggling

# -----------------------------
# MAIN PROGRAM
# -----------------------------

# Use BCM GPIO numbering
GPIO.setmode(GPIO.BCM)

# Button input with pull-up resistor
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Interrupt/event detection
GPIO.add_event_detect(
    BUTTON,
    GPIO.FALLING,      # Trigger when button goes LOW
    callback=toggle_fill,
    bouncetime=300     # Prevent button bouncing
)

# Setup buzzer pin as OUTPUT
GPIO.setup(BUZZER, GPIO.OUT)# buzzer setup

# Create PWM signal on buzzer
# Start at 100 Hz
buzzer_pwm = GPIO.PWM(BUZZER, 100)# buzzer setup

# Start PWM with 50% duty cycle
buzzer_pwm.start(50)# 

# Create shift register object
shift_reg = ShiftRegister()# shift register object

# Create LED bar graph object
led_bar = LedBarGraph(shift_reg)# led bar graph object

try:

    while True:# infinite loop

        # Read potentiometer on ADC channel A2
        analog_value = read_channel(2)# read potentiometer on ADC channel A2

        # Scale ADC value (0-255)
        # into LED value (0-10)
        led_value = int((analog_value / 255) * 10)# scaling

        # Show LEDs
        led_bar.set_pattern(led_value, fill_mode)#showing LEDs

        # Convert analog value into frequency
        # Lower potentiometer -> lower pitch
        # Higher potentiometer -> higher pitch
        frequency = 100 + int((analog_value / 255) * 1000)# converting analog value into frequency

        # Change buzzer frequency dynamically
        buzzer_pwm.ChangeFrequency(frequency)# changing buzzer frequency

        # Small delay
        time.sleep(0.05)# small delay

# Stop safely with CTRL+C
except KeyboardInterrupt:# Stop safely with CTRL+C

    pass

finally:

    # Stop PWM signal
    buzzer_pwm.stop()# stop PWM signal

    # Turn off LEDs
    shift_reg.clear()# turn off LEDs

    # Reset GPIO pins
    GPIO.cleanup()    # reset GPIO pins    