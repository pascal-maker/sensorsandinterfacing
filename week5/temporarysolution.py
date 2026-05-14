import time
import RPi.GPIO as GPIO
import smbus

# =========================================================
# CONSTANTS
# =========================================================

# I2C address of the ADC
ADC_ADDRESS = 0x48

# Potentiometer channel
POT_CHANNEL = 4

# GPIO pins
SERVO_PIN = 18
BUTTON_PIN = 20

# Servo PWM settings
PWM_FREQUENCY = 50      # 50 Hz -> servo period is 20 ms
MIN_PULSE_MS = 0.6      # practical pulse width for about 0 degrees
MAX_PULSE_MS = 2.4      # practical pulse width for about 180 degrees

# =========================================================
# SETUP
# =========================================================

# Use BCM numbering
GPIO.setmode(GPIO.BCM)

# Servo pin is output
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Button pin is input with internal pull-up resistor
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Open I2C bus
bus = smbus.SMBus(1)

# Create PWM object for servo
servo_pwm = GPIO.PWM(SERVO_PIN, PWM_FREQUENCY)
servo_pwm.start(0)

# Variable that stores whether the system is on or off
system_on = True

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def read_adc(channel):
    """
    Read one analog value from the ADC.

    This version uses the command pattern that currently
    gives you a valid reading on your setup.
    """

    # Only allow valid channels
    if channel < 0 or channel > 7:
        raise ValueError("ADC channel must be between 0 and 7")

    # Build command byte for ADS7830-style reading
    command = 0x84 | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)

    # Read one byte from the ADC
    value = bus.read_byte_data(ADC_ADDRESS, command)

    return value


def map_value_to_angle(adc_value):
    """
    Convert ADC value (0..255) to servo angle (0..180).
    """
    angle = int((adc_value / 255.0) * 180)
    return angle


def angle_to_duty_cycle(angle):
    """
    Convert servo angle (0..180) to PWM duty cycle.

    Servo expects:
    - 50 Hz PWM
    - 20 ms period
    - pulse width roughly between 0.6 ms and 2.4 ms
    """

    # Clamp angle to safe range
    angle = max(0, min(180, angle))

    # Map angle to pulse width
    pulse_width_ms = MIN_PULSE_MS + (angle / 180.0) * (MAX_PULSE_MS - MIN_PULSE_MS)

    # Convert pulse width to duty cycle percentage
    duty_cycle = (pulse_width_ms / 20.0) * 100.0

    return duty_cycle


def set_servo_angle(angle):
    """
    Move servo to the requested angle.
    """
    duty_cycle = angle_to_duty_cycle(angle)

    # Send PWM duty cycle to servo
    servo_pwm.ChangeDutyCycle(duty_cycle)

    # Give the servo time to move
    time.sleep(0.1)

    # Stop active holding signal to reduce jitter
    servo_pwm.ChangeDutyCycle(0)


def show_status(adc_value=None, angle=None, message=None):
    """
    Temporary output function.

    Because the LCD is not detected yet,
    this version prints status in the terminal.
    """
    if message:
        print(message)
    elif adc_value is not None and angle is not None:
        print(f"Analog: {adc_value:3} | Angle: {angle:3}")


def toggle_system(channel):
    """
    Button interrupt callback.

    Toggles the system on or off.
    """
    global system_on
    system_on = not system_on

    if system_on:
        show_status(message="System ON")
    else:
        servo_pwm.ChangeDutyCycle(0)
        show_status(message="System OFF")

    print("System on:", system_on)

# =========================================================
# BUTTON INTERRUPT
# =========================================================

GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=toggle_system, bouncetime=300)

# =========================================================
# MAIN PROGRAM
# =========================================================

try:
    print("Temporary solution running (terminal output instead of LCD).")

    while True:
        if system_on:
            # Read potentiometer value
            adc_value = read_adc(POT_CHANNEL)

            # Convert to servo angle
            angle = map_value_to_angle(adc_value)

            # Move servo
            set_servo_angle(angle)

            # Show values in terminal
            show_status(adc_value=adc_value, angle=angle)

        else:
            show_status(message="System OFF")

        # Small delay for stability
        time.sleep(0.2)

except KeyboardInterrupt:
    print("Program stopped by user.")

finally:
    # Stop PWM
    servo_pwm.stop()
    del servo_pwm

    # Close I2C bus
    bus.close()

    # Clean up GPIO
    GPIO.cleanup()

    print("Cleanup done.")