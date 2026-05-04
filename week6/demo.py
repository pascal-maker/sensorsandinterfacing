import smbus
import time
import math

bus = smbus.SMBus(1)#enable i2c
addr = 0x68#mpu6050 address

bus.write_byte_data(addr, 0x6B, 0)#wake up

def combine(h, l):#convert two bytes to one signed value combining the high and low bytes to get the full 16 bit value
    val = (h << 8) | l#shift high byte left by 8 and bitwise OR with low byte
    if val > 32767:#if value is greater than 32767, it is a negative number sensors uses neftaive values for opposite directions
        val -= 65536#subtract 2^16 to get the negative value
    return val

pitch = 0#pitch angle means tilting forwards and backwards
roll = 0#roll angle means tilting side to side
prev_time = time.time()#previous time 

while True:#loop forever
    data = bus.read_i2c_block_data(addr, 0x3B, 14)#read 14 bytes starting from 0x3B reading 14 bytes at once grabs all sensorr data in one shot reducing delay and error    

    acc_x = combine(data[0], data[1]) / 16384#convert raw acceleration to g how much force the sensor feels relative to gravity in each direction  dividing by 16834 convers the raw number into a scale of -1 to 1 
    acc_y = combine(data[2], data[3]) / 16384#convert raw acceleration to g how much force the sensor feels relative to gravity in each direction 
    acc_z = combine(data[4], data[5]) / 16384#convert raw acceleration to g how much force the sensor feels relative to gravity in each direction 

    gyro_x = combine(data[8], data[9]) / 131#convert raw gyroscope to degrees per second how fast the sensor is rotating
    gyro_y = combine(data[10], data[11]) / 131#convert raw gyroscope to degrees per second how fast the sensor is rotating dividing by 131 converts the raw number into a scale of -250 to 250 degrees per second 

    # time difference
    curr_time = time.time()#get current time
    dt = curr_time - prev_time#calculate time difference
    prev_time = curr_time#update previous time

    # accelerometer angles
    pitch_acc = math.atan2(acc_x, math.sqrt(acc_y**2 + acc_z**2)) * 180 / math.pi#calculate pitch angle using accelerometer using an angle from two numbers and convert it to degrees  and asko combines the other two axes into one value  divdided by 180 convertng radian to degrees
    roll_acc  = math.atan2(acc_y, math.sqrt(acc_x**2 + acc_z**2)) * 180 / math.pi#calculate roll angle using accelerometer and convertng radian to degrees

    # complementary filter
    alpha = 0.98#98% gyro, 2% accelerometer
    pitch = alpha * (pitch + gyro_x * dt) + (1 - alpha) * pitch_acc#98% gyro update + 2% accel correction
    roll  = alpha * (roll  + gyro_y * dt) + (1 - alpha) * roll_acc#98% gyro update + 2% accel correction

    print(f"Pitch: {pitch:.2f}°, Roll: {roll:.2f}°")#print pitch and roll

    time.sleep(0.05)