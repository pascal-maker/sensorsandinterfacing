"""Combined Week 07 assignments A, B, C, and D."""

# Path and sys make the repository's shared hardware package importable.
from pathlib import Path
import sys
import time

import RPi.GPIO as GPIO

# This script is in weeks/week07, two directories below the repository root.
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from hardware import ADS7830, DCMotor, ServoMotor, StepperMotor

# Button wiring uses the Raspberry Pi's BCM pin numbers.
BUTTON_STEPPER_LEFT = 20
BUTTON_STEPPER_RIGHT = 21
BUTTON_DC_MODE = 16
BUTTON_SERVO_TOGGLE = 26

# ADS7830 analog inputs used by the potentiometer and joystick.
POTENTIOMETER_CHANNEL = 0
JOYSTICK_X_CHANNEL = 6

# Event callbacks update these flags; the main loop performs the actual work.
stepper_left_pressed = False
stepper_right_pressed = False
servo_enabled = False


def stepper_left_event(channel):
    """Track both the press and release of the left stepper button."""
    global stepper_left_pressed
    stepper_left_pressed = GPIO.input(BUTTON_STEPPER_LEFT) == GPIO.LOW


def stepper_right_event(channel):
    """Track both the press and release of the right stepper button."""
    global stepper_right_pressed
    stepper_right_pressed = GPIO.input(BUTTON_STEPPER_RIGHT) == GPIO.LOW


def servo_toggle_event(channel):
    """Enable or disable joystick control after a button press."""
    global servo_enabled
    servo_enabled = not servo_enabled


def main():
    # BCM selects GPIO numbers instead of physical header-pin numbers.
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    button_pins = (
        BUTTON_STEPPER_LEFT,
        BUTTON_STEPPER_RIGHT,
        BUTTON_DC_MODE,
        BUTTON_SERVO_TOGGLE,
    )
    # Internal pull-ups make every button active-low: pressed=LOW, released=HIGH.
    GPIO.setup(button_pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Create each reusable device once. The application owns their cleanup.
    adc = ADS7830(address=0x48)
    # Pin order matches ULN2003 inputs IN1 through IN4.
    stepper = StepperMotor(pins=(19, 13, 6, 5), step_delay=0.002)
    # The two DC pins drive opposite L293D H-bridge inputs.
    dc_motor = DCMotor(left_pin=14, right_pin=15)
    # GPIO 18 produces the 50 Hz control pulses for the servo.
    servo = ServoMotor(pin=18, min_pulse_ms=0.6, max_pulse_ms=2.4)

    # Held stepper buttons need BOTH edges so release stops the motor.
    # No long debounce is used because it could hide a quick release event.
    GPIO.add_event_detect(
        BUTTON_STEPPER_LEFT, GPIO.BOTH, callback=stepper_left_event
    )
    GPIO.add_event_detect(
        BUTTON_STEPPER_RIGHT, GPIO.BOTH, callback=stepper_right_event
    )

    # These buttons toggle state once per debounced falling (press) edge.
    GPIO.add_event_detect(
        BUTTON_DC_MODE,
        GPIO.FALLING,
        callback=lambda channel: dc_motor.toggle(),
        bouncetime=200,
    )
    GPIO.add_event_detect(
        BUTTON_SERVO_TOGGLE,
        GPIO.FALLING,
        callback=servo_toggle_event,
        bouncetime=200,
    )

    try:
        while True:
            # A/B: move only when exactly one stepper button is held.
            if stepper_left_pressed and not stepper_right_pressed:
                # Negative direction walks backward through the half-step table.
                stepper.step(direction=-1)
            elif stepper_right_pressed and not stepper_left_pressed:
                # Positive direction walks forward through the half-step table.
                stepper.step(direction=1)
            else:
                # Stop when neither or both direction buttons are held.
                stepper.release()

            # C: continuously map potentiometer input 0..255 to speed 0..100%.
            potentiometer = adc.read_raw(POTENTIOMETER_CHANNEL)
            dc_motor.set_speed(potentiometer / 255 * 100)

            # D: when enabled, map joystick X input 0..255 to servo angle 0..180°.
            if servo_enabled:
                joystick_x = adc.read_raw(JOYSTICK_X_CHANNEL)
                servo_angle = joystick_x / 255 * 180
                servo.set_angle(servo_angle, move_time=0, release=False)
            else:
                joystick_x = None
                servo_angle = None
                servo.release()

            # Console diagnostics allow testing even without external motor power.
            servo_text = (
                f"ON, angle={servo_angle:5.1f}°" if servo_enabled else "OFF"
            )
            print(
                f"DC={dc_motor.state:5} speed={dc_motor.speed:5.1f}% | "
                f"pot={potentiometer:3} | servo={servo_text}"
            )
            # Limit ADC reads and console updates to roughly 20 times per second.
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nCombined motor program stopped")
    finally:
        # Always remove power signals and release resources on every exit path.
        stepper.close()
        dc_motor.close()
        servo.close()
        adc.close()
        GPIO.cleanup()


# Run only when executed directly, not when imported by another script.
if __name__ == "__main__":
    main()
