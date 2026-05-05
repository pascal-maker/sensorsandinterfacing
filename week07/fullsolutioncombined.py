import RPi.GPIO as GPIO
import smbus
import time
import threading

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  

# ----------------------
# Pins
# ----------------------
BUTTON_LEFT = 20#setting the left button pin
BUTTON_RIGHT = 21#setting the right button pin
BUTTON_SERVO = 26#setting the servo button pin
BUTTON_DC = 16#setting the dc button pin
SERVO_PIN = 18#setting the servo pin
MOTOR_PIN1 = 14#setting the motor pin 1
MOTOR_PIN2 = 15#setting the motor pin 2
ADC_ADDRESS = 0x48#setting the adc address
JOYSTICK_X_CHANNEL = 6#setting the joystick x channel
POT_CHANNEL = 0#setting the pot channel
STEPPER_PINS = (19, 13, 6, 5)#setting the pins for the stepper motor
bus = smbus.SMBus(1)#setting the bus

# ----------------------
# GPIO Setup
# ----------------------
GPIO.setup(BUTTON_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setting the left button as input with pull up
GPIO.setup(BUTTON_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setting the right button as input with pull up
GPIO.setup(BUTTON_SERVO, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setting the servo button as input with pull up
GPIO.setup(BUTTON_DC, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setting the dc button as input with pull up
GPIO.setup(SERVO_PIN, GPIO.OUT)#setting the servo pin as output
GPIO.setup(MOTOR_PIN1, GPIO.OUT)#setting the motor pin 1 as output
GPIO.setup(MOTOR_PIN2, GPIO.OUT)#setting the motor pin 2 as output
GPIO.setup(STEPPER_PINS, GPIO.OUT)#setting the stepper pins as output

# ----------------------
# PWM Setup
# ----------------------
servo_pwm = GPIO.PWM(SERVO_PIN, 50)#setting the servo pwm frequency
servo_pwm.start(0)#starting the servo pwm
motor_pwm1 = GPIO.PWM(MOTOR_PIN1, 1000)#setting the motor pwm frequency
motor_pwm2 = GPIO.PWM(MOTOR_PIN2, 1000)#setting the motor pwm frequency
motor_pwm1.start(0)#starting the motor pwm
motor_pwm2.start(0)#starting the motor pwm

# ----------------------
# Variables
# ----------------------
left_pressed = False#setting the left button pressed variable to false
right_pressed = False#setting the right button pressed variable to false
servo_on = False#setting the servo on variable to false
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
# Functions
# ----------------------#function to read adc values
def read_adc(channel):#function to read adc values
    if channel == 6:#checking if the channel is 6
        command = 0x84 | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)#command to read adc values
        return bus.read_byte_data(ADC_ADDRESS,command)#return the adc value
    else: #else the channel is not 6
        control_byte = 0x40 | channel#setting the control byte
        bus.write_byte(ADC_ADDRESS, control_byte)#writing the control byte to the bus
        bus.read_byte(ADC_ADDRESS)#reading the adc value
        return bus.read_byte(ADC_ADDRESS)#returning the adc value

def angle_to_duty_cycle(angle):#converting the angle to duty cycle
    angle = max(0, min(180, angle))#clamping the angle between 0 and 180
    pulse_width_ms = 0.6 + (angle / 180.0) * (2.4 - 0.6)#calculating the pulse width
    return (pulse_width_ms / 20.0) * 100.0#converting the pulse width to duty cycle

def left_event(channel):#left button event
    global left_pressed#setting the left button pressed variable to true
    left_pressed = (GPIO.input(BUTTON_LEFT) == 0)#setting the left button pressed variable to true

def right_event(channel):#right button event
    global right_pressed#setting the right button pressed variable to true
    right_pressed = (GPIO.input(BUTTON_RIGHT) == 0)#setting the right button pressed variable to true

def dc_event(channel):#dc button event
    global dc_mode#setting the dc mode to off
    if GPIO.input(BUTTON_DC) == 0:#checking if the dc button is pressed
        dc_mode = (dc_mode + 1) % 3#changing the dc mode

def servo_event(channel):#servo button event
    global servo_on#setting the servo on variable to true
    if GPIO.input(BUTTON_SERVO) == 0:#checking if the servo button is pressed
        servo_on = not servo_on#changing the servo state

GPIO.add_event_detect(BUTTON_LEFT, GPIO.BOTH, callback=left_event, bouncetime=200)#adding event detection for the left button
GPIO.add_event_detect(BUTTON_RIGHT, GPIO.BOTH, callback=right_event, bouncetime=200)#adding event detection for the right button
GPIO.add_event_detect(BUTTON_DC, GPIO.FALLING, callback=dc_event, bouncetime=200)#adding event detection for the dc button
GPIO.add_event_detect(BUTTON_SERVO, GPIO.FALLING, callback=servo_event, bouncetime=200)#adding event detection for the servo button

# ----------------------
# Main Loop
# ----------------------
try:
    while True:
        # Servo control
      if left_pressed and not right_pressed:#checking if the left button is pressed
        step = steps[step_index]#getting the step for the stepper motor
        for i in range(4):#looping through the steps
            GPIO.output(STEPPER_PINS[i], step[i])#driving the pins
        step_index = (step_index + 1) % len(steps)#incrementing the step index
        time.sleep(0.002)#delay between steps
      elif right_pressed and not left_pressed:#checking if the right button is pressed
        step = steps[step_index]#getting the step for the stepper motor
        for i in range(4):#looping through the steps
            GPIO.output(STEPPER_PINS[i], step[i])#driving the pins
        step_index = (step_index - 1) % len(steps)#decrementing the step index
        time.sleep(0.002)#delay between steps
      else:
        for pin in STEPPER_PINS:#looping through the pins
            GPIO.output(pin, 0)#turning off the pins
      #dc motor
      pot_value = read_adc(POT_CHANNEL)#reading the adc value
      speed = (pot_value / 255.0) * 100.0#calculating the speed
      if dc_mode == OFF:#checking if the dc mode is off
        motor_pwm1.ChangeDutyCycle(0)#turning off the motor
        motor_pwm2.ChangeDutyCycle(0)#turning off the motor
      elif dc_mode == LEFT:#checking if the dc mode is left
        motor_pwm1.ChangeDutyCycle(speed)#changing the motor speed
        motor_pwm2.ChangeDutyCycle(0)#turning off the motor
      elif dc_mode == RIGHT:#checking if the dc mode is right
        motor_pwm1.ChangeDutyCycle(0)#turning off the motor
        motor_pwm2.ChangeDutyCycle(speed)#changing the motor speed
      
      #servo control
      if servo_on:#checking if the servo is on
        adc_value = read_adc(JOYSTICK_X_CHANNEL)#reading the adc value
        angle = (adc_value / 255.0) * 180#calculating the angle
        servo_pwm.ChangeDutyCycle(angle_to_duty_cycle(angle))#changing the servo duty cycle
        print(f"SERVO ON | ADC: {adc_value:3} | Angle: {angle:5.1f}° | Duty Cycle: {angle_to_duty_cycle(angle):5.1f}%")#printing the servo state
      else:
          servo_pwm.ChangeDutyCycle(0)#turning off the servo
          print("SERVO OFF")#printing the servo state
      time.sleep(0.05)#delay between steps

          

except KeyboardInterrupt:
    print("Program stopped by user")#printing the program stopped message
    servo_pwm.stop()#stopping the servo
    motor_pwm1.stop()#stopping the motor
    motor_pwm2.stop()#stopping the motor
    bus.close()#closing the bus
    GPIO.cleanup()#cleaning up the pins
