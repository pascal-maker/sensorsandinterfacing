"""Assignment C: toggle DC direction and control speed with a potentiometer."""

# Path and sys make the repository's shared hardware package importable.
from pathlib import Path
import sys
import time

import RPi.GPIO as GPIO

# This script is in weeks/week07, two directories below the repository root.
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from hardware import ADS7830, DCMotor

# GPIO 16 toggles motor state; ADS7830 channel 3 reads the potentiometer.
BUTTON_PIN = 16
POTENTIOMETER_CHANNEL = 3


def main():
    # Use Broadcom GPIO numbering and the Pi's internal button pull-up.
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # The ADS7830 changes analog voltage into an integer from 0 through 255.
    adc = ADS7830(address=0x48)
    # GPIO 14 and 15 connect to the two L293D H-bridge control inputs.
    motor = DCMotor(left_pin=14, right_pin=15)

    # Each debounced press advances OFF -> LEFT -> RIGHT -> OFF.
    GPIO.add_event_detect(
        BUTTON_PIN,
        GPIO.FALLING,
        callback=lambda channel: motor.toggle(),
        bouncetime=200,
    )

    try:
        while True:
            # Convert the complete ADC range linearly into a PWM percentage.
            raw_value = adc.read_raw(POTENTIOMETER_CHANNEL)
            motor.set_speed(raw_value / 255 * 100)

            # This output also lets the exercise be checked without motor power.
            print(
                f"Mode: {motor.state:5} | ADC: {raw_value:3} | "
                f"Speed: {motor.speed:5.1f}%"
            )
            # Update ten times per second without flooding the console.
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nDC motor stopped")
    finally:
        # Stop PWM before releasing I2C and all GPIO resources.
        motor.close()
        adc.close()
        GPIO.cleanup()


# Run only when executed directly, not when imported by another script.
if __name__ == "__main__":
    main()
