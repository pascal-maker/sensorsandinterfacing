"""Calculate stable pitch and roll angles with an MPU6050."""

import math  # Provides functions used to calculate angles.
import time  # Measures elapsed time and controls the sampling speed.

import smbus  # Communicates with the sensor over I2C.


# Open I2C bus 1, which is the standard I2C bus on a Raspberry Pi.
# This creates the connection that is used for every read and write below.
bus = smbus.SMBus(1)

# The MPU6050 normally uses I2C address 0x68.
# An I2C address identifies which connected device we want to communicate with.
addr = 0x68

# Register 0x6B is the power-management register. Writing 0 wakes the sensor.
# The MPU6050 starts in sleep mode after it receives power.
bus.write_byte_data(addr, 0x6B, 0)


def combine(high_byte, low_byte):
    """Combine two big-endian bytes into a signed 16-bit value."""
    # One byte contains only 8 bits, but each MPU6050 measurement contains
    # 16 bits. Therefore, every measurement has a high and a low byte.

    # Move the high byte eight bits left and attach the low byte.
    # The bitwise OR operator (|) joins the two parts together.
    value = (high_byte << 8) | low_byte

    # Values above 32767 are negative in 16-bit two's-complement format.
    # Subtracting 65536 converts these values to normal Python negatives.
    if value > 32767:
        value -= 65536

    # Send the completed positive or negative measurement back to the caller.
    return value


# Pitch is forward/backward tilt and roll is side-to-side tilt.
# Both estimated angles start at zero degrees.
# These variables will be updated on every pass through the loop.
pitch = 0
roll = 0

# Store the starting time so the first elapsed time can be calculated.
previous_time = time.time()

# The try block lets us catch Ctrl+C and stop the program neatly.
try:
    # Continue taking measurements until the user presses Ctrl+C.
    while True:
        # Read all 14 sensor bytes in one I2C transaction, starting at 0x3B:
        # accelerometer X/Y/Z, temperature, and gyroscope X/Y/Z.
        # Reading one block keeps all measurements close together in time.
        data = bus.read_i2c_block_data(addr, 0x3B, 14)

        # At the default +/-2 g range, the accelerometer sensitivity is
        # 16384 units per g. Convert its three raw readings to g.
        # Bytes 0-1 are X, bytes 2-3 are Y, and bytes 4-5 are Z.
        acc_x = combine(data[0], data[1]) / 16384
        acc_y = combine(data[2], data[3]) / 16384
        acc_z = combine(data[4], data[5]) / 16384

        # At the default +/-250 degrees/second range, the gyroscope sensitivity
        # is 131 units per degree/second. Only X and Y are needed here.
        # Bytes 6-7 contain temperature, so the gyro starts at byte 8.
        # Bytes 8-9 are gyro X and bytes 10-11 are gyro Y.
        gyro_x = combine(data[8], data[9]) / 131
        gyro_y = combine(data[10], data[11]) / 131

        # Calculate how many seconds have passed since the previous reading.
        # This is more accurate than assuming every loop takes exactly 0.05 s.
        current_time = time.time()
        delta_time = current_time - previous_time

        # Save this time so it becomes the reference during the next loop.
        previous_time = current_time

        # Calculate angles from gravity measured by the accelerometer.
        # atan2 returns radians, so multiply by 180/pi to get degrees.
        # The square root combines the other two axes into one magnitude.
        pitch_acc = math.atan2(
            acc_x, math.sqrt(acc_y**2 + acc_z**2)
        ) * 180 / math.pi
        roll_acc = math.atan2(
            acc_y, math.sqrt(acc_x**2 + acc_z**2)
        ) * 180 / math.pi

        # A complementary filter combines the strengths of both sensors:
        # the gyroscope responds quickly but drifts, while the accelerometer
        # provides a stable gravity reference but is noisy during movement.
        # Alpha controls how strongly the filter trusts the gyroscope.
        alpha = 0.98

        # Use 98% of the gyro prediction and 2% accelerometer correction.
        # Rotation speed multiplied by elapsed time gives the angle change.
        # Adding that change to the old angle produces the gyro prediction.
        pitch = alpha * (pitch + gyro_x * delta_time) + (1 - alpha) * pitch_acc
        roll = alpha * (roll + gyro_y * delta_time) + (1 - alpha) * roll_acc

        # Display both angles in degrees with two digits after the decimal point.
        # The \n is added automatically by print, so each reading gets a new line.
        print(f"Pitch: {pitch:.2f}°, Roll: {roll:.2f}°")

        # Wait 0.05 seconds, giving a target rate of about 20 readings per second.
        # This also prevents the loop from using the processor unnecessarily.
        time.sleep(0.05)
except KeyboardInterrupt:
    # Ctrl+C stops the infinite loop without displaying an error traceback.
    # This message confirms that the user, rather than a sensor error, stopped it.
    print("\nProgram stopped")
finally:
    # Always release the I2C bus, even if the program stops because of an error.
    # The finally block runs after normal stopping and after unexpected errors.
    bus.close()
