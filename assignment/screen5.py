import smbus
import time
import math

# LCD Settings
I2C_ADDR = 0x27  # address of the lcd
LCD_WIDTH = 16  # width of the lcd, 16 characters per line
LCD_CHR = 1  # character mode, send a normal character
LCD_CMD = 0  # command mode, send an lcd command
LCD_LINE_1 = 0x80  # first line of the lcd
LCD_LINE_2 = 0xC0  # second line of the lcd

ENABLE = 0b00000100  # enable pin to toggle the lcd so it reads data
RS = 0b00000001  # register select pin: 0 = command mode, 1 = character mode

# MPU settings
MPU_ADDR = 0x68  # address of the mpu
PWR_MGMT_1 = 0x6B  # power management register

ACCEL_XOUT_H = 0x3B  # start register for x accelerometer data
ACCEL_YOUT_H = 0x3D  # start register for y accelerometer data
ACCEL_ZOUT_H = 0x3F  # start register for z accelerometer data

ACCEL_SCALE = 16384.0  # scale factor to convert raw accelerometer data to g

# Open i2c bus
bus = smbus.SMBus(1)  # initialize the i2c bus


def lcd_toggle_enable(bits):
    # toggle the enable pin so the lcd reads the data
    time.sleep(0.0005)  # wait a tiny bit
    bus.write_byte(I2C_ADDR, bits | ENABLE)  # set enable high
    time.sleep(0.0005)  # wait a tiny bit
    bus.write_byte(I2C_ADDR, bits & ~ENABLE)  # set enable low
    time.sleep(0.0005)  # wait a tiny bit


def lcd_send_byte(bits, mode):
    # send a byte to the lcd in 4-bit mode
    high_bits = mode | (bits & 0xF0) | 0x08  # upper 4 bits
    low_bits = mode | ((bits << 4) & 0xF0) | 0x08  # lower 4 bits shifted left

    bus.write_byte(I2C_ADDR, high_bits)  # send the upper 4 bits
    lcd_toggle_enable(high_bits)  # toggle enable

    bus.write_byte(I2C_ADDR, low_bits)  # send the lower 4 bits
    lcd_toggle_enable(low_bits)  # toggle enable


def lcd_init():
    # initialize the lcd: set 4-bit mode, turn display on, set 2 lines, clear display
    lcd_send_byte(0x33, LCD_CMD)  # function set 8-bit mode
    lcd_send_byte(0x32, LCD_CMD)  # switch to 4-bit mode
    lcd_send_byte(0x06, LCD_CMD)  # entry mode set: increment cursor
    lcd_send_byte(0x0C, LCD_CMD)  # display on, cursor off, blink off
    lcd_send_byte(0x28, LCD_CMD)  # function set: 4-bit mode, 2 lines, 5x8 dots
    lcd_send_byte(0x01, LCD_CMD)  # clear the lcd
    time.sleep(0.0005)


def lcd_string(message, line):
    # make sure the message is 16 characters long
    message = message.ljust(LCD_WIDTH, " ")
    lcd_send_byte(line, LCD_CMD)  # send the line address to the lcd

    # send each character to the lcd
    for ch in message[:LCD_WIDTH]:
        lcd_send_byte(ord(ch), LCD_CHR)


def lcd_clear():
    # clear the lcd
    lcd_send_byte(0x01, LCD_CMD)
    time.sleep(0.0005)


# MPU functions
def mpu_init():
    # initialize the mpu: set the power management register to 0 to wake it up
    bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0)
    time.sleep(0.0005)


def read_word_2c(addr):
    # read a 16-bit signed value from the mpu
    high = bus.read_byte_data(MPU_ADDR, addr)  # read the high byte
    low = bus.read_byte_data(MPU_ADDR, addr + 1)  # read the low byte

    val = (high << 8) | low  # combine the two bytes into one 16-bit value

    if val >= 0x8000:
        # convert to signed value using two's complement
        val = val - 65536

    return val


def read_accel_g():
    # read the accelerometer data and convert it to g
    raw_x = read_word_2c(ACCEL_XOUT_H)  # read x-axis data
    raw_y = read_word_2c(ACCEL_YOUT_H)  # read y-axis data
    raw_z = read_word_2c(ACCEL_ZOUT_H)  # read z-axis data

    x_g = raw_x / ACCEL_SCALE  # convert x-axis raw value to g
    y_g = raw_y / ACCEL_SCALE  # convert y-axis raw value to g
    z_g = raw_z / ACCEL_SCALE  # convert z-axis raw value to g

    return x_g, y_g, z_g


def calculate_combined_g(x_g, y_g, z_g):
    # calculate total acceleration magnitude
    return math.sqrt(x_g**2 + y_g**2 + z_g**2)


def make_lines(x, y, z, c):
    # format the lcd lines
    # line 1: x on the left, y on the right
    # line 2: z on the left, combined g on the right
    # use 2 decimals

    left1 = f"X:{x:.2f}"  # format x value
    right1 = f"Y:{y:.2f}"  # format y value

    left2 = f"Z:{z:.2f}"  # format z value
    right2 = f"C:{c:.2f}"  # format combined g value

    line1 = left1.ljust(8) + right1.rjust(8)  # x left, y right
    line2 = left2.ljust(8) + right2.rjust(8)  # z left, c right

    return line1, line2


def main():
    try:
        lcd_init()
        mpu_init()

        while True:
            x, y, z = read_accel_g()  # read the accelerometer data
            combined_g = calculate_combined_g(x, y, z)  # calculate the combined g value

            line1, line2 = make_lines(x, y, z, combined_g)  # format the lcd lines

            lcd_string(line1, LCD_LINE_1)  # display the first line
            lcd_string(line2, LCD_LINE_2)  # display the second line

            time.sleep(0.1)  # small delay

    except KeyboardInterrupt:
        lcd_clear()
        print("Exiting...")


if __name__ == "__main__":
    main()