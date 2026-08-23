"""Assignment 2: display MPU6050 temperature, acceleration, and gyro data."""

# Path and sys let this file find the shared hardware package in the repository.
# time provides the one-second delay between measurements.
from pathlib import Path
import sys
import time

# This file is in weeks/week06, so parents[2] is the repository root.
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
# Add the repository root to Python's module search path if necessary.
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

# Import the reusable driver from hardware/mpu6050.py.
from hardware import MPU6050


def main():
    # Create the sensor object at the MPU6050's usual I2C address, 0x68.
    sensor = MPU6050(address=0x68)
    try:
        # Wake the sensor and configure its accelerometer and gyro registers.
        sensor.setup()

        # Select an accelerometer range of +/-2 g and a gyroscope range of
        # +/-250 degrees per second.
        sensor.range = (2, 250)

        # Continue taking measurements until the user presses Ctrl+C.
        while True:
            # Read the sensor chip's internal temperature in degrees Celsius.
            # This is the chip temperature, not an exact room temperature.
            temperature = sensor.get_temperature()

            # Return acceleration along the X, Y, and Z axes in g. When the
            # sensor is flat and still, the results should be near 0, 0, and 1 g.
            accel_x, accel_y, accel_z = sensor.get_acceleration()

            # Return rotation speeds around all axes in degrees per second.
            # These values should be close to zero while the sensor is still.
            gyro_x, gyro_y, gyro_z = sensor.get_gyroscope()

            # .2f and .3f select how many digits appear after the decimal point.
            print(f"Temperature: {temperature:.2f} °C")
            print(f"Acceleration: X={accel_x:.3f} g, Y={accel_y:.3f} g, Z={accel_z:.3f} g")
            print(f"Gyroscope: X={gyro_x:.2f} °/s, Y={gyro_y:.2f} °/s, Z={gyro_z:.2f} °/s")
            # Separate each group of results and update about once per second.
            print()
            time.sleep(1)
    except KeyboardInterrupt:
        # Ctrl+C stops the infinite loop without showing an error traceback.
        print("\nProgram stopped")
    finally:
        # Always release the I2C bus, even if an unexpected error occurs.
        sensor.close()


# Run main only when this file is executed directly, not when it is imported.
if __name__ == "__main__":
    main()
