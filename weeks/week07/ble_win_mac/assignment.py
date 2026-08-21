import time 
import queue
import threading
import RPi.GPIO as GPIO

# import the BLE UART loop from your BLE files
# change this import only if your folder structure is different
from ble.bluetooth_uart_server import ble_gatt_uart_loop, stop_ble_gatt_uart_loop
# ----------------------
# Variables
# ----------------------
left_pressed = False#setting the left button pressed variable to false
right_pressed = False#setting the right button pressed variable to false
servo_on = False#setting the servo on variable to true
OFF = 0#setting the off variable to 0
LEFT = 1#setting the left variable to 1
RIGHT = 2#setting the right variable to 2
dc_mode = OFF#setting the dc mode to off
step_index = 0#setting the step index to 0

# ----------------------
# Steps
# ----------------------
steps = (
    (1, 0, 0, 0),#setting the steps for the stepper motor
    (1, 1, 0, 0),#step2 of the stepper motor
    (0, 1, 0, 0),#step3 of the stepper motor
    (0, 1, 1, 0),#step4 of the stepper motor
    (0, 0, 1, 0),#step5 of the stepper motor
    (0, 0, 1, 1),#step6 of the stepper motor
    (0, 0, 0, 1),#step7 of the stepper motor
    (1, 0, 0, 1),#step8 of the stepper motor
)

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



#SERVO motor
servo_pin = 18
GPIO.setup(servo_pin, GPIO.OUT)
#PWM
dc_pwm1 = GPIO.PWM(motor_pin1, 100)#creating the PWM signal for the first motor pin
dc_pwm2 = GPIO.PWM(motor_pin2, 100)#creating the PWM signal for the second motor pin
dc_pwm1.start(0)#starting the PWM signal for the first motor pin
dc_pwm2.start(0)#starting the PWM signal for the second motor pin

servo_pwm = GPIO.PWM(servo_pin, 50)#creating the PWM signal for the servo pin
servo_pwm.start(0)#starting the PWM signal for the servo pin
#ble queques and threads
rx_q = queue.Queue()
tx_q = queue.Queue()
threading.Thread(target=ble_gatt_uart_loop, args=(rx_q, tx_q, "pj-pi-gatt-uart"), daemon=True).start()

# add the functions for the stepper motor
def stop_stepper():
    for pin in STEPPER_PINS:
        GPIO.output(pin, 0)

def stepper_half_turn(direction):
      global step_index                                             
      for _ in range(2048):           # 2048 not 4                  
          step_index = (step_index + direction) % 8
          for i, pin in enumerate(STEPPER_PINS):                    
              GPIO.output(pin, steps[step_index][i])        
          time.sleep(0.002)                                         
      stop_stepper()        

# add the functions for the DC motor
def dc_left(speed):
    dc_pwm1.ChangeDutyCycle(speed)
    dc_pwm2.ChangeDutyCycle(0)

def dc_right(speed):
    dc_pwm1.ChangeDutyCycle(0)
    dc_pwm2.ChangeDutyCycle(speed)

def dc_stop():
    dc_pwm1.ChangeDutyCycle(0)
    dc_pwm2.ChangeDutyCycle(0)

# add the functions for the servo motor
def servo_set_angle(angle):
    if angle < 0:
        angle = 0
    if angle > 180:
        angle = 180
    duty = angle / 18 + 2
    servo_pwm.ChangeDutyCycle(duty)

# add the function to convert degrees to steps
def degrees_to_steps(degrees):
    return int(abs(degrees) / 360 * 4096)  # 512 cycles × 8 half-steps = 4096

# add the function to control the stepper motor
def stepper_turn_steps(num_steps, direction):   # rename parameter
      global step_index                                             
      for _ in range(num_steps):                                    
          step_index = (step_index + direction) % 8
          for i, pin in enumerate(STEPPER_PINS):                    
              GPIO.output(pin, steps[step_index][i])   
          time.sleep(0.002)
      stop_stepper()                   

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
                    cycles = degrees_to_steps(degrees)

                    stepper_turn_steps(cycles, direction)
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
    sleep(0.5)

finally:
    stop_stepper()
    dc_stop()

    dc_pwm1.stop()
    dc_pwm2.stop()
   
    servo_pwm.ChangeDutyCycle(0)
    servo_pwm.stop()

    stop_ble_gatt_uart_loop()
    time.sleep(0.5)
    GPIO.cleanup()
