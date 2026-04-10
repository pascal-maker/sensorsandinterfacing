import smbus
import time

# =========================================================
# CONSTANTS
# =========================================================

# I2C address of the MPU6050 sensor
MPU_ADDRESS = 0x68

# Register addresses inside the MPU6050
PWR_MGMT_1   = 0x6B   # power management register
ACCEL_CONFIG = 0x1C   # accelerometer range register
GYRO_CONFIG  = 0x1B   # gyroscope range register
DATA_START   = 0x3B   # first register where measurement data starts

# Open I2C bus 1 on the Raspberry Pi
bus = smbus.SMBus(1)

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def wake_mpu():
    """
    Wake up the MPU6050.
    By default the sensor starts in sleep mode,
    so we must write 0 to register 0x6B.
    """
    bus.write_byte_data(MPU_ADDRESS, PWR_MGMT_1, 0x00)#
    time.sleep(0.1)  # short pause so the sensor has time to wake up


def set_accel_range(range_setting=0):
    """
    Set the accelerometer full-scale range.

    range_setting:
        0 -> ±2g
        1 -> ±4g
        2 -> ±8g
        3 -> ±16g

    Bits 4 and 3 of ACCEL_CONFIG are AFS_SEL[1:0].
    So we shift the chosen setting 3 positions to the left.
    """
    value = (range_setting & 0x03) << 3
    bus.write_byte_data(MPU_ADDRESS, ACCEL_CONFIG, value)
    time.sleep(0.05)


def set_gyro_range(range_setting=0):
    """
    Set the gyroscope full-scale range.

    range_setting:
        0 -> ±250 °/s
        1 -> ±500 °/s
        2 -> ±1000 °/s
        3 -> ±2000 °/s

    Bits 4 and 3 of GYRO_CONFIG are FS_SEL[1:0].
    So we shift the chosen setting 3 positions to the left.
    """
    value = (range_setting & 0x03) << 3
    bus.write_byte_data(MPU_ADDRESS, GYRO_CONFIG, value)
    time.sleep(0.05)


def read_word_2c(data, index):
    """
    Read 2 bytes from the list 'data' and combine them into 1 signed 16-bit value.

    The MPU6050 stores values as:
    - high byte first
    - low byte second

    So we combine them like this:
        value = (high_byte << 8) | low_byte

    Then we convert from two's complement if the sign bit is 1.
    """
    # Combine high byte and low byte into one 16-bit number
    value = (data[index] << 8) | data[index + 1]

    # Check if the sign bit (bit 15) is 1
    # If yes, this is a negative number in two's complement
    if value & 0x8000:
        value -= 65536   # same as subtracting 2^16

    return value


def get_accel_scale_factor(accel_range_setting):
    """
    Return the correct accelerometer scale factor in LSB/g.

    This depends on the selected accelerometer range.
    """
    if accel_range_setting == 0:
        return 16384.0   # ±2g
    elif accel_range_setting == 1:
        return 8192.0    # ±4g
    elif accel_range_setting == 2:
        return 4096.0    # ±8g
    elif accel_range_setting == 3:
        return 2048.0    # ±16g
    else:
        raise ValueError("Invalid accelerometer range setting")


def get_gyro_scale_factor(gyro_range_setting):
    """
    Return the correct gyroscope scale factor in LSB/(°/s).

    This depends on the selected gyroscope range.
    """
    if gyro_range_setting == 0:
        return 131.0     # ±250 °/s
    elif gyro_range_setting == 1:
        return 65.5      # ±500 °/s
    elif gyro_range_setting == 2:
        return 32.8      # ±1000 °/s
    elif gyro_range_setting == 3:
        return 16.4      # ±2000 °/s
    else:
        raise ValueError("Invalid gyroscope range setting")


def read_all_raw():
    """
    Read all 14 bytes starting from register 0x3B.

    These 14 bytes contain:
    - accel x high + low
    - accel y high + low
    - accel z high + low
    - temperature high + low
    - gyro x high + low
    - gyro y high + low
    - gyro z high + low
    """
    # Read 14 consecutive bytes starting from register 0x3B
    data = bus.read_i2c_block_data(MPU_ADDRESS, DATA_START, 14)

    # Convert every 2 bytes into one signed value
    accel_x = read_word_2c(data, 0)
    accel_y = read_word_2c(data, 2)
    accel_z = read_word_2c(data, 4)

    temp_raw = read_word_2c(data, 6)

    gyro_x = read_word_2c(data, 8)
    gyro_y = read_word_2c(data, 10)
    gyro_z = read_word_2c(data, 12)

    return accel_x, accel_y, accel_z, temp_raw, gyro_x, gyro_y, gyro_z


def read_scaled(accel_range_setting=0, gyro_range_setting=0):
    """
    Read all raw values and convert them to real units.

    Output:
    - acceleration in g
    - temperature in °C
    - angular velocity in °/s
    """
    # Get the correct scaling factors for the chosen ranges
    accel_scale = get_accel_scale_factor(accel_range_setting)
    gyro_scale = get_gyro_scale_factor(gyro_range_setting)

    # Read the raw sensor values
    accel_x_raw, accel_y_raw, accel_z_raw, temp_raw, gyro_x_raw, gyro_y_raw, gyro_z_raw = read_all_raw()

    # Convert raw accelerometer values to g
    accel_x_g = accel_x_raw / accel_scale
    accel_y_g = accel_y_raw / accel_scale
    accel_z_g = accel_z_raw / accel_scale

    # Convert raw temperature value to degrees Celsius
    # Formula from datasheet:
    # temp_C = raw / 340 + 36.53
    temperature_c = (temp_raw / 340.0) + 36.53

    # Convert raw gyroscope values to degrees per second
    gyro_x_dps = gyro_x_raw / gyro_scale
    gyro_y_dps = gyro_y_raw / gyro_scale
    gyro_z_dps = gyro_z_raw / gyro_scale

    # Return both raw and scaled values in a dictionary
    return {
        "accel_raw": (accel_x_raw, accel_y_raw, accel_z_raw),
        "accel_g": (accel_x_g, accel_y_g, accel_z_g),
        "temp_raw": temp_raw,
        "temp_c": temperature_c,
        "gyro_raw": (gyro_x_raw, gyro_y_raw, gyro_z_raw),
        "gyro_dps": (gyro_x_dps, gyro_y_dps, gyro_z_dps),
    }


# =========================================================
# MAIN PROGRAM
# =========================================================

try:
    # Choose the desired ranges
    accel_range_setting = 0   # 0 means ±2g
    gyro_range_setting = 0    # 0 means ±250 °/s

    # Wake up the sensor first
    wake_mpu()

    # Configure accelerometer and gyroscope range
    set_accel_range(accel_range_setting)
    set_gyro_range(gyro_range_setting)

    print("MPU6050 initialized.")
    print("Reading values...\n")

    while True:
        # Read all scaled values from the sensor
        values = read_scaled(accel_range_setting, gyro_range_setting)

        # Extract raw accelerometer values
        ax_raw, ay_raw, az_raw = values["accel_raw"]

        # Extract scaled accelerometer values in g
        ax_g, ay_g, az_g = values["accel_g"]

        # Extract raw gyroscope values
        gx_raw, gy_raw, gz_raw = values["gyro_raw"]

        # Extract scaled gyroscope values in degrees/second
        gx_dps, gy_dps, gz_dps = values["gyro_dps"]

        # Extract raw and scaled temperature
        temp_raw = values["temp_raw"]
        temp_c = values["temp_c"]

        # Print accelerometer data
        print("Accelerometer raw : X={:6d}  Y={:6d}  Z={:6d}".format(ax_raw, ay_raw, az_raw))
        print("Accelerometer (g) : X={:7.3f} Y={:7.3f} Z={:7.3f}".format(ax_g, ay_g, az_g))

        # Print gyroscope data
        print("Gyroscope raw     : X={:6d}  Y={:6d}  Z={:6d}".format(gx_raw, gy_raw, gz_raw))
        print("Gyroscope (°/s)   : X={:7.3f} Y={:7.3f} Z={:7.3f}".format(gx_dps, gy_dps, gz_dps))

        # Print temperature data
        print("Temperature raw   : {}".format(temp_raw))
        print("Temperature (°C)  : {:.2f}".format(temp_c))

        print("-" * 60)

        # Wait a little before the next reading
        time.sleep(0.5)

except KeyboardInterrupt:
    # Stop program cleanly when Ctrl+C is pressed
    print("\nProgram stopped by user.")