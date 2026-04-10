import time
from assignment2 import MPU6050   # change filename if needed

sensor = MPU6050(address=0x68, accel_range=2, gyro_range=250)#
sensor.setup()

while True:
    temp = sensor.read_temperature()
    ax, ay, az = sensor.read_accel()
    gx, gy, gz = sensor.read_gyro()

    print("new readings")
    print(f"temperature is {temp:.2f} Celsius")
    print(f"accelero : x : {ax:.2f}   y : {ay:.2f}   z : {az:.2f}")
    print(f"gyro : rot_x : {gx:.2f}°/s   rot_y : {gy:.2f}°/s   rot_z : {gz:.2f}°/s")
    print()

    time.sleep(1)