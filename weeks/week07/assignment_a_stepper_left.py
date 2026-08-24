"""Assignment A: turn the stepper left while GPIO 20 is held."""

# Path and sys make the repository's shared hardware package importable.
from pathlib import Path
import sys
import time  # Prevents a busy loop while the button is released.

import RPi.GPIO as GPIO

# This script is in weeks/week07, two directories below the repository root.
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from hardware import StepperMotor

# The pull-up means released=HIGH and pressed=LOW.
BUTTON_PIN = 20
button_pressed = False


def button_event(channel):
    """Remember the current button level after a press or release event."""
    global button_pressed
    button_pressed = GPIO.input(BUTTON_PIN) == GPIO.LOW

    # Print only when the button changes state, not after every motor step.
    if button_pressed:
        print("GPIO 20 pressed: stepper turning left")
    else:
        print("GPIO 20 released: stepper stopped")


def main():
    # BCM refers to GPIO numbers rather than physical header-pin numbers.
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # The class configures GPIO 19, 13, 6, and 5 for the ULN2003 driver.
    stepper = StepperMotor()

    # BOTH generates an interrupt when the button is pressed and released.
    GPIO.add_event_detect(BUTTON_PIN, GPIO.BOTH, callback=button_event)
    print("Stepper-left test started")
    print("Hold GPIO 20 to turn left; release it to stop. Press Ctrl+C to exit.")
    try:
        while True:
            if button_pressed:
                # -1 walks backward through the coil sequence (left).
                stepper.step(direction=-1)
            else:
                # Remove coil power whenever the button is not held.
                stepper.release()
                time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nStepper stopped")
    finally:
        # This also runs if an unexpected exception stops the program.
        stepper.close()
        GPIO.cleanup()


# Do not start the hardware loop if another program imports this file.
if __name__ == "__main__":
    main()
