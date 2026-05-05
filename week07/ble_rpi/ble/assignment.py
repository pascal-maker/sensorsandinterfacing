import time
import queue
import threading
import RPi.GPIO as GPIO

from bluetooth_uart_server import ble_gatt_uart_loop  # correct import — same folder

# ----------------------
# GPIO Setup
# ----------------------
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Stepper
STEPPER_PINS = (19, 13, 6, 5)
GPIO.setup(STEPPER_PINS, GPIO.OUT)

# DC motor
MOTOR_PIN1 = 14
MOTOR_PIN2 = 15
GPIO.setup(MOTOR_PIN1, GPIO.OUT)
GPIO.setup(MOTOR_PIN2, GPIO.OUT)

# Servo
SERVO_PIN = 18
GPIO.setup(SERVO_PIN, GPIO.OUT)

# PWM
dc_pwm1 = GPIO.PWM(MOTOR_PIN1, 1000)
dc_pwm2 = GPIO.PWM(MOTOR_PIN2, 1000)
dc_pwm1.start(0)
dc_pwm2.start(0)

servo_pwm = GPIO.PWM(SERVO_PIN, 50)
servo_pwm.start(0)

# ----------------------
# Variables
# ----------------------
OFF = 0
LEFT = 1
RIGHT = 2
dc_mode = OFF
step_index = 0

# ----------------------
# Steps
# ----------------------
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

# ----------------------
# BLE queues and thread
# ----------------------
rx_q = queue.Queue()
tx_q = queue.Queue()

threading.Thread(
    target=ble_gatt_uart_loop,
    args=(rx_q, tx_q, "pj-pi-gatt-uart"),
    daemon=True
).start()
