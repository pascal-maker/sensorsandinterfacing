"""Assignment 2: display MPU6050 temperature, acceleration, and gyro data."""

from pathlib import Path
import sys
import time

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from hardware import MPU6050


def main():
    sensor = MPU6050(address=0x68)
    try:
        sensor.setup()
        sensor.range = (2, 250)

        while True:
            temperature = sensor.get_temperature()
            accel_x, accel_y, accel_z = sensor.get_acceleration()
            gyro_x, gyro_y, gyro_z = sensor.get_gyroscope()

            print(f"Temperature: {temperature:.2f} °C")
            print(f"Acceleration: X={accel_x:.3f} g, Y={accel_y:.3f} g, Z={accel_z:.3f} g")
            print(f"Gyroscope: X={gyro_x:.2f} °/s, Y={gyro_y:.2f} °/s, Z={gyro_z:.2f} °/s")
            print()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nProgram stopped")
    finally:
        sensor.close()


if __name__ == "__main__":
    main()
