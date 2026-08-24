"""Compatibility entry point for the reusable :class:`hardware.MPU6050`."""

import time

from hardware import MPU6050

__all__ = ["MPU6050"]


def main():
    sensor = MPU6050(address=0x68)
    try:
        sensor.setup()
        while True:
            acceleration = sensor.get_acceleration()
            gyroscope = sensor.get_gyroscope()
            temperature = sensor.get_temperature()
            print(f"Temperature: {temperature:.2f} °C")
            print(f"Acceleration (g): X={acceleration[0]:.2f}, Y={acceleration[1]:.2f}, Z={acceleration[2]:.2f}")
            print(f"Gyroscope (°/s): X={gyroscope[0]:.2f}, Y={gyroscope[1]:.2f}, Z={gyroscope[2]:.2f}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nProgram stopped")
    finally:
        sensor.close()


if __name__ == "__main__":
    main()
