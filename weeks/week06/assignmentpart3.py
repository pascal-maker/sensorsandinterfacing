"""Assignment 3: sound a GPIO 12 buzzer whenever the MPU6050 moves."""

# Path and sys let this file find the shared hardware package in the repository.
# time controls how frequently movement is measured.
from pathlib import Path
import sys
import time

# RPi.GPIO controls the Raspberry Pi pin connected to the buzzer.
import RPi.GPIO as GPIO

# This file is in weeks/week06, so parents[2] is the repository root.
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
# Add the repository root to Python's module search path if necessary.
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

# Import the reusable MPU6050 driver from hardware/mpu6050.py.
from hardware import MPU6050


# BCM GPIO 12 is the output pin connected to the buzzer.
BUZZER_PIN = 12

# Lower values detect smaller movements. Increase this if vibration or sensor
# noise causes false alarms. This is measured as total acceleration change in g.
MOVEMENT_THRESHOLD = 0.20

# Wait 0.02 seconds between readings, for about 50 samples per second.
SAMPLE_DELAY = 0.02


def movement_amount(previous, current):
    """Return the sum of absolute acceleration changes across all axes."""
    # zip pairs the old and new X, Y, and Z values. The absolute differences
    # are added so movement in either direction produces a positive result.
    return sum(abs(new - old) for old, new in zip(previous, current))


def main():
    # Hide harmless GPIO warnings and use Broadcom (BCM) pin numbering.
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # Configure GPIO 12 as an output and make sure the buzzer starts switched off.
    GPIO.setup(BUZZER_PIN, GPIO.OUT, initial=GPIO.LOW)

    # Create the sensor object at the MPU6050's usual I2C address, 0x68.
    sensor = MPU6050(address=0x68)
    try:
        # Wake the sensor and configure its accelerometer and gyro registers.
        sensor.setup()

        # Use the most sensitive accelerometer range, from -2 g to +2 g.
        sensor.accel_range = 2

        # Save the first reading so it can be compared with the next reading.
        previous_acceleration = sensor.get_acceleration()

        # Continue detecting movement until the user presses Ctrl+C.
        while True:
            # Read the current X, Y, and Z acceleration values in g.
            acceleration = sensor.get_acceleration()

            # Compare the current reading with the previous reading. A larger
            # change means that the sensor moved more between the two samples.
            movement = movement_amount(previous_acceleration, acceleration)

            # Movement is detected when the change exceeds the adjustable limit.
            moving = movement > MOVEMENT_THRESHOLD

            # Switch the buzzer on during movement and off when the sensor is still.
            GPIO.output(BUZZER_PIN, GPIO.HIGH if moving else GPIO.LOW)

            # Display the measured change, configured limit, and buzzer state.
            print(
                f"Movement: {movement:.3f} g | "
                f"threshold: {MOVEMENT_THRESHOLD:.3f} g | "
                f"buzzer: {'ON' if moving else 'OFF'}"
            )

            # The current reading becomes the reference for the next comparison.
            previous_acceleration = acceleration
            time.sleep(SAMPLE_DELAY)
    except KeyboardInterrupt:
        # Ctrl+C stops the infinite loop without displaying an error traceback.
        print("\nProgram stopped")
    finally:
        # Always silence the buzzer, close I2C, and release the GPIO resources,
        # including when the program stops because of an unexpected error.
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        sensor.close()
        GPIO.cleanup()


# Run main only when this file is executed directly, not when it is imported.
if __name__ == "__main__":
    main()
