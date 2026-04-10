import smbus
import time


class MPU6050:
    """
    Simple class for the MPU6050 sensor.
    It can:
    - wake up the sensor
    - set accelerometer range
    - set gyroscope range
    - read acceleration
    - read gyroscope values
    """

    # ==============================
    # Important register addresses
    # ==============================
    PWR_MGMT_1 = 0x6B      # register to wake up sensor
    ACCEL_CONFIG = 0x1C    # register for accelerometer range
    GYRO_CONFIG = 0x1B     # register for gyroscope range

    ACCEL_XOUT_H = 0x3B    # first accel register
    GYRO_XOUT_H = 0x43     # first gyro register

    def __init__(self, address=0x68, bus_number=1, accel_range=2, gyro_range=250):
        """
        Constructor.

        address      = I2C address of MPU6050
        bus_number   = usually 1 on Raspberry Pi
        accel_range  = 2, 4, 8, or 16 g
        gyro_range   = 250, 500, 1000, or 2000 °/s
        """

        self.address = address
        self.bus = smbus.SMBus(bus_number)

        self.accel_range = accel_range
        self.gyro_range = gyro_range

    def setup(self):
        """
        Prepare the sensor:
        1. wake it up
        2. set accel range
        3. set gyro range
        """

        # Wake up sensor by writing 0 to power management register
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0)

        # Set accelerometer range
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, self._accel_range_to_register())

        # Set gyroscope range
        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, self._gyro_range_to_register())

        # Small delay so settings can settle
        time.sleep(0.1)

    @staticmethod
    def convert_bytes(msb, lsb):
        """
        Convert 2 bytes into one signed 16-bit integer.

        Step 1: glue bytes together
        Step 2: check if number is negative
        Step 3: if negative, convert from two's complement
        """

        # Combine MSB and LSB into one 16-bit value
        value = (msb << 8) | lsb

        # If sign bit is 1, convert to negative value
        if value & 0x8000:
            value -= 65536

        return value

    def _read_three_axes_raw(self, start_register):
        """
        Read 6 bytes starting from start_register.
        Return raw X, Y, Z values.
        """

        # Read 6 bytes in one transaction
        data = self.bus.read_i2c_block_data(self.address, start_register, 6)

        # Convert the bytes into 3 signed integers
        x = self.convert_bytes(data[0], data[1])
        y = self.convert_bytes(data[2], data[3])
        z = self.convert_bytes(data[4], data[5])

        return x, y, z

    def read_accel(self):
        """
        Read acceleration in g.
        """
        raw_x, raw_y, raw_z = self._read_three_axes_raw(self.ACCEL_XOUT_H)

        # Divide by correct scale factor
        scale = self._accel_scale_factor()

        x = raw_x / scale
        y = raw_y / scale
        z = raw_z / scale

        return x, y, z

    def read_gyro(self):
        """
        Read gyroscope values in degrees per second.
        """
        raw_x, raw_y, raw_z = self._read_three_axes_raw(self.GYRO_XOUT_H)

        # Divide by correct scale factor
        scale = self._gyro_scale_factor()

        x = raw_x / scale
        y = raw_y / scale
        z = raw_z / scale

        return x, y, z

    def _accel_range_to_register(self):
        """
        Convert accel range to register value.
        """

        if self.accel_range == 2:
            return 0x00   # ±2g
        elif self.accel_range == 4:
            return 0x08   # ±4g
        elif self.accel_range == 8:
            return 0x10   # ±8g
        elif self.accel_range == 16:
            return 0x18   # ±16g
        else:
            raise ValueError("accel_range must be 2, 4, 8, or 16")

    def _gyro_range_to_register(self):
        """
        Convert gyro range to register value.
        """

        if self.gyro_range == 250:
            return 0x00   # ±250 °/s
        elif self.gyro_range == 500:
            return 0x08   # ±500 °/s
        elif self.gyro_range == 1000:
            return 0x10   # ±1000 °/s
        elif self.gyro_range == 2000:
            return 0x18   # ±2000 °/s
        else:
            raise ValueError("gyro_range must be 250, 500, 1000, or 2000")

    def _accel_scale_factor(self):
        """
        Return the correct accel scale factor.
        """

        if self.accel_range == 2:
            return 16384.0
        elif self.accel_range == 4:
            return 8192.0
        elif self.accel_range == 8:
            return 4096.0
        elif self.accel_range == 16:
            return 2048.0

    def _gyro_scale_factor(self):
        """
        Return the correct gyro scale factor.
        """

        if self.gyro_range == 250:
            return 131.0
        elif self.gyro_range == 500:
            return 65.5
        elif self.gyro_range == 1000:
            return 32.8
        elif self.gyro_range == 2000:
            return 16.4


# ======================================
# Test program
# ======================================

sensor = MPU6050(address=0x68, accel_range=2, gyro_range=250)
sensor.setup()

while True:
    ax, ay, az = sensor.read_accel()
    gx, gy, gz = sensor.read_gyro()

    print(f"Accel: X={ax:.2f}g  Y={ay:.2f}g  Z={az:.2f}g")
    print(f"Gyro : X={gx:.2f}°/s  Y={gy:.2f}°/s  Z={gz:.2f}°/s")
    print("-" * 50)

    time.sleep(0.5)