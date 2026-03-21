from mpu6050 import MPU6050
import time

mpu = MPU6050(0x68, accel_range=2, gyro_range=250)
mpu.setup()
while True:
    temp = mpu.get_temperature()
    ax,ay,az = mpu.get_acceleration()
    gx,gy,gz = mpu.get_gyroscope()
    print("new reading:")
    print(f"Temperature: {temp:.2f} °C")
    print(f"Acceleration (g): X={ax:.2f}, Y={ay:.2f}, Z={az:.2f}")
    print(f"Gyroscope (°/s): X={gx:.2f}, Y={gy:.2f}, Z={gz:.2f}")
    time.sleep(1)