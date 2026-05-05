import time
import queue
import threading
import RPi.GPIO as GPIO

from ble.bluetooth_uart_server import ble_gatt_uart_loop, stop_ble_gatt_uart_loop

# ----------------------
# GPIO Setup
# ----------------------
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# DC Motor
MOTOR_PINS = (14, 15)
GPIO.setup(MOTOR_PINS, GPIO.OUT)

# Servo
SERVO_PIN = 18
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Stepper
STEPPER_PINS = (19, 13, 6, 5)
GPIO.setup(STEPPER_PINS, GPIO.OUT)

# PWM
dc_pwm1 = GPIO.PWM(14, 1000)  # fixed: was motor_pin1 (undefined), 1000Hz not 100Hz
dc_pwm2 = GPIO.PWM(15, 1000)  # fixed: was motor_pin2 (undefined), 1000Hz not 100Hz
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

# ----------------------
# Stepper functions
# ----------------------
def stop_stepper():
    for pin in STEPPER_PINS:
        GPIO.output(pin, 0)

def stepper_half_turn(direction):
    global step_index
    for _ in range(2048):
        step_index = (step_index + direction) % 8
        for i, pin in enumerate(STEPPER_PINS):
            GPIO.output(pin, steps[step_index][i])
        time.sleep(0.002)
    stop_stepper()

def degrees_to_steps(degrees):
    return int(abs(degrees) / 360 * 4096)  # 512 cycles × 8 half-steps = 4096

def stepper_turn_steps(num_steps, direction):
    global step_index
    for _ in range(num_steps):
        step_index = (step_index + direction) % 8
        for i, pin in enumerate(STEPPER_PINS):
            GPIO.output(pin, steps[step_index][i])
        time.sleep(0.002)
    stop_stepper()

# ----------------------
# DC motor functions
# ----------------------
def dc_left(speed):
    dc_pwm1.ChangeDutyCycle(speed)
    dc_pwm2.ChangeDutyCycle(0)

def dc_right(speed):
    dc_pwm1.ChangeDutyCycle(0)
    dc_pwm2.ChangeDutyCycle(speed)

def dc_stop():
    dc_pwm1.ChangeDutyCycle(0)
    dc_pwm2.ChangeDutyCycle(0)

# ----------------------
# Servo functions
# ----------------------
def servo_set_angle(angle):
    angle = max(0, min(180, angle))
    duty = angle / 18 + 2
    servo_pwm.ChangeDutyCycle(duty)

# ----------------------
# Main loop
# ----------------------
try:
    while True:
        try:
            cmd = rx_q.get(timeout=0.01)
            cmd_lower = cmd.strip().lower()

            if cmd_lower == "dc-left":
                dc_left(60)
                tx_q.put("DC turning left")

            elif cmd_lower == "dc-right":
                dc_right(60)
                tx_q.put("DC turning right")

            elif cmd_lower == "dc-stop":
                dc_stop()
                tx_q.put("DC stopped")

            elif cmd_lower == "sweep-left":
                servo_set_angle(0)
                tx_q.put("Servo swept left")

            elif cmd_lower == "sweep-right":
                servo_set_angle(180)
                tx_q.put("Servo swept right")

            elif cmd_lower == "step-right":
                stepper_half_turn(direction=1)
                tx_q.put("Stepper half turn right")

            elif cmd_lower == "step-left":
                stepper_half_turn(direction=-1)
                tx_q.put("Stepper half turn left")

            elif cmd_lower.startswith("step "):
                try:
                    degrees = int(cmd.split()[1])
                    direction = 1 if degrees >= 0 else -1
                    num_steps = degrees_to_steps(degrees)
                    stepper_turn_steps(num_steps, direction)
                    tx_q.put(f"Stepper moved {degrees} degrees")
                except (IndexError, ValueError):
                    tx_q.put("ERROR: use format like 'Step 90' or 'Step -45'")

            else:
                tx_q.put("ERROR: unknown command")

        except queue.Empty:
            pass

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Ctrl-C received, shutting down...")
    stop_ble_gatt_uart_loop()
    time.sleep(0.5)  # fixed: was sleep(0.5) — time not imported as sleep

finally:
    stop_stepper()
    dc_stop()
    dc_pwm1.stop()
    dc_pwm2.stop()
    servo_pwm.ChangeDutyCycle(0)
    servo_pwm.stop()
    time.sleep(0.5)
    GPIO.cleanup()
