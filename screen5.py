import smbus
import time
import math 

#LCD Settings

I2C_ADDR = 0x27#address of the lcd
LCD_WIDTH = 16#width of the lcd 16 characters per line
LCD_CHR = 1#character mode send a normal character
LCD_CMD = 0#command mode send a lcd command
LCD_LINE_1 = 0x80#first line of the lcd
LCD_LINE_2 = 0xC0#second line of the lcd

ENABLE = 0b00000100#enable pin to toggle the enable pin the lcd so it reads data
RS = 0b00000001#register select pin 0 command mode 1 character mode
#MPU settings
MPU_ADDR = 0x68#address of the mpu
PWR_MGMT_1 = 0x6B#power management register

ACCEL_XOUT_H = 0x3B#start register for the accelerometer data

ACCEL_YOUT_H = 0x3D#start register for the accelerometer data

ACCEL_ZOUT_H = 0x3F#start register for the accelerometer data

ACCEL_SCALE = 16384.0#scale factor for the accelerometer to convert raw data to g's
#open i2c bus
bus = smbus.SMBus(1)#initialize the i2c bus

def lcd_toggle_enable(bits):#toggle the enable pin so the lcd reads the data
    time.sleep(0.0005)#wait a tiny bit
    bus.write_byte(I2C_ADDR, bits | ENABLE)#set enable high
    time.sleep(0.0005)#wait a tiny bit
    bus.write_byte(I2C_ADDR, bits & ~ENABLE)#set enable low
    time.sleep(0.0005)#wait a tiny bit

def lcd_send_byte(bits, mode):#send a byte to the lcd
    high_bits = mode | (bits & 0xF0) | 0x08#split the byte into two nibbles
    low_bits = mode | ((bits << 4) & 0xF0) | 0x08#split the byte into two nibbles
    i2cbus.write_byte(I2C_ADDR, high_bits)#send the upper 4 bits of the byte
    lcd_toggle_enable(high_bits)#toggle the enable pin
    bus.write_byte(I2C_ADDR, low_bits)#send the lower 4 bits of the byte
    lcd_toggle_enable(low_bits)#toggle the enable pin

def lcd_init():#initialize the lcd set 4 bit mode turn display on set 2 lines clear the display
    lcd_send_byte(0x33, LCD_CMD)#function set 8 bit mode
    lcd_send_byte(0x32, LCD_CMD)#function set 8 bit mode
    lcd_send_byte(0x06, LCD_CMD)#entry mode set increment cursor
    lcd_send_byte(0x0C, LCD_CMD)#display on cursor off blink off
    lcd_send_byte(0x28, LCD_CMD)#function set 4 bit mode 2 lines 5x8 dots
    lcd_send_byte(0x01, LCD_CMD)#clear the lcd
    time.sleep(0.0005)    

def lcd_string(message, line):#make sure the message is 16 characters long
    message = message.ljust(LCD_WIDTH, " ")# make sure the message is 16 characters long
    lcd_send_byte(line, LCD_CMD)#send the line to the lcd
    for ch in message[:LCD_WIDTH]:#iterate through the message and send each character to the lcd
        lcd_send_byte(ord(ch), LD_CHR)#send the character to the lcd

def lcd_clear():#clear the lcd
    lcd_send_byte(0x01, LCD_CMD)#clear the lcd
    time.sleep(0.0005)    
#mpu functions
def mpu_init():#initialize the mpu set the power management register to 0 to wake it up
    bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0)#wake up the mpu
    time.sleep(0.0005)#wait a tiny bit
#read one signed 16bit value
def read_word_2c(addr):#read a 16 bit signed value from the mpu
    high = bus.read_byte_data(MPU_ADDR, addr)#read the high byte
    low = bus.read_byte_data(MPU_ADDR, addr + 1)#read the low byte
    val = (high << 8) | low#combine the two bytes in python into one 16 bit number  
    if val >= 0x8000:#if the value is negative
        val =  val - 65536#convert to signed valye using two complement
    return val#return the value

def read_accel_g():#read the accelerometer data and convert it to g's
    raw_x = read_word_2c(ACCEL_XOUT_H)#read the x-axis accelerometer data
    raw_y = read_word_2c(ACCEL_YOUT_H)#read the y-axis accelerometer data
    raw_z = read_word_2c(ACCEL_ZOUT_H)#read the z-axis accelerometer data
    x_g = raw_x / ACCEL_SCALE#convert the x-axis accelerometer data to g's
    y_g = raw_y / ACCEL_SCALE#convert the y-axis accelerometer data to g's
    z_g = raw_z / ACCEL_SCALE#convert the z-axis accelerometer data to g's
    return x_g, y_g, z_g#return the accelerometer data in g's
 
#calculate combined value total acceletation magnitude
def calculate_combined_g(x_g, y_g, z_g):#calculate the combined g value
    return math.sqrt(x_g**2 + y_g**2 + z_g**2)#return the combined g value
    #sqrt(x^2 + y^2 + z^2)

 #format lcd lines the assigment says to display the values on the lcd line 1 x on the left and y on the right  and line 2 z on the left and combined g on the right  and it uses 2 decinals left/right alignmement

def make_lines(x,y,z,c):#format the lcd lines
    left1 = f"X:{x:.2f}"#format the x value to be displayed on the lcd
    right1 = f"Y:{y:.2f}"#format the y value to be displayed on the lcd
    left2 = f"Z:{z:.2f}"#format the z value to be displayed on the lcd
    right2 = f"C:{c:.2f}"#format the combined g value to be displayed on the lcd
    
    line1 = left1.ljust(8) + right1.rjust(8)#
    line2 = left2.ljust(8) + right2.rjust(8)#
    
    return line1, line2
    
#main loop

def main():
    try:
        lcd_init()
        mpu_init()
        while True:
            x, y, z = read_accel_g()
            combined_g = calculate_combined_g(x, y, z)
            line1, line2 = make_lines(x, y, z, combined_g)
            lcd_string(line1, LCD_LINE_1)
            lcd_string(line2, LCD_LINE_2)
            time.sleep(0.1)
    except KeyboardInterrupt:
        lcd_clear()
        print("Exiting...")

if __name__ == "__main__":
    main()