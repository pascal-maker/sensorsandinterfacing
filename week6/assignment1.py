import smbus
import time


class MPU6050:
    """
    Class to communicate with the MPU6050 IMU over I2C.

    This class can:
    - wake the sensor up
    - set accelerometer range
    - set gyroscope range
    - read acceleration in X, Y, Z
    - read gyroscope values in X, Y, Z

    The MPU6050 stores values in registers.
    Some values use 2 registers (1 high byte + 1 low byte).
    """

    # =========================================================
    # REGISTER ADDRESSES
    # =========================================================

    # Power management register
    # We use this to wake the sensor up
    PWR_MGMT_1 = 0x6B

    # Accelerometer configuration register
    # We use this to choose the accelerometer range
    ACCEL_CONFIG = 0x1C

    # Gyroscope configuration register
    # We use this to choose the gyroscope range
    GYRO_CONFIG = 0x1B

    # Start register of the accelerometer measurements
    # From here we can read 6 bytes in a row:
    # XH, XL, YH, YL, ZH, ZL
    ACCEL_START = 0x3B

    # Start register of the gyroscope measurements
    # From here we can also read 6 bytes in a row:
    # XH, XL, YH, YL, ZH, ZL
    GYRO_START = 0x43

    # =========================================================
    # CONSTRUCTOR
    # =========================================================

    def __init__(self, address=0x68, bus_number=1, accel_range=2, gyro_range=250):
        """
        Constructor of the class.

        Parameters:
        - address: I2C address of the MPU6050 (default = 0x68)
        - bus_number: Raspberry Pi I2C bus number (usually 1)
        - accel_range: desired accelerometer range in g (2, 4, 8, or 16)
        - gyro_range: desired gyroscope range in degrees/second
                      (250, 500, 1000, or 2000)

        We store these values inside the object using self.
        """

        # Store the I2C address of the sensor
        self.address = address

        # Open the I2C bus
        # On Raspberry Pi, bus 1 is usually the correct one
        self.bus = smbus.SMBus(bus_number)

        # Store the chosen accelerometer range
        self.accel_range = accel_range

        # Store the chosen gyroscope range
        self.gyro_range = gyro_range

    # =========================================================
    # SETUP METHOD
    # =========================================================

    def setup(self):
        """
        Configure the sensor.

        This method does 3 important things:
        1. Wake the sensor up
        2. Set the accelerometer range
        3. Set the gyroscope range
        """

        # -----------------------------------------------------
        # 1. Wake up the MPU6050
        # -----------------------------------------------------
        #
        # By default, the MPU6050 starts in sleep mode.
        # If we do not wake it up, readings may be wrong or zero.
        #
        # Writing 0 to register 0x6B clears the sleep bit.
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0)

        # -----------------------------------------------------
        # 2. Set accelerometer configuration
        # -----------------------------------------------------
        #
        # We first determine which value must be written
        # to the ACCEL_CONFIG register, based on self.accel_range
        accel_config_value = self._get_accel_config_value()

        # Write that value to the accelerometer configuration register
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, accel_config_value)

        # -----------------------------------------------------
        # 3. Set gyroscope configuration
        # -----------------------------------------------------
        #
        # Same idea for the gyroscope
        gyro_config_value = self._get_gyro_config_value()

        # Write that value to the gyroscope configuration register
        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, gyro_config_value)

        # Short pause to make sure the sensor has time to apply the settings
        time.sleep(0.1)

    # =========================================================
    # STATIC HELPER METHOD
    # =========================================================

    @staticmethod
    def bytes_to_int(msb, lsb):
        """
        Combine two bytes into one signed 16-bit integer.

        Parameters:
        - msb = Most Significant Byte (high byte)
        - lsb = Least Significant Byte (low byte)

        The MPU6050 stores values in big-endian format:
        first the high byte, then the low byte.

        Example:
        msb = 0x01
        lsb = 0x02

        Then the full value becomes:
        0x0102

        We combine them like this:
        (msb << 8) | lsb

        Then we check if the value is negative using two's complement:
        - if bit 15 is 1, the number is negative
        - then subtract 65536 to convert it to a signed value
        """

        # Shift the high byte 8 places to the left
        # This moves it to the upper half of the 16-bit number
        value = (msb << 8) | lsb

        # Check the sign bit (bit 15)
        # 0x8000 = 1000 0000 0000 0000 in binary
        # If this bit is 1, then the number is negative
        if value & 0x8000:
            value -= 65536  # same as subtracting 2^16

        return value

    # =========================================================
    # PRIVATE HELPER METHOD TO READ 3 AXES
    # =========================================================

    def _read_xyz_raw(self, start_register):
        """
        Read 3 raw values (X, Y, Z) from the sensor.

        Parameters:
        - start_register:
            for accelerometer = 0x3B
            for gyroscope     = 0x43

        This method:
        1. reads 6 bytes in one I2C transaction
        2. combines them into 3 signed 16-bit integers
        3. returns x, y, z raw values
        """

        # Read 6 bytes in one go starting from start_register
        #
        # For accelerometer:
        # data[0] = X high byte
        # data[1] = X low byte
        # data[2] = Y high byte
        # data[3] = Y low byte
        # data[4] = Z high byte
        # data[5] = Z low byte
        data = self.bus.read_i2c_block_data(self.address, start_register, 6)

        # Combine the first 2 bytes into the X value
        x = self.bytes_to_int(data[0], data[1])

        # Combine the next 2 bytes into the Y value
        y = self.bytes_to_int(data[2], data[3])

        # Combine the last 2 bytes into the Z value
        z = self.bytes_to_int(data[4], data[5])

        # Return all 3 values at once
        return x, y, z

    # =========================================================
    # PUBLIC METHOD: READ ACCELEROMETER
    # =========================================================

    def read_accel(self):
        """
        Read accelerometer values and return them in g-forces.

        Steps:
        1. Read raw X, Y, Z values
        2. Determine the correct scale factor
        3. Divide raw values by the scale factor
        4. Return x, y, z in g
        """

        # Read raw accelerometer values from registers starting at 0x3B
        raw_x, raw_y, raw_z = self._read_xyz_raw(self.ACCEL_START)

        # Get the correct accelerometer scale factor
        scale = self._get_accel_scale_factor()

        # Convert raw values to g
        x = raw_x / scale
        y = raw_y / scale
        z = raw_z / scale

        return x, y, z

    # =========================================================
    # PUBLIC METHOD: READ GYROSCOPE
    # =========================================================

    def read_gyro(self):
        """
        Read gyroscope values and return them in degrees per second.

        Steps:
        1. Read raw X, Y, Z values
        2. Determine the correct scale factor
        3. Divide raw values by the scale factor
        4. Return x, y, z in °/s
        """

        # Read raw gyroscope values from registers starting at 0x43
        raw_x, raw_y, raw_z = self._read_xyz_raw(self.GYRO_START)

        # Get the correct gyroscope scale factor
        scale = self._get_gyro_scale_factor()

        # Convert raw values to degrees per second
        x = raw_x / scale
        y = raw_y / scale
        z = raw_z / scale

        return x, y, z

    # =========================================================
    # PRIVATE HELPER: ACCEL REGISTER CONFIG VALUE
    # =========================================================

    def _get_accel_config_value(self):
        """
        Convert the chosen accelerometer range to the correct
        register value for ACCEL_CONFIG.

        ACCEL_CONFIG uses bits 4 and 3 (AFS_SEL):
        - ±2g  -> 00 -> 0x00
        - ±4g  -> 01 -> 0x08
        - ±8g  -> 10 -> 0x10
        - ±16g -> 11 -> 0x18
        """

        if self.accel_range == 2:
            return 0x00   # bits 4 and 3 = 00
        elif self.accel_range == 4:
            return 0x08   # bits 4 and 3 = 01
        elif self.accel_range == 8:
            return 0x10   # bits 4 and 3 = 10
        elif self.accel_range == 16:
            return 0x18   # bits 4 and 3 = 11
        else:
            raise ValueError("accel_range must be 2, 4, 8, or 16")

    # =========================================================
    # PRIVATE HELPER: GYRO REGISTER CONFIG VALUE
    # =========================================================

    def _get_gyro_config_value(self):
        """
        Convert the chosen gyroscope range to the correct
        register value for GYRO_CONFIG.

        GYRO_CONFIG uses bits 4 and 3 (FS_SEL):
        - ±250   -> 00 -> 0x00
        - ±500   -> 01 -> 0x08
        - ±1000  -> 10 -> 0x10
        - ±2000  -> 11 -> 0x18
        """

        if self.gyro_range == 250:
            return 0x00   # bits 4 and 3 = 00
        elif self.gyro_range == 500:
            return 0x08   # bits 4 and 3 = 01
        elif self.gyro_range == 1000:
            return 0x10   # bits 4 and 3 = 10
        elif self.gyro_range == 2000:
            return 0x18   # bits 4 and 3 = 11
        else:
            raise ValueError("gyro_range must be 250, 500, 1000, or 2000")

    # =========================================================
    # PRIVATE HELPER: ACCEL SCALE FACTOR
    # =========================================================

    def _get_accel_scale_factor(self):
        """
        Return the correct accelerometer scale factor.

        These values come from the datasheet:
        - ±2g  -> 16384 LSB/g
        - ±4g  -> 8192 LSB/g
        - ±8g  -> 4096 LSB/g
        - ±16g -> 2048 LSB/g
        """

        if self.accel_range == 2:
            return 16384.0
        elif self.accel_range == 4:
            return 8192.0
        elif self.accel_range == 8:
            return 4096.0
        elif self.accel_range == 16:
            return 2048.0

    # =========================================================
    # PRIVATE HELPER: GYRO SCALE FACTOR
    # =========================================================

    def _get_gyro_scale_factor(self):
        """
        Return the correct gyroscope scale factor.

        These values come from the datasheet:
        - ±250   -> 131 LSB/(°/s)
        - ±500   -> 65.5 LSB/(°/s)
        - ±1000  -> 32.8 LSB/(°/s)
        - ±2000  -> 16.4 LSB/(°/s)
        """

        if self.gyro_range == 250:
            return 131.0
        elif self.gyro_range == 500:
            return 65.5
        elif self.gyro_range == 1000:
            return 32.8
        elif self.gyro_range == 2000:
            return 16.4


# =========================================================
# MAIN TEST PROGRAM
# =========================================================

# Create an MPU6050 object
# We choose:
# - address 0x68
# - accelerometer range ±2g
# - gyroscope range ±250 °/s
sensor = MPU6050(address=0x68, accel_range=2, gyro_range=250)

# Configure the sensor
sensor.setup()

# Keep reading and printing values forever
while True:
    # Read acceleration in g
    ax, ay, az = sensor.read_accel()

    # Read rotation speed in degrees per second
    gx, gy, gz = sensor.read_gyro()

    # Display acceleration
    print(f"Accel: X={ax:.2f}g  Y={ay:.2f}g  Z={az:.2f}g")

    # Display gyroscope
    print(f"Gyro : X={gx:.2f}°/s  Y={gy:.2f}°/s  Z={gz:.2f}°/s")

    print("-" * 50)

    # Wait half a second before next reading
    time.sleep(0.5)