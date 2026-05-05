from RPi import GPIO
from time import sleep
import threading

GPIO.setmode(GPIO.BCM)#

BTN_LEFT = 20
stepper_pins = (19, 13, 6, 5)#

GPIO.setup(BTN_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(stepper_pins, GPIO.OUT)#

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

stepper_left_active = False

def apply_step(step):
    for i in range(4):
        GPIO.output(stepper_pins[i], step[i])

def stop_stepper():
    for pin in stepper_pins:
        GPIO.output(pin, 0)

def stepper_worker():
    global stepper_left_active
    while True:
        if stepper_left_active:
            for step in steps:
                if not stepper_left_active:
                    break
                apply_step(step)
                sleep(0.001)
        else:
            stop_stepper()
            sleep(0.01)

def btn_left_pressed(channel):
    global stepper_left_active
    stepper_left_active = True

def btn_left_released(channel):
    global stepper_left_active
    stepper_left_active = False

GPIO.add_event_detect(BTN_LEFT, GPIO.BOTH, bouncetime=50)

threading.Thread(target=stepper_worker, daemon=True).start()

previous_state = GPIO.input(BTN_LEFT)

try:
    while True:
        current_state = GPIO.input(BTN_LEFT)

        if previous_state == GPIO.HIGH and current_state == GPIO.LOW:
            btn_left_pressed(BTN_LEFT)

        elif previous_state == GPIO.LOW and current_state == GPIO.HIGH:
            btn_left_released(BTN_LEFT)

        previous_state = current_state
        sleep(0.01)

except KeyboardInterrupt:
    stop_stepper()
    GPIO.cleanup()