from RPi import GPIO
from time import sleep

# Use BCM pin numbering
GPIO.setmode(GPIO.BCM)

# 4 GPIO pins connected to IN1, IN2, IN3, IN4 of the ULN2003
stepper_pin_1 = 19
stepper_pin_2 = 13
stepper_pin_3 = 6
stepper_pin_4 = 5

# Set the 4 pins as outputs
GPIO.setup(stepper_pin_1, GPIO.OUT)
GPIO.setup(stepper_pin_2, GPIO.OUT)
GPIO.setup(stepper_pin_3, GPIO.OUT)
GPIO.setup(stepper_pin_4, GPIO.OUT)

# Step 1: only coil 1 ON
def step1():
    GPIO.output(stepper_pin_1, 1)
    GPIO.output(stepper_pin_2, 0)
    GPIO.output(stepper_pin_3, 0)
    GPIO.output(stepper_pin_4, 0)

# Step 2: coil 1 and coil 2 ON
def step2():
    GPIO.output(stepper_pin_1, 1)
    GPIO.output(stepper_pin_2, 1)
    GPIO.output(stepper_pin_3, 0)
    GPIO.output(stepper_pin_4, 0)

# Step 3: only coil 2 ON
def step3():
    GPIO.output(stepper_pin_1, 0)
    GPIO.output(stepper_pin_2, 1)
    GPIO.output(stepper_pin_3, 0)
    GPIO.output(stepper_pin_4, 0)

# Step 4: coil 2 and coil 3 ON
def step4():
    GPIO.output(stepper_pin_1, 0)
    GPIO.output(stepper_pin_2, 1)
    GPIO.output(stepper_pin_3, 1)
    GPIO.output(stepper_pin_4, 0)

# Step 5: only coil 3 ON
def step5():
    GPIO.output(stepper_pin_1, 0)
    GPIO.output(stepper_pin_2, 0)
    GPIO.output(stepper_pin_3, 1)
    GPIO.output(stepper_pin_4, 0)

# Step 6: coil 3 and coil 4 ON
def step6():
    GPIO.output(stepper_pin_1, 0)
    GPIO.output(stepper_pin_2, 0)
    GPIO.output(stepper_pin_3, 1)
    GPIO.output(stepper_pin_4, 1)

# Step 7: only coil 4 ON
def step7():
    GPIO.output(stepper_pin_1, 0)
    GPIO.output(stepper_pin_2, 0)
    GPIO.output(stepper_pin_3, 0)
    GPIO.output(stepper_pin_4, 1)

# Step 8: coil 4 and coil 1 ON
def step8():
    GPIO.output(stepper_pin_1, 1)
    GPIO.output(stepper_pin_2, 0)
    GPIO.output(stepper_pin_3, 0)
    GPIO.output(stepper_pin_4, 1)

# Turn all coils off
def stop_motor():
    GPIO.output(stepper_pin_1, 0)
    GPIO.output(stepper_pin_2, 0)
    GPIO.output(stepper_pin_3, 0)
    GPIO.output(stepper_pin_4, 0)

try:
    print("Clockwise")
    for _ in range(512):
        step1(); sleep(0.001)
        step2(); sleep(0.001)
        step3(); sleep(0.001)
        step4(); sleep(0.001)
        step5(); sleep(0.001)
        step6(); sleep(0.001)
        step7(); sleep(0.001)
        step8(); sleep(0.001)

    print("Counterclockwise")
    for _ in range(512):
        step8(); sleep(0.001)
        step7(); sleep(0.001)
        step6(); sleep(0.001)
        step5(); sleep(0.001)
        step4(); sleep(0.001)
        step3(); sleep(0.001)
        step2(); sleep(0.001)
        step1(); sleep(0.001)

    stop_motor()

except KeyboardInterrupt:
    stop_motor()

finally:
    GPIO.cleanup()