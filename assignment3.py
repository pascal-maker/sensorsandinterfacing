from mpu6050 import MPU6050
import RPi.GPIO as GPIO
import time

BUZZER_PIN = 12

# smaller = more sensitive
ACCEL_THRESHOLD = 0.20
GYRO_THRESHOLD = 20.0

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

mpu = MPU6050(0x68, accel_range=2, gyro_range=250)
mpu.setup()

prev_ax, prev_ay, prev_az = mpu.get_acceleration()

try:
    while True:
        ax, ay, az = mpu.get_acceleration()
        gx, gy, gz = mpu.get_gyroscope()

        accel_change = abs(ax - prev_ax) + abs(ay - prev_ay) + abs(az - prev_az)
        gyro_movement = abs(gx) + abs(gy) + abs(gz)

        if accel_change > ACCEL_THRESHOLD or gyro_movement > GYRO_THRESHOLD:
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            print("Movement detected -> buzzer ON")
        else:
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            print("No important movement -> buzzer OFF")

        prev_ax, prev_ay, prev_az = ax, ay, az
        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    GPIO.cleanup()