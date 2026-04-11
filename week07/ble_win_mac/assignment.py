import time
import queue
import threading
import RPi.GPIO as GPIO

# import the BLE UART loop from your BLE files
# change this import only if your folder structure is different
from ble.bluetooth_uart_server import ble_gatt_uart_loop#importing the ble uart loop

# =========================================================
# GPIO SETUP
# =========================================================

GPIO.setmode(GPIO.BCM)#setting the mode to BCM
GPIO.setwarnings(False)#setting the warnings to false

# -------------------------
# Stepper motor pins
# -------------------------
# These 4 pins control the stepper motor driver
STEPPER_PINS = (19, 13, 6, 5)#setting the stepper motor pins
GPIO.setup(STEPPER_PINS, GPIO.OUT)#setting the stepper motor pins as output

# -------------------------
# DC motor pins
# -------------------------
# These 2 pins control the H-bridge / motor driver
MOTOR_PIN1 = 14#setting the dc motor pins
MOTOR_PIN2 = 15#setting the dc motor pins
GPIO.setup(MOTOR_PIN1, GPIO.OUT)#setting the dc motor pins as output
GPIO.setup(MOTOR_PIN2, GPIO.OUT)#setting the dc motor pins as output

# -------------------------
# Servo pin
# -------------------------
SERVO_PIN = 18#setting the servo pin
GPIO.setup(SERVO_PIN, GPIO.OUT)#setting the servo pin as output

# =========================================================
# PWM SETUP
# =========================================================

# DC motor PWM at 1000 Hz
dc_pwm1 = GPIO.PWM(MOTOR_PIN1, 1000)#setting the dc motor pwm
dc_pwm2 = GPIO.PWM(MOTOR_PIN2, 1000)#setting the dc motor pwm
dc_pwm1.start(0)#starting the dc motor pwm
dc_pwm2.start(0)#starting the dc motor pwm

# Servo PWM at 50 Hz
servo_pwm = GPIO.PWM(SERVO_PIN, 50)#setting the servo pwm
servo_pwm.start(0)#starting the servo pwm

# =========================================================
# BLE SETUP
# =========================================================

# RX queue = phone -> Pi
rx_q = queue.Queue()#setting the rx queue

# TX queue = Pi -> phone
tx_q = queue.Queue()#setting the tx queue

# Bluetooth name that should appear on your phone
device_name = "pj-pi-gatt-uart"#setting the bluetooth name

# Start BLE UART loop in a background thread
threading.Thread(#starting the ble uart loop in a background thread
    target=ble_gatt_uart_loop,#setting the ble uart loop
    args=(rx_q, tx_q, device_name),#setting the rx queue, tx queue and device name
    daemon=True#setting the daemon to true
).start()

# =========================================================
# STATES
# =========================================================

# fixed speed for DC motor commands
dc_speed = 60.0#setting the dc motor speed

# servo starts in the middle
servo_angle = 90.0#setting the servo angle
servo_target = 90.0#setting the servo target

# stepper motor state
step_index = 0#setting the stepper index
stepper_steps_left = 0#setting the stepper steps left
stepper_direction = 1#setting the stepper direction

# 8-step half-step sequence for the stepper motor
steps = (
    (1, 0, 0, 0),
    (1, 1, 0, 0),
    (0, 1, 0, 0),
    (0, 1, 1, 0),
    (0, 0, 1, 0),
    (0, 0, 1, 1),
    (0, 0, 0, 1),
    (1, 0, 0, 1),
)#setting the stepper motor steps

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def angle_to_duty(angle):#converting the angle to duty cycle
    """
    Convert a servo angle (0..180) to PWM duty cycle.
    """
    angle = max(0, min(180, angle))  # clamp between 0 and 180

    # convert angle to pulse width in ms
    pulse_ms = 0.6 + (angle / 180.0) * (2.4 - 0.6)

    # servo period at 50 Hz = 20 ms
    return (pulse_ms / 20.0) * 100.0


def set_servo(angle):#setting the servo angle
    """
    Move the servo to a given angle.
    """
    global servo_angle#setting the servo angle

    servo_angle = max(0, min(180, angle))#setting the servo angle
    duty = angle_to_duty(servo_angle)#setting the duty cycle

    servo_pwm.ChangeDutyCycle(duty)#setting the duty cycle
    time.sleep(0.05)#waiting for 0.05 seconds
    servo_pwm.ChangeDutyCycle(0)   # reduce jitter


def dc_left():#setting the dc motor left
    """
    Turn DC motor left at fixed speed.
    """
    dc_pwm1.ChangeDutyCycle(dc_speed)#setting the duty cycle
    dc_pwm2.ChangeDutyCycle(0)#setting the duty cycle


def dc_right():#setting the dc motor right
    """
    Turn DC motor right at fixed speed.
    """
    dc_pwm1.ChangeDutyCycle(0)#setting the duty cycle
    dc_pwm2.ChangeDutyCycle(dc_speed)#setting the duty cycle


def dc_stop():#setting the dc motor stop
    """
    Stop DC motor.
    """
    dc_pwm1.ChangeDutyCycle(0)#setting the duty cycle
    dc_pwm2.ChangeDutyCycle(0)#setting the duty cycle


def stepper_stop():#setting the stepper motor stop
    """
    Turn all stepper coils off.
    """
    for pin in STEPPER_PINS:#setting the stepper pins to 0
        GPIO.output(pin, 0)#setting the stepper pins to 0


def stepper_one_step(direction):#setting the stepper motor one step
    """
    Do one physical step on the stepper motor.
    direction = +1 or -1
    """
    global step_index#setting the step index

    # get current step pattern
    step = steps[step_index]

    # send that pattern to the 4 stepper pins
    for i in range(4):
        GPIO.output(STEPPER_PINS[i], step[i])

    # move step index forward or backward
    step_index = (step_index + direction) % len(steps)

    # small delay so the motor can physically move
    time.sleep(0.002)


def degrees_to_steps(degrees):#converting the degrees to steps
    """
    Convert real shaft degrees to number of motor steps.

    From your course:
    360 degrees = 4096 real output steps
    """
    return round(abs(degrees) / 360.0 * 4096)#returning the number of steps


def start_stepper_move(degrees):#starting the stepper motor move
    """
    Prepare a stepper movement job.
    Positive degrees = one direction
    Negative degrees = other direction
    """
    global stepper_steps_left, stepper_direction#setting the stepper steps left and stepper direction

    stepper_steps_left = degrees_to_steps(degrees)#setting the stepper steps left

    if degrees >= 0:#setting the stepper direction
        stepper_direction = 1
    else:
        stepper_direction = -1#setting the stepper direction


# =========================================================
# COMMAND HANDLER
# =========================================================

def handle_command(cmd):#handling the command
    """
    Interpret the BLE text command and perform the right action.
    """
    global servo_target#setting the servo target

    cmd = cmd.strip()#stripping the command
    cmd_lower = cmd.lower()#converting the command to lower case

    # -------------------------
    # DC motor commands
    # -------------------------
    if cmd_lower == "dc-left":#checking if the command is dc-left
        dc_left()
        print("DC motor left")
        tx_q.put("OK: DC-left")
        return

    if cmd_lower == "dc-right":#checking if the command is dc-right
        dc_right()
        print("DC motor right")
        tx_q.put("OK: DC-right")
        return

    if cmd_lower == "dc-stop":#checking if the command is dc-stop
        dc_stop()
        print("DC motor stop")
        tx_q.put("OK: DC-stop")
        return

    # -------------------------
    # Servo commands
    # -------------------------
    if cmd_lower == "sweep-left":#checking if the command is sweep-left
        servo_target = 0
        print("Servo sweep left")
        tx_q.put("OK: Sweep-left")
        return

    if cmd_lower == "sweep-right":#checking if the command is sweep-right
        servo_target = 180
        print("Servo sweep right")
        tx_q.put("OK: Sweep-right")
        return

    # -------------------------
    # Stepper fixed commands
    # -------------------------
    if cmd_lower == "step-right":#checking if the command is step-right
        start_stepper_move(180)   # half turn
        print("Stepper half turn right")
        tx_q.put("OK: Step-right")
        return

    if cmd_lower == "step-left":#checking if the command is step-left
        start_stepper_move(-180)  # half turn opposite direction
        print("Stepper half turn left")
        tx_q.put("OK: Step-left")
        return

    # -------------------------
    # Stepper custom degree command
    # -------------------------
    # Example: Step 90
    # Example: Step -45
    if cmd_lower.startswith("step "):#checking if the command starts with step
        try:
            value = float(cmd.split()[1])#getting the value
            start_stepper_move(value)#starting the stepper motor move
            print(f"Stepper move {value} degrees")#printing the stepper motor move
            tx_q.put(f"OK: Step {value}")#putting the value in the tx queue
        except:
            print("Wrong step command")
            tx_q.put("ERROR: use Step 90 or Step -45")
        return

    # -------------------------
    # Unknown command
    # -------------------------
    print("Unknown command:", cmd)
    tx_q.put("ERROR: Unknown command")


# =========================================================
# MAIN LOOP
# =========================================================

try:
    print("BLE motor controller started")#printing the ble motor controller started
    print("Bluetooth name:", device_name)#printing the bluetooth name

    while True:#looping through the code
        # -------------------------
        # Check if a BLE message came in
        # -------------------------
        try:
            incoming = rx_q.get(timeout=0.02)#getting the incoming message
            if incoming:#checking if the incoming message is not empty
                print("Received:", incoming)#printing the incoming message
                handle_command(incoming)#handling the incoming message
        except queue.Empty:#checking if the queue is empty
            pass

        # -------------------------
        # Move servo gradually to target angle
        # -------------------------
        if servo_angle < servo_target:#checking if the servo angle is less than the servo target
            set_servo(min(servo_angle + 2, servo_target))#setting the servo angle
        elif servo_angle > servo_target:#checking if the servo angle is greater than the servo target
            set_servo(max(servo_angle - 2, servo_target))

        # -------------------------
        # Continue stepper movement if a job is active
        # -------------------------
        if stepper_steps_left > 0:#checking if the stepper steps left is greater than 0
            stepper_one_step(stepper_direction)#taking one step of the stepper motor
            stepper_steps_left -= 1
        else:
            stepper_stop()

except KeyboardInterrupt:
    print("Program stopped by user")#printing that the program is stopped by user

finally:
    dc_stop()
    stepper_stop()
    servo_pwm.stop()
    dc_pwm1.stop()
    dc_pwm2.stop()
    GPIO.cleanup()