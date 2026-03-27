from RPi import GPIO
from time import sleep
import threading

GPIO.setmode(GPIO.BCM)

# -------------------------
# Buttons
# -------------------------
BTN_STEPPER_LEFT = 20
BTN_STEPPER_RIGHT = 21
BTN_DC_TOGGLE = 16
BTN_SERVO_TOGGLE = 26

GPIO.setup(BTN_STEPPER_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_STEPPER_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_DC_TOGGLE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_SERVO_TOGGLE, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# -------------------------
# Stepper motor
# -------------------------
stepper_pins = (19, 13, 6, 5)
GPIO.setup(stepper_pins, GPIO.OUT)

steps = (
    (1, 0, 0, 0),
    (1, 1, 0, 0),
    (0, 1, 0, 0),
    (0, 1, 1, 0),
    (0, 0, 1, 0),
    (0, 0, 1, 1),
    (0, 0, 0, 1),
    (1, 0, 0, 1),
)

stepper_direction = 0
# -1 = left, 0 = stop, 1 = right

def apply_step(step):
    for i in range(4):
        GPIO.output(stepper_pins[i], step[i])

def stop_stepper():
    for pin in stepper_pins:
        GPIO.output(pin, 0)

def stepper_worker():
    global stepper_direction
    while True:
        if stepper_direction == -1:
            for step in steps:
                if stepper_direction != -1:
                    break
                apply_step(step)
                sleep(0.001)

        elif stepper_direction == 1:
            for step in reversed(steps):
                if stepper_direction != 1:
                    break
                apply_step(step)
                sleep(0.001)

        else:
            stop_stepper()
            sleep(0.01)

# -------------------------
# DC motor
# -------------------------
DC_PIN_1 = 14
DC_PIN_2 = 15
GPIO.setup(DC_PIN_1, GPIO.OUT)
GPIO.setup(DC_PIN_2, GPIO.OUT)

dc_pwm_1 = GPIO.PWM(DC_PIN_1, 1000)
dc_pwm_2 = GPIO.PWM(DC_PIN_2, 1000)
dc_pwm_1.start(0)
dc_pwm_2.start(0)

dc_state = 0
# 0=OFF, 1=LEFT, 2=RIGHT

# -------------------------
# Servo motor
# -------------------------
SERVO_PIN = 18
GPIO.setup(SERVO_PIN, GPIO.OUT)

servo_pwm = GPIO.PWM(SERVO_PIN, 50)
servo_pwm.start(0)
servo_enabled = False

# -------------------------
# ADC helper
# Replace this later
# -------------------------
def read_adc(channel):
    return 128

def map_adc_to_percent(value):
    return int((value / 255) * 100)

def adc_to_angle(adc_value):
    return int((adc_value / 255) * 180)

def angle_to_duty(angle):
    return 2 + (angle / 18)

# -------------------------
# Button callbacks
# -------------------------
def dc_toggle(channel):
    global dc_state
    dc_state = (dc_state + 1) % 3

def servo_toggle(channel):
    global servo_enabled
    servo_enabled = not servo_enabled

GPIO.add_event_detect(BTN_DC_TOGGLE, GPIO.FALLING, callback=dc_toggle, bouncetime=250)
GPIO.add_event_detect(BTN_SERVO_TOGGLE, GPIO.FALLING, callback=servo_toggle, bouncetime=250)

# -------------------------
# Start stepper thread
# -------------------------
threading.Thread(target=stepper_worker, daemon=True).start()

# -------------------------
# Main loop
# -------------------------
prev_left = GPIO.input(BTN_STEPPER_LEFT)
prev_right = GPIO.input(BTN_STEPPER_RIGHT)

try:
    while True:
        # -----------------
        # Held buttons for stepper
        # -----------------
        current_left = GPIO.input(BTN_STEPPER_LEFT)
        current_right = GPIO.input(BTN_STEPPER_RIGHT)

        if current_left == GPIO.LOW:
            stepper_direction = -1
        elif current_right == GPIO.LOW:
            stepper_direction = 1
        else:
            stepper_direction = 0

        prev_left = current_left
        prev_right = current_right

        # -----------------
        # Potentiometer controls DC speed
        # -----------------
        pot_raw = read_adc(0)   # change channel if needed
        dc_speed = map_adc_to_percent(pot_raw)

        if dc_state == 0:
            dc_pwm_1.ChangeDutyCycle(0)
            dc_pwm_2.ChangeDutyCycle(0)
            print(f"DC OFF | speed={dc_speed}%")

        elif dc_state == 1:
            dc_pwm_1.ChangeDutyCycle(dc_speed)
            dc_pwm_2.ChangeDutyCycle(0)
            print(f"DC LEFT | speed={dc_speed}%")

        elif dc_state == 2:
            dc_pwm_1.ChangeDutyCycle(0)
            dc_pwm_2.ChangeDutyCycle(dc_speed)
            print(f"DC RIGHT | speed={dc_speed}%")

        # -----------------
        # Servo from joystick X channel 6
        # -----------------
        if servo_enabled:
            x_raw = read_adc(6)
            angle = adc_to_angle(x_raw)
            duty = angle_to_duty(angle)
            servo_pwm.ChangeDutyCycle(duty)
            print(f"SERVO ON | raw={x_raw} angle={angle}")
        else:
            servo_pwm.ChangeDutyCycle(0)
            print("SERVO OFF")

        sleep(0.1)

except KeyboardInterrupt:
    print("Stopping...")

finally:
    stop_stepper()

    dc_pwm_1.ChangeDutyCycle(0)
    dc_pwm_2.ChangeDutyCycle(0)
    dc_pwm_1.stop()
    dc_pwm_2.stop()
    dc_pwm_1 = None
    dc_pwm_2 = None

    servo_pwm.ChangeDutyCycle(0)
    servo_pwm.stop()
    servo_pwm = None

    GPIO.cleanup()