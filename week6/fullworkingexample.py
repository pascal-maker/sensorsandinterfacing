import smbus
import time
import math
bus = smbus.SMBus(1)
MPU_ADDRESS = 0x68
bus.write_byte_data(MPU_ADDRESS, 0x6B, 0)#wake up

def combine(high,low):#high byte first then low byte
    value = (high<<8) | low#shift high byte to the left by 8 bits and then OR it with the low byte
    if value > 32768:#if the value is greater than 32768, then it is a negative number
        value -= 65536#subtract 65536 from the value to get the correct value
    return value#return the combined value

pitch = 0#pitch angle
roll = 0#roll angle
previous_time = time.time()
while True:#loop forever
    current_time = time.time()#get current time
    dt = current_time - previous_time#calculate time difference
    previous_time = current_time#update previous time
    
    data = bus.read_i2c_block_data(MPU_ADDRESS, 0x3B, 14)#read 14 bytes starting from 0x3B
    ax = combine(data[0],data[1])#convert first two bytes to one signed value
    ay = combine(data[2],data[3])#convert next two bytes to one signed value
    az = combine(data[4],data[5])#convert next two bytes to one signed value
    gx = combine(data[8],data[9])#convert next two bytes to one signed value
    gy = combine(data[10],data[11])#convert next two bytes to one signed value
    gz = combine(data[12],data[13])#convert next two bytes to one signed value

    #accelerometer angles
    angle_x = math.atan2(ay, az) * 180 / math.pi#calculate angle x
    angle_y = math.atan2(-ax, math.sqrt(ay * ay + az * az)) * 180 / math.pi#calculate angle y

    #complementary filter: mix gyro (fast, drifts) with accelerometer (slow, stable)
    alpha = 0.98#98% gyro, 2% accelerometer
    pitch = alpha * (pitch + gx * dt) + (1 - alpha) * angle_x#98% gyro update + 2% accel correction
    roll = alpha * (roll + gy * dt) + (1 - alpha) * angle_y#98% gyro update + 2% accel correction
    
    print(f"Pitch: {pitch:.2f} degrees, Roll: {roll:.2f} degrees")#print pitch and roll
    time.sleep(0.1)#wait 0.1 seconds
  - #The gyroscope tracks rotation fast and smoothly, but slowly drifts off over time                            
  - #The accelerometer always knows the true angle (using gravity), but is jittery                               
  - #alpha = 0.98 means: trust the gyro 98% each update, but let the accelerometer fix the drift 2%              
  - #gx * dt = how many degrees the gyro says you rotated since the last loop                                    
  - #The result is smooth and accurate