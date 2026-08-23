"""Assignment 1: demonstrate the reusable MPU6050 class."""

from pathlib import Path
import sys
import time

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from hardware import MPU6050


def main():
    # The constructor accepts the I2C address requested by the assignment.
    sensor = MPU6050(address=0x68)
    try:
        sensor.setup()
        sensor.range = (2, 250)

        while True:
            accel_x, accel_y, accel_z = sensor.get_acceleration()
            gyro_x, gyro_y, gyro_z = sensor.get_gyroscope()

            print(f"Acceleration (g): X={accel_x:7.3f}, Y={accel_y:7.3f}, Z={accel_z:7.3f}")
            print(f"Gyroscope (°/s): X={gyro_x:7.2f}, Y={gyro_y:7.2f}, Z={gyro_z:7.2f}")
            print()
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nProgram stopped")
    finally:
        sensor.close()


if __name__ == "__main__":
    main()
