import smbus
import time
import math
import threading

# LCD Settings
I2C_ADDR = 0x27#address of the lcd
LCD_WIDTH = 16#width of the lcd 16 characters per line
LCD_CHR = 1#character mode send a normal character
LCD_CMD = 0#command mode send an lcd command

LCD_LINE_1 = 0x80#first line of the lcd
LCD_LINE_2 = 0xC0#second line of the lcd

ENABLE = 0b00000100#enable pin to toggle the lcd so it reads data

# MPU settings
MPU_ADDR = 0x68#address of the mpu
PWR_MGMT_1 = 0x6B#power management register

ACCEL_XOUT_H = 0x3B#start register for x accelerometer data
ACCEL_YOUT_H = 0x3D#start register for y accelerometer data
ACCEL_ZOUT_H = 0x3F#start register for z accelerometer data

ACCEL_SCALE = 16384.0#scale factor to convert raw accelerometer data to g

bus = smbus.SMBus(1)#initialize the i2c bus


def lcd_toggle_enable(bits):#toggle the enable pin so the lcd reads the data
    time.sleep(0.0005)#wait a tiny bit
    bus.write_byte(I2C_ADDR, bits | ENABLE)#set enable high
    time.sleep(0.0005)#wait a tiny bit
    bus.write_byte(I2C_ADDR, bits & ~ENABLE)#set enable low
    time.sleep(0.0005)#wait a tiny bit


def lcd_send_byte(bits, mode):#send a byte to the lcd in 4-bit mode
    high_bits = mode | (bits & 0xF0) | 0x08#upper 4 bits
    low_bits = mode | ((bits << 4) & 0xF0) | 0x08#lower 4 bits shifted left

    bus.write_byte(I2C_ADDR, high_bits)#send the upper 4 bits
    lcd_toggle_enable(high_bits)#toggle enable

    bus.write_byte(I2C_ADDR, low_bits)#send the lower 4 bits
    lcd_toggle_enable(low_bits)#toggle enable


def lcd_init():#initialize the lcd
    lcd_send_byte(0x33, LCD_CMD)#function set 8-bit mode
    lcd_send_byte(0x32, LCD_CMD)#switch to 4-bit mode
    lcd_send_byte(0x06, LCD_CMD)#entry mode set increment cursor
    lcd_send_byte(0x0C, LCD_CMD)#display on cursor off blink off
    lcd_send_byte(0x28, LCD_CMD)#function set 4-bit mode 2 lines 5x8 dots
    lcd_send_byte(0x01, LCD_CMD)#clear the lcd
    time.sleep(0.002)#wait a tiny bit


def lcd_string(message, line):#make sure the message is 16 characters long
    message = message.ljust(LCD_WIDTH, " ")#pad the message with spaces to the width of the lcd
    lcd_send_byte(line, LCD_CMD)#send the line address to the lcd

    for ch in message[:LCD_WIDTH]:#send each character to the lcd
        lcd_send_byte(ord(ch), LCD_CHR)#send the character


def lcd_clear():#clear the lcd
    lcd_send_byte(0x01, LCD_CMD)#send the clear display command
    time.sleep(0.002)


def mpu_init():#initialize the mpu
    bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0)#set the power management register to 0 to wake it up
    time.sleep(0.002)


def read_word_2c(addr):#read a 16-bit signed value from the mpu
    high = bus.read_byte_data(MPU_ADDR, addr)#read the high byte from the mpu
    low = bus.read_byte_data(MPU_ADDR, addr + 1)#read the low byte from the mpu

    val = (high << 8) | low#combine the high and low bytes into a 16-bit value

    if val >= 0x8000:#if the value is negative
        val = val - 65536

    return val


def read_accel_g():#read the accelerometer data in g
    raw_x = read_word_2c(ACCEL_XOUT_H)#read the x accelerometer data
    raw_y = read_word_2c(ACCEL_YOUT_H)#read the y accelerometer data
    raw_z = read_word_2c(ACCEL_ZOUT_H)#read the z accelerometer data

    x_g = raw_x / ACCEL_SCALE#convert the x accelerometer data to g
    y_g = raw_y / ACCEL_SCALE#convert the y accelerometer data to g
    z_g = raw_z / ACCEL_SCALE#convert the z accelerometer data to g

    return x_g, y_g, z_g#return the accelerometer data


def calculate_combined_g(x_g, y_g, z_g):#calculate the combined g force
    return math.sqrt(x_g**2 + y_g**2 + z_g**2)#calculate the combined g force


def make_lines(x, y, z, c):#make the lines to be displayed on the lcd
    left1 = f"X:{x:.2f}"#format the x accelerometer data
    right1 = f"Y:{y:.2f}"#format the y accelerometer data

    left2 = f"Z:{z:.2f}"#format the z accelerometer data
    right2 = f"C:{c:.2f}"#format the combined g force

    line1 = left1.ljust(8) + right1.rjust(8)#format the first line with x and y accelerometer data
    line2 = left2.ljust(8) + right2.rjust(8)#format the second line with z and combined g force

    return line1, line2#return the formatted lines


def wait_or_stop(stop_event, seconds):
    steps = int(seconds / 0.1)#calculate the number of steps

    for _ in range(steps):
        if stop_event.is_set():#if the stop event is set return
            return
        time.sleep(0.1)


def run(stop_event):#run the screen
    lcd_init()#initialize the lcd
    mpu_init()#initialize the mpu

    while not stop_event.is_set():#run the screen until the stop event is set
        x, y, z = read_accel_g()#read the accelerometer data in g
        combined_g = calculate_combined_g(x, y, z)#calculate the combined g force

        line1, line2 = make_lines(x, y, z, combined_g)#make the lines to be displayed on the lcd

        lcd_string(line1, LCD_LINE_1)#send the first line to the lcd
        lcd_string(line2, LCD_LINE_2)#send the second line to the lcd

        wait_or_stop(stop_event, 0.1)#wait a tiny bit before checking again

    lcd_clear()#clear the lcd


if __name__ == "__main__":#this is the main part of the program that will run when the file is executed
    stop_event = threading.Event()#create a stop event to stop the screen

    try:
        run(stop_event)#run the screen
    except KeyboardInterrupt:#if the user presses ctrl+c
        stop_event.set()
        lcd_clear()#clear the lcd