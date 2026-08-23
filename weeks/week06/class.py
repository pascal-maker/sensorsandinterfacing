"""Assignment 1: demonstrate the reusable MPU6050 class."""

# Path and sys let this file find the shared hardware package in the repository.
# time is used to pause briefly between measurements.
from pathlib import Path
import sys
import time

# This file is in weeks/week06, so parents[2] is the repository root.
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
# Add the repository root to Python's module search path if it is not there yet.
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

# Import the reusable MPU6050 driver from hardware/mpu6050.py.
from hardware import MPU6050


def main():
    # Create the sensor object at the MPU6050's usual I2C address, 0x68.
    sensor = MPU6050(address=0x68)
    try:
        # Wake the sensor and configure its accelerometer and gyroscope registers.
        sensor.setup()

        # Use an acceleration range of +/-2 g and a gyroscope range of
        # +/-250 degrees per second.
        sensor.range = (2, 250)

        # Keep reading and displaying measurements until Ctrl+C is pressed.
        while True:
            # Each method returns three values, one for the X, Y, and Z axes.
            # Acceleration is measured in g. When the sensor is flat and still,
            # X and Y should be near 0 g while Z should be near 1 g.
            accel_x, accel_y, accel_z = sensor.get_acceleration()

            # Gyroscope values are rotation speeds in degrees per second.
            # All three values should be near zero while the sensor is still.
            gyro_x, gyro_y, gyro_z = sensor.get_gyroscope()

            # 7.3f and 7.2f align the values and select the decimal precision.
            print(f"Acceleration (g): X={accel_x:7.3f}, Y={accel_y:7.3f}, Z={accel_z:7.3f}")
            print(f"Gyroscope (°/s): X={gyro_x:7.2f}, Y={gyro_y:7.2f}, Z={gyro_z:7.2f}")
            # Print a blank line, then wait half a second before reading again.
            print()
            time.sleep(0.5)
    except KeyboardInterrupt:
        # Ctrl+C stops the infinite loop without showing an error traceback.
        print("\nProgram stopped")
    finally:
        # Always close the I2C bus, even when the program stops due to an error.
        sensor.close()


# Run main only when this file is executed directly, not when it is imported.
if __name__ == "__main__":
    main()
