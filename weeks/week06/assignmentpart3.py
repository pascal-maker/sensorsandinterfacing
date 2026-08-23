"""Assignment 3: sound a GPIO 12 buzzer whenever the MPU6050 moves."""

from pathlib import Path
import sys
import time

import RPi.GPIO as GPIO

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from hardware import MPU6050


BUZZER_PIN = 12

# Lower values detect smaller movements. Increase this if vibration or sensor
# noise causes false alarms. This is measured as total acceleration change in g.
MOVEMENT_THRESHOLD = 0.20
SAMPLE_DELAY = 0.02


def movement_amount(previous, current):
    """Return the sum of absolute acceleration changes across all axes."""
    return sum(abs(new - old) for old, new in zip(previous, current))


def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUZZER_PIN, GPIO.OUT, initial=GPIO.LOW)

    sensor = MPU6050(address=0x68)
    try:
        sensor.setup()
        sensor.accel_range = 2
        previous_acceleration = sensor.get_acceleration()

        while True:
            acceleration = sensor.get_acceleration()
            movement = movement_amount(previous_acceleration, acceleration)
            moving = movement > MOVEMENT_THRESHOLD

            GPIO.output(BUZZER_PIN, GPIO.HIGH if moving else GPIO.LOW)
            print(
                f"Movement: {movement:.3f} g | "
                f"threshold: {MOVEMENT_THRESHOLD:.3f} g | "
                f"buzzer: {'ON' if moving else 'OFF'}"
            )

            previous_acceleration = acceleration
            time.sleep(SAMPLE_DELAY)
    except KeyboardInterrupt:
        print("\nProgram stopped")
    finally:
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        sensor.close()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
