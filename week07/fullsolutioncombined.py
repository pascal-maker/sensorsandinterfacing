import time
import smbus
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

STEPPER_PINS = (19,13,6,5)#setting the stepper pins
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

GPIO.setup(STEPPER_PINS, GPIO.OUT)#setting the stepper pins as output
GPIO.setup(BUTTON_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setting the left button as input
GPIO.setup(BUTTON_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setting the right button as input
GPIO.setup(BUTTON_SERVO, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setting the servo button as input
GPIO.setup(SERVO_PIN, GPIO.OUT)#setting the servo pin as output
GPIO.setup(MOTOR_PIN1, GPIO.OUT)#setting the motor pin 1 as output
GPIO.setup(MOTOR_PIN2, GPIO.OUT)#setting the motor pin 2 as output

bus = smbus.SMBus(1)#setting the bus

servo_pwm = GPIO.PWM(SERVO_PIN, 50)#setting the servo pin as pwm
servo_pwm.start(0)#starting the servo pin

motor_pwm1 = GPIO.PWM(MOTOR_PIN1, 1000)#setting the motor pin 1 as pwm
motor_pwm2 = GPIO.PWM(MOTOR_PIN2, 1000)#setting the motor pin 2 as pwm
motor_pwm1.start(0)#starting the motor pin 1
motor_pwm2.start(0)#starting the motor pin 2

left_pressed = False#setting the left pressed to false
right_pressed = False#setting the right pressed to false
servo_on = False#setting the servo on to false
OFF = 0#setting the mode to off
LEFT = 1#setting the mode to left
RIGHT = 2#setting the mode to right
dc_mode = OFF#setting the mode to off
step_index = 0#setting the step index to 0

steps = (
    (1, 0, 0, 0),#setting the stepper steps
    (1, 1, 0, 0),#setting the stepper steps
    (0, 1, 0, 0),#setting the stepper steps
    (0, 1, 1, 0),#setting the stepper steps
    (0, 0, 1, 0),#setting the stepper steps
    (0, 0, 1, 1),#setting the stepper steps
    (0, 0, 0, 1),#setting the stepper steps
    (1, 0, 0, 1),#setting the stepper steps
)



def read_adc(channel):#reading the adc value
    if channel == 6:#checking the channel
        command = 0x84 | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)#setting the command byte
        return bus.read_byte_data(ADC_ADDRESS,command)#returning the adc value
    else:
        control_byte = 0x40 | channel#setting the control byte
        bus.write_byte(ADC_ADDRESS, control_byte)#writing the control byte to the bus
        bus.read_byte(ADC_ADDRESS)#reading the adc value
        return bus.read_byte(ADC_ADDRESS)#returning the adc value



def angle_to_duty_cycle(angle):#converting the angle to duty cycle
    angle = max(0, min(180, angle))#clamping the angle between 0 and 180
    pulse_width_ms = 0.6 + (angle / 180.0) * (2.4 - 0.6)#calculating the pulse width
    return (pulse_width_ms / 20.0) * 100.0#converting the pulse width to duty cycle

def left_event(channel) :#checking the left button state
    global left_pressed#setting the left pressed to true
    left_pressed = (GPIO.input(BUTTON_LEFT) == 0)#checking the left button state

def right_event(channel) :#checking the right button state
    global right_pressed#setting the right pressed to true
    right_pressed = (GPIO.input(BUTTON_RIGHT) == 0)#checking the right button state

def dc_event(channel) :#checking the dc button state
    global dc_mode#setting the dc mode to true
    if GPIO.input(BUTTON_DC) == 0:#checking the dc button state
        dc_mode = (dc_mode + 1) % 3#changing the dc mode

def servo_event(channel) :#checking the servo button state
    global servo_on#setting the servo on to true
    if GPIO.input(BUTTON_SERVO) == 0:#checking the servo button state
        servo_on = not servo_on#changing the servo state

GPIO.add_event_detect(BUTTON_LEFT, GPIO.BOTH, callback=left_event, bouncetime=200)
GPIO.add_event_detect(BUTTON_RIGHT, GPIO.BOTH, callback=right_event, bouncetime=200)
GPIO.add_event_detect(BUTTON_DC, GPIO.FALLING, callback=dc_event, bouncetime=200)#adding the dc button event
GPIO.add_event_detect(BUTTON_SERVO, GPIO.FALLING, callback=servo_event, bouncetime=200)#adding the servo button event


try:
    while True:
        # Servo control
      if left_pressed and not right_pressed:#checking the left button state
        step = steps[step_index]#setting the step
        for i in range(4):#setting the stepper pins
            GPIO.output(STEPPER_PINS[i], step[i])
        step_index = (step_index + 1) % len(steps)#incrementing the step index
        time.sleep(0.002)#waiting for 0.002 seconds
      elif right_pressed and not left_pressed:#checking the right button state
        step = steps[step_index]#setting the step
        for i in range(4):#setting the stepper pins
            GPIO.output(STEPPER_PINS[i], step[i])
        step_index = (step_index - 1) % len(steps)#decrementing the step index
        time.sleep(0.002)#waiting for 0.002 seconds
      else:
        for pin in STEPPER_PINS:#setting the stepper pins to 0
            GPIO.output(pin, 0)
      #c dc motor
      pot_value = read_adc(POT_CHANNEL)#reading the adc value
      speed = (pot_value / 255.0) * 100.0#calculating the speed
      if dc_mode == OFF:#checking the dc mode
        motor_pwm1.ChangeDutyCycle(0)#setting the motor pin 1 to 0% duty cycle
        motor_pwm2.ChangeDutyCycle(0)#setting the motor pin 2 to 0% duty cycle
      elif dc_mode == LEFT:#checking the dc mode
        motor_pwm1.ChangeDutyCycle(speed)#setting the motor pin 1 to speed% duty cycle
        motor_pwm2.ChangeDutyCycle(0)#setting the motor pin 2 to 0% duty cycle
      elif dc_mode == RIGHT:#checking the dc mode
        motor_pwm1.ChangeDutyCycle(0)#setting the motor pin 1 to 0% duty cycle
        motor_pwm2.ChangeDutyCycle(speed)#setting the motor pin 2 to speed% duty cycle
      
      #servo control
      if servo_on:
        adc_value = read_adc(JOYSTICK_X_CHANNEL)#reading the adc value
        angle = (adc_value / 255.0) * 180#calculating the angle
        servo_pwm.ChangeDutyCycle(angle_to_duty_cycle(angle))#setting the servo duty cycle
        print(f"SERVO ON | ADC: {adc_value:3} | Angle: {angle:5.1f}° | Duty Cycle: {angle_to_duty_cycle(angle):5.1f}%")
      else:#checking the servo state
          servo_pwm.ChangeDutyCycle(0)#setting the servo duty cycle to 0
          print("SERVO OFF")
      time.sleep(0.05)#waiting for 0.05 seconds

          

except KeyboardInterrupt:#checking for keyboard interrupt
    print("Program stopped by user")#printing that the program is stopped by user
    servo_pwm.stop()#stopping the servo pwm
    motor_pwm1.stop()
    motor_pwm2.stop()
    bus.close()
    GPIO.cleanup()