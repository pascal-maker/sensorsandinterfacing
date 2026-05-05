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
dc_pwm1.start(0)#creating a pwm signal for the first motor pin
dc_pwm2.start(0)#creating a pwm signal for the second motor pin

servo_pwm = GPIO.PWM(SERVO_PIN, 50)#creating a pwm signal for the servo pin
servo_pwm.start(0)#starting the pwm signal for the servo pin

# ----------------------
# Variables
# ----------------------
OFF = 0#setting the off variable to 0
LEFT = 1#setting the left variable to 1
RIGHT = 2#setting the right variable to 2
dc_mode = OFF#setting the dc mode to off
step_index = 0#setting the step index to 0

# ----------------------
# Steps
# ----------------------
steps = (#setting the steps for the stepper motor
    (1, 0, 0, 0),#step1 of the stepper motor
    (1, 1, 0, 0),#step2 of the stepper motor
    (0, 1, 0, 0),#step3 of the stepper motor
    (0, 1, 1, 0),#step4 of the stepper motor
    (0, 0, 1, 0),#step5 of the stepper motor
    (0, 0, 1, 1),#step6 of the stepper motor
    (0, 0, 0, 1),#step7 of the stepper motor
    (1, 0, 0, 1),#step8 of the stepper motor
)

# ----------------------
# BLE queues and thread
# ----------------------
rx_q = queue.Queue()#setting the rx queue
tx_q = queue.Queue()#setting the tx queue

threading.Thread(
    target=ble_gatt_uart_loop,#starting the thread
    args=(rx_q, tx_q, "pj-pi-gatt-uart"),#arguments for the thread
    daemon=True
).start()#running the thread

# ----------------------
# Stepper functions
# ----------------------
def stop_stepper():#stopping the stepper motor
    for pin in STEPPER_PINS:#setting the pins
        GPIO.output(pin, 0)#setting the pins to output

def stepper_half_turn(direction):#rotating the stepper motor in half turn direction
    global step_index#setting the step index
    for _ in range(2048):#iterating through the steps
        step_index = (step_index + direction) % 8#setting the step index
        for i, pin in enumerate(STEPPER_PINS):#setting the pins
            GPIO.output(pin, steps[step_index][i])#setting the pins to output
        time.sleep(0.002)#waiting for the step delay
    stop_stepper()#stopping the stepper motor

def degrees_to_steps(degrees):
    return int(abs(degrees) / 360 * 4096)  # 512 cycles × 8 half-steps = 4096

def stepper_turn_steps(num_steps, direction):#rotating the stepper motor in steps direction
    global step_index#setting the step index
    for _ in range(num_steps):#iterating through the steps
        step_index = (step_index + direction) % 8#setting the step index
        for i, pin in enumerate(STEPPER_PINS):#setting the pins
            GPIO.output(pin, steps[step_index][i])#setting the pins to output
        time.sleep(0.002)#waiting for the step delay
    stop_stepper()#stopping the stepper motor

# ----------------------
# DC motor functions
# ----------------------
def dc_left(speed):#moving the dc motor in left direction
    dc_pwm1.ChangeDutyCycle(speed)#setting the pin 1 to speed% duty cycle
    dc_pwm2.ChangeDutyCycle(0)#setting the pin 2 to 0% duty cycle

def dc_right(speed):#moving the dc motor in right direction
    dc_pwm1.ChangeDutyCycle(0)#setting the pin 1 to 0% duty cycle
    dc_pwm2.ChangeDutyCycle(speed)#setting the pin 2 to speed% duty cycle

def dc_stop():#stopping the dc motor
    dc_pwm1.ChangeDutyCycle(0)#setting the pin 1 to 0% duty cycle
    dc_pwm2.ChangeDutyCycle(0)#setting the pin 2 to 0% duty cycle

# ----------------------
# Servo functions
# ----------------------
def servo_set_angle(angle):#setting the servo angle
    angle = max(0, min(180, angle))#setting the angle to be between 0 and 180
    duty = angle / 18 + 2#setting the duty cycle
    servo_pwm.ChangeDutyCycle(duty)#setting the pwm signal for the servo pin

# ----------------------
# Main loop
# ----------------------
try:#main loop
    while True:#looping through the main loop
        try:#checking if there is a command
            cmd = rx_q.get(timeout=0.01)#getting the command
            cmd_lower = cmd.strip().lower()#getting the command in lowercase

            if cmd_lower == "dc-left":#checking if the command is dc-left
                dc_left(60)
                tx_q.put("DC turning left")

            elif cmd_lower == "dc-right":#checking if the command is dc-right
                dc_right(60)
                tx_q.put("DC turning right")

            elif cmd_lower == "dc-stop":#checking if the command is dc-stop
                dc_stop()
                tx_q.put("DC stopped")

            elif cmd_lower == "sweep-left":#checking if the command is sweep-left
                servo_set_angle(0)
                tx_q.put("Servo swept left")

            elif cmd_lower == "sweep-right":#checking if the command is sweep-right
                servo_set_angle(180)
                tx_q.put("Servo swept right")

            elif cmd_lower == "step-right":#checking if the command is step-right
                stepper_half_turn(direction=1)#rotating the stepper motor in right direction
                tx_q.put("Stepper half turn right")

            elif cmd_lower == "step-left":#checking if the command is step-left
                stepper_half_turn(direction=-1)#rotating the stepper motor in left direction
                tx_q.put("Stepper half turn left")

            elif cmd_lower.startswith("step "):#checking if the command is step
                try:#try
                    degrees = int(cmd.split()[1])#getting the degrees
                    direction = 1 if degrees >= 0 else -1#setting the direction
                    num_steps = degrees_to_steps(degrees)#calculating the steps
                    stepper_turn_steps(num_steps, direction)#rotating the stepper motor in steps direction
                    tx_q.put(f"Stepper moved {degrees} degrees")#printing the degrees   
                except (IndexError, ValueError):#error handling
                    tx_q.put("ERROR: use format like 'Step 90' or 'Step -45'")#printing the error

            else:#error handling
                tx_q.put("ERROR: unknown command")#printing the error

        except queue.Empty:#error handling
            pass

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Ctrl-C received, shutting down...")
    stop_ble_gatt_uart_loop()#stopping the ble gatt uart loop
    time.sleep(0.5)  # fixed: was sleep(0.5) — time not imported as sleep

finally:
    stop_stepper()#stopping the stepper motor
    dc_stop()#stopping the dc motor
    dc_pwm1.stop()#stopping the dc pwm signal for the first motor pin
    dc_pwm2.stop()#stopping the dc pwm signal for the second motor pin
    servo_pwm.ChangeDutyCycle(0)#stopping the pwm signal for the servo pin
    servo_pwm.stop()#stopping the pwm signal for the servo pin
    time.sleep(0.5)#waiting for the delay
    GPIO.cleanup()#cleaning up the gpio pins
