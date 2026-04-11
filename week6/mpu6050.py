"""
Week 6 — MPU6050 IMU Sensor
Class: MPU6050
"""

import smbus
import time


class MPU6050:
    """
    Driver for the MPU6050 6-axis IMU (accelerometer + gyroscope).
    Connected via I2C bus 1, default address 0x68.
    """

    # Register addresses
    PWR_MGMT_1   = 0x6B
    ACCEL_CONFIG = 0x1C
    GYRO_CONFIG  = 0x1B
    DATA_START   = 0x3B   # first of 14 consecutive data bytes

    # Scale factors indexed by range setting (0–3)
    ACCEL_SCALE = {0: 16384.0, 1: 8192.0, 2: 4096.0, 3: 2048.0}
    GYRO_SCALE  = {0: 131.0,   1: 65.5,   2: 32.8,   3: 16.4}

    def __init__(self, address=0x68, bus_num=1):
        self.address = address
        self._bus = smbus.SMBus(bus_num)
        self._accel_range = 0   # ±2 g
        self._gyro_range  = 0   # ±250 °/s
        self._wake()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _wake(self):
        """Take sensor out of sleep mode."""
        self._bus.write_byte_data(self.address, self.PWR_MGMT_1, 0x00)
        time.sleep(0.1)

    def set_accel_range(self, setting=0):
        """
        Set accelerometer full-scale range.
        0 → ±2g, 1 → ±4g, 2 → ±8g, 3 → ±16g
        """
        if setting not in self.ACCEL_SCALE:
            raise ValueError("setting must be 0–3")
        self._accel_range = setting
        self._bus.write_byte_data(self.address, self.ACCEL_CONFIG, (setting & 0x03) << 3)
        time.sleep(0.05)

    def set_gyro_range(self, setting=0):
        """
        Set gyroscope full-scale range.
        0 → ±250 °/s, 1 → ±500, 2 → ±1000, 3 → ±2000
        """
        if setting not in self.GYRO_SCALE:
            raise ValueError("setting must be 0–3")
        self._gyro_range = setting
        self._bus.write_byte_data(self.address, self.GYRO_CONFIG, (setting & 0x03) << 3)
        time.sleep(0.05)

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------

    @staticmethod
    def _to_signed(high, low):
        """Combine two bytes into a signed 16-bit integer (two's complement)."""
        value = (high << 8) | low
        return value - 65536 if value & 0x8000 else value

    def read_raw(self):
        """
        Return a dict with raw 16-bit values for accel, temp, and gyro.
        """
        data = self._bus.read_i2c_block_data(self.address, self.DATA_START, 14)
        return {
            "accel": (
                self._to_signed(data[0], data[1]),
                self._to_signed(data[2], data[3]),
                self._to_signed(data[4], data[5]),
            ),
            "temp_raw": self._to_signed(data[6], data[7]),
            "gyro": (
                self._to_signed(data[8],  data[9]),
                self._to_signed(data[10], data[11]),
                self._to_signed(data[12], data[13]),
            ),
        }

    def read(self):
        """
        Return a dict with human-readable values:
          accel_g   — acceleration in g (x, y, z)
          temp_c    — temperature in °C
          gyro_dps  — angular velocity in °/s (x, y, z)
        """
        raw = self.read_raw()
        a_scale = self.ACCEL_SCALE[self._accel_range]
        g_scale = self.GYRO_SCALE[self._gyro_range]

        ax, ay, az = raw["accel"]
        gx, gy, gz = raw["gyro"]

        return {
            "accel_g":  (ax / a_scale, ay / a_scale, az / a_scale),
            "temp_c":   raw["temp_raw"] / 340.0 + 36.53,
            "gyro_dps": (gx / g_scale, gy / g_scale, gz / g_scale),
        }

    def print_data(self):
        d = self.read()
        ax, ay, az = d["accel_g"]
        gx, gy, gz = d["gyro_dps"]
        print(f"Accel  (g)   x={ax:+.3f}  y={ay:+.3f}  z={az:+.3f}")
        print(f"Gyro (°/s)  x={gx:+.3f}  y={gy:+.3f}  z={gz:+.3f}")
        print(f"Temp         {d['temp_c']:.2f} °C\n")

    def close(self):
        self._bus.close()


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    imu = MPU6050()
    imu.set_accel_range(0)   # ±2g
    imu.set_gyro_range(0)    # ±250 °/s

    try:
        while True:
            imu.print_data()
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        imu.close()
