"""Reusable MPU6050 accelerometer, gyroscope, and temperature driver."""

import time

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus


class MPU6050:
    PWR_MGMT_1 = 0x6B
    GYRO_CONFIG = 0x1B
    ACCEL_CONFIG = 0x1C
    ACCEL_XOUT_H = 0x3B
    TEMP_OUT_H = 0x41
    GYRO_XOUT_H = 0x43

    ACCEL_SCALES = {2: 16384.0, 4: 8192.0, 8: 4096.0, 16: 2048.0}
    GYRO_SCALES = {250: 131.0, 500: 65.5, 1000: 32.8, 2000: 16.4}

    def __init__(self, address=0x68, bus_id=1):
        self.address = address
        self.bus = SMBus(bus_id)
        self._accel_range = 2
        self._gyro_range = 250

    def setup(self):
        """Wake the sensor and set its accelerometer and gyroscope ranges."""
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0x00)
        self._write_accel_range()
        self._write_gyro_range()
        time.sleep(0.1)

    @staticmethod
    def combine_bytes(high_byte, low_byte):
        """Combine two big-endian bytes as a signed 16-bit two's-complement value."""
        value = (high_byte << 8) | low_byte
        return value - 0x10000 if value & 0x8000 else value

    @staticmethod
    def _range_register_value(options, selected_range):
        # The range selection occupies bits 4 and 3 of both config registers.
        return list(options).index(selected_range) << 3

    def _write_accel_range(self):
        value = self._range_register_value(self.ACCEL_SCALES, self._accel_range)
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, value)

    def _write_gyro_range(self):
        value = self._range_register_value(self.GYRO_SCALES, self._gyro_range)
        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, value)

    @property
    def accel_range(self):
        return self._accel_range

    @accel_range.setter
    def accel_range(self, value):
        if value not in self.ACCEL_SCALES:
            raise ValueError("Accelerometer range must be 2, 4, 8, or 16 g")
        self._accel_range = value
        self._write_accel_range()

    @property
    def gyro_range(self):
        return self._gyro_range

    @gyro_range.setter
    def gyro_range(self, value):
        if value not in self.GYRO_SCALES:
            raise ValueError("Gyroscope range must be 250, 500, 1000, or 2000 dps")
        self._gyro_range = value
        self._write_gyro_range()

    @property
    def range(self):
        """Return both configured ranges as (accelerometer g, gyroscope dps)."""
        return self.accel_range, self.gyro_range

    @range.setter
    def range(self, values):
        accel_range, gyro_range = values
        if accel_range not in self.ACCEL_SCALES:
            raise ValueError("Accelerometer range must be 2, 4, 8, or 16 g")
        if gyro_range not in self.GYRO_SCALES:
            raise ValueError("Gyroscope range must be 250, 500, 1000, or 2000 dps")
        self._accel_range = accel_range
        self._gyro_range = gyro_range
        self._write_accel_range()
        self._write_gyro_range()

    def _read_acceleration(self):
        """Read all three acceleration axes in one six-byte I2C transaction."""
        data = self.bus.read_i2c_block_data(self.address, self.ACCEL_XOUT_H, 6)
        scale = self.ACCEL_SCALES[self.accel_range]
        return tuple(
            self.combine_bytes(data[index], data[index + 1]) / scale
            for index in (0, 2, 4)
        )

    def _read_gyroscope(self):
        """Read all three gyroscope axes in one six-byte I2C transaction."""
        data = self.bus.read_i2c_block_data(self.address, self.GYRO_XOUT_H, 6)
        scale = self.GYRO_SCALES[self.gyro_range]
        return tuple(
            self.combine_bytes(data[index], data[index + 1]) / scale
            for index in (0, 2, 4)
        )

    def get_acceleration(self):
        """Return acceleration (x, y, z) in g."""
        return self._read_acceleration()

    def get_gyroscope(self):
        """Return angular velocity (x, y, z) in degrees per second."""
        return self._read_gyroscope()

    def get_temperature(self):
        data = self.bus.read_i2c_block_data(self.address, self.TEMP_OUT_H, 2)
        raw_temperature = self.combine_bytes(data[0], data[1])
        return raw_temperature / 340.0 + 36.53

    def close(self):
        self.bus.close()

    cleanup = close
