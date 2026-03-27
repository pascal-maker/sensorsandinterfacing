from RPi import GPIO
from time import sleep

# Use BCM numbering
GPIO.setmode(GPIO.BCM)

# 4 GPIO pins connected to the ULN2003 driver inputs
stepper_pin_1 = 19
stepper_pin_2 = 13
stepper_pin_3 = 6
stepper_pin_4 = 5

# Set all 4 pins as OUTPUT
GPIO.setup(stepper_pin_1, GPIO.OUT)
GPIO.setup(stepper_pin_2, GPIO.OUT)
GPIO.setup(stepper_pin_3, GPIO.OUT)
GPIO.setup(stepper_pin_4, GPIO.OUT)

# -----------------------------
# Step functions
# Each function sets one step pattern
# 1 = ON / HIGH
# 0 = OFF / LOW
# -----------------------------

def step1():
    GPIO.output(stepper_pin_1, 1)
    GPIO.output(stepper_pin_2, 0)
    GPIO.output(stepper_pin_3, 0)
    GPIO.output(stepper_pin_4, 0)

def step2():
    GPIO.output(stepper_pin_1, 1)
    GPIO.output(stepper_pin_2, 1)
    GPIO.output(stepper_pin_3, 0)
    GPIO.output(stepper_pin_4, 0)

def step3():
    GPIO.output(stepper_pin_1, 0)
    GPIO.output(stepper_pin_2, 1)
    GPIO.output(stepper_pin_3, 0)
    GPIO.output(stepper_pin_4, 0)

def step4():
    GPIO.output(stepper_pin_1, 0)
    GPIO.output(stepper_pin_2, 1)
    GPIO.output(stepper_pin_3, 1)
    GPIO.output(stepper_pin_4, 0)

def step5():
    GPIO.output(stepper_pin_1, 0)
    GPIO.output(stepper_pin_2, 0)
    GPIO.output(stepper_pin_3, 1)
    GPIO.output(stepper_pin_4, 0)

def step6():
    GPIO.output(stepper_pin_1, 0)
    GPIO.output(stepper_pin_2, 0)
    GPIO.output(stepper_pin_3, 1)
    GPIO.output(stepper_pin_4, 1)

def step7():
    GPIO.output(stepper_pin_1, 0)
    GPIO.output(stepper_pin_2, 0)
    GPIO.output(stepper_pin_3, 0)
    GPIO.output(stepper_pin_4, 1)

def step8():
    GPIO.output(stepper_pin_1, 1)
    GPIO.output(stepper_pin_2, 0)
    GPIO.output(stepper_pin_3, 0)
    GPIO.output(stepper_pin_4, 1)

# Function to turn everything off
def stop_motor():
    GPIO.output(stepper_pin_1, 0)
    GPIO.output(stepper_pin_2, 0)
    GPIO.output(stepper_pin_3, 0)
    GPIO.output(stepper_pin_4, 0)

try:
    print("Stepper motor starts turning clockwise...")

    # Repeat the 8-step sequence many times
    # 512 sequences is about 1 full output rotation for this geared motor
    for n in range(512):
        step1()
        sleep(0.001)

        step2()
        sleep(0.001)

        step3()
        sleep(0.001)

        step4()
        sleep(0.001)

        step5()
        sleep(0.001)

        step6()
        sleep(0.001)

        step7()
        sleep(0.001)

        step8()
        sleep(0.001)

    print("Now turning counterclockwise...")

    # Reverse the order to turn the other direction
    for n in range(512):
        step8()
        sleep(0.001)

        step7()
        sleep(0.001)

        step6()
        sleep(0.001)

        step5()
        sleep(0.001)

        step4()
        sleep(0.001)

        step3()
        sleep(0.001)

        step2()
        sleep(0.001)

        step1()
        sleep(0.001)

    print("Motor stopped.")
    stop_motor()

except KeyboardInterrupt:
    print("Program stopped by user.")
    stop_motor()

finally:
    GPIO.cleanup()