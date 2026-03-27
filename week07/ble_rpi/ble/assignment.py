import bluetooth_uart_server
from RPi import GPIO
from time import sleep
import threading
import queue

# -------------------------
# GPIO setup
# -------------------------
GPIO.setmode(GPIO.BCM)

# Stepper
STEPPER_PINS = (19, 13, 6, 5)
GPIO.setup(STEPPER_PINS, GPIO.OUT)

STEPS = (
    (1, 0, 0, 0),
    (1, 1, 0, 0),
    (0, 1, 0, 0),
    (0, 1, 1, 0),
    (0, 0, 1, 0),
    (0, 0, 1, 1),
    (0, 0, 0, 1),
    (1, 0, 0, 1),
)

# DC motor
DC_PIN_1 = 14
DC_PIN_2 = 15
GPIO.setup(DC_PIN_1, GPIO.OUT)
GPIO.setup(DC_PIN_2, GPIO.OUT)

dc_pwm_1 = GPIO.PWM(DC_PIN_1, 1000)
dc_pwm_2 = GPIO.PWM(DC_PIN_2, 1000)
dc_pwm_1.start(0)
dc_pwm_2.start(0)

# Servo
SERVO_PIN = 18
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo_pwm = GPIO.PWM(SERVO_PIN, 50)
servo_pwm.start(0)

# -------------------------
# BLE queues + thread
# -------------------------
rx_q = queue.Queue()
tx_q = queue.Queue()

threading.Thread(
    target=bluetooth_uart_server.ble_gatt_uart_loop,
    args=(rx_q, tx_q, "pjs-rpi-PM"),
    daemon=True
).start()

# -------------------------
# Helpers
# -------------------------
def stop_stepper():
    for pin in STEPPER_PINS:
        GPIO.output(pin, 0)

def apply_step(step):
    for i in range(4):
        GPIO.output(STEPPER_PINS[i], step[i])

def stepper_turn_steps(step_count, direction=1, delay=0.001):
    sequence = STEPS if direction > 0 else tuple(reversed(STEPS))
    for _ in range(step_count):
        for step in sequence:
            apply_step(step)
            sleep(delay)
    stop_stepper()

def stepper_half_turn(direction=1):
    # Based on your class note: 512 cycles ≈ 1 full output rotation
    # so half turn ≈ 256
    stepper_turn_steps(256, direction)

def degrees_to_cycles(degrees):
    # 512 cycles ~= 360 degrees
    return int(abs(degrees) * 512 / 360)

def servo_angle_to_duty(angle):
    # simple 0..180 mapping
    angle = max(0, min(180, angle))
    return 2 + (angle / 18)

def servo_set_angle(angle):
    duty = servo_angle_to_duty(angle)
    servo_pwm.ChangeDutyCycle(duty)
    sleep(0.3)
    servo_pwm.ChangeDutyCycle(0)

def dc_stop():
    dc_pwm_1.ChangeDutyCycle(0)
    dc_pwm_2.ChangeDutyCycle(0)

def dc_left(speed=60):
    dc_pwm_1.ChangeDutyCycle(speed)
    dc_pwm_2.ChangeDutyCycle(0)

def dc_right(speed=60):
    dc_pwm_1.ChangeDutyCycle(0)
    dc_pwm_2.ChangeDutyCycle(speed)

# -------------------------
# Main BLE command loop
# -------------------------
print("BLE motor controller started: pjs-rpi-PM")

try:
    while True:
        try:
            incoming = rx_q.get_nowait()
        except queue.Empty:
            incoming = None

        if incoming:
            cmd = str(incoming).strip()
            cmd_lower = cmd.lower()

            print("Incoming:", cmd)
            tx_q.put(f"ACK: {cmd}")

            # DC commands
            if cmd_lower == "dc-left":
                dc_left(60)
                tx_q.put("DC turning left")

            elif cmd_lower == "dc-right":
                dc_right(60)
                tx_q.put("DC turning right")

            elif cmd_lower == "dc-stop":
                dc_stop()
                tx_q.put("DC stopped")

            # Servo sweep commands
            elif cmd_lower == "sweep-left":
                servo_set_angle(0)
                tx_q.put("Servo swept left")

            elif cmd_lower == "sweep-right":
                servo_set_angle(180)
                tx_q.put("Servo swept right")

            # Stepper fixed half-turn commands
            elif cmd_lower == "step-right":
                stepper_half_turn(direction=1)
                tx_q.put("Stepper half turn right")

            elif cmd_lower == "step-left":
                stepper_half_turn(direction=-1)
                tx_q.put("Stepper half turn left")

            # Step ### command
            elif cmd_lower.startswith("step "):
                try:
                    degrees = int(cmd.split()[1])
                    direction = 1 if degrees >= 0 else -1
                    cycles = degrees_to_cycles(degrees)

                    stepper_turn_steps(cycles, direction)
                    tx_q.put(f"Stepper moved {degrees} degrees")

                except (IndexError, ValueError):
                    tx_q.put("ERROR: use format like 'Step 90' or 'Step -45'")

            else:
                tx_q.put("ERROR: unknown command")

        sleep(0.05)

except KeyboardInterrupt:
    print("Ctrl-C received, shutting down...")
    bluetooth_uart_server.stop_ble_gatt_uart_loop()
    sleep(0.5)

finally:
    stop_stepper()
    dc_stop()

    dc_pwm_1.stop()
    dc_pwm_2.stop()
    dc_pwm_1 = None
    dc_pwm_2 = None

    servo_pwm.ChangeDutyCycle(0)
    servo_pwm.stop()
    servo_pwm = None

    GPIO.cleanup()