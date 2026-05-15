# ----------------------------------------
# IMPORTS
# ----------------------------------------

import RPi.GPIO as GPIO
import smbus2
import time

# ----------------------------------------
# GPIO CONSTANTS
# ----------------------------------------

BUTTON = 20          # Button GPIO
BUZZER = 12          # Passive buzzer GPIO

# Shift register pins
DATA_PIN = 22        # DS
CLOCK_PIN = 17       # SHCP
LATCH_PIN = 27       # STCP

# ----------------------------------------
# ADC SETUP
# ----------------------------------------

I2C_ADDRESS = 0x48 # Address of the ADC
bus = smbus2.SMBus(1) # Open I2C bus

# ADS7830 command table
COMMANDS = [
    0x84,  # CH0
    0xC4,  # CH1
    0x94,  # CH2 -> A2
    0xD4,  # CH3 -> A3
    0xA4,  # CH4 -> A4
    0xE4,  # CH5
    0xB4,  # CH6
    0xF4   # CH7
]

# Potentiometer channel
A2_CHANNEL = 2#

# ----------------------------------------
# GPIO SETUP
# ----------------------------------------

GPIO.setmode(GPIO.BCM)

GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(DATA_PIN, GPIO.OUT)
GPIO.setup(CLOCK_PIN, GPIO.OUT)
GPIO.setup(LATCH_PIN, GPIO.OUT)

GPIO.setup(BUZZER, GPIO.OUT)

# ----------------------------------------
# BUZZER PWM
# ----------------------------------------

buzzer_pwm = GPIO.PWM(BUZZER, 100)
buzzer_pwm.start(50)

# ----------------------------------------
# GLOBAL VARIABLES
# ----------------------------------------

fill_mode = False

# ----------------------------------------
# BUTTON INTERRUPT
# ----------------------------------------

def toggle_fill(channel):

    global fill_mode

    fill_mode = not fill_mode

    print("Fill mode:", fill_mode)

GPIO.add_event_detect(
    BUTTON,
    GPIO.FALLING,
    callback=toggle_fill,
    bouncetime=300
)

# ----------------------------------------
# READ ADC
# ----------------------------------------

def read_channel(channel):

    command = COMMANDS[channel]

    bus.write_byte(I2C_ADDRESS, command)

    return bus.read_byte(I2C_ADDRESS)

# ----------------------------------------
# SHIFT REGISTER FUNCTIONS
# ----------------------------------------

def write_one_bit(bit):

    GPIO.output(DATA_PIN, bit)

    GPIO.output(CLOCK_PIN, GPIO.HIGH)
    GPIO.output(CLOCK_PIN, GPIO.LOW)

def copy_to_storage_register():

    GPIO.output(LATCH_PIN, GPIO.HIGH)
    GPIO.output(LATCH_PIN, GPIO.LOW)

def write_byte(value):

    for i in range(7, -1, -1):

        bit = (value >> i) & 1

        write_one_bit(bit)

def shift_out_16bit(value):

    high_byte = (value >> 8) & 0xFF
    low_byte = value & 0xFF

    write_byte(high_byte)
    write_byte(low_byte)

    copy_to_storage_register()

def clear_register():

    shift_out_16bit(0)

# ----------------------------------------
# CREATE LED PATTERN
# ----------------------------------------

def set_bar_graph(value, fill=False):

    # Keep value between 0 and 10
    if value < 0:
        value = 0

    if value > 10:
        value = 10

    # All LEDs OFF
    if value == 0:

        pattern = 0

    # Fill mode
    elif fill:

        pattern = (1 << value) - 1

    # Single LED mode
    else:

        pattern = 1 << (value - 1)

    shift_out_16bit(pattern)

# ----------------------------------------
# MAIN LOOP
# ----------------------------------------

try:

    while True:

        # Read potentiometer
        analog_value = read_channel(A2_CHANNEL)

        # Scale 0-255 -> 0-10
        led_value = int((analog_value / 255) * 10)

        # Show LEDs
        set_bar_graph(led_value, fill_mode)

        # Convert potentiometer to frequency
        frequency = 100 + int((analog_value / 255) * 1000)

        # Change buzzer frequency
        buzzer_pwm.ChangeFrequency(frequency)

        # Debug output
        print(
            f"ADC={analog_value} "
            f"LED={led_value} "
            f"Freq={frequency}Hz "
            f"Fill={fill_mode}"
        )

        time.sleep(0.05)

# ----------------------------------------
# EXIT CLEANLY
# ----------------------------------------

except KeyboardInterrupt:

    pass

finally:

    buzzer_pwm.stop()

    clear_register()

    GPIO.cleanup()

    bus.close()