import smbus
import time

bus = smbus.SMBus(1)#enable i2c
MPU_ADDRESS = 0x68
bus.write_byte_data(MPU_ADDRESS, 0x6B, 0)#wake up

bus.write_byte_data(MPU_ADDRESS, 0x1C, 0)#accel range
bus.write_byte_data(MPU_ADDRESS, 0x1B, 0)#gyro range

def read_block():
    return bus.read_i2c_block_data(MPU_ADDRESS, 0x3B, 14)#read 14 bytes starting from 0x3B
def combine(high,low):#convert two bytes to one signed value
    value = (high<<8) | low#shift high byte 8 bits to the left and bitwise OR with low byte
    if value > 32768:#if value is greater than 32768, it is a negative number
        value -= 65536#subtract 2^16 to get the negative value
    return value

try:
    while True:
        data = read_block()#read 14 bytes starting from 0x3B
        print(data)#
        ax = combine(data[0],data[1])#convert first two bytes to one signed value
        ay = combine(data[2],data[3])#convert next two bytes to one signed value
        az = combine(data[4],data[5])#convert next two bytes to one signed value

    #temperature
    temp_raw = combine(data[6],data[7])#convert next two bytes to one signed value
    temp_c = (temp_raw / 340.0) + 36.53#convert raw temperature to degrees Celsius

    #gyroscope
    gx = combine(data[8],data[9])#convert next two bytes to one signed value
    gy = combine(data[10],data[11])#convert next two bytes to one signed value
    gz = combine(data[12],data[13])#convert next two bytes to one signed value

    accel_x_g = ax / 16384.0#convert raw acceleration to g
    accel_y_g = ay / 16384.0#convert raw acceleration to g
    accel_z_g = az / 16384.0#convert raw acceleration to g

    gyro_x_dps = gx / 131.0#convert raw gyroscope to degrees per second
    gyro_y_dps = gy / 131.0#convert raw gyroscope to degrees per second
    gyro_z_dps = gz / 131.0#convert raw gyroscope to degrees per second

    print("Accelerometer (g): ({:.3f}, {:.3f}, {:.3f})".format(accel_x_g, accel_y_g, accel_z_g))#print acceleration
    print("Gyroscope (°/s): ({:.3f}, {:.3f}, {:.3f})".format(gyro_x_dps, gyro_y_dps, gyro_z_dps))#print gyroscope
    print("Temperature: {:.2f} °C".format(temp_c))#print temperature

    time.sleep(0.5)#wait 0.5 seconds

except KeyboardInterrupt:
    print("Stopped by user")
finally:
    bus.close()
