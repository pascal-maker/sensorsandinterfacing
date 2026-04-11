import time
import RPi.GPIO as GPIO
import smbus
BUTTON = 26#setting the button pin
SERVO_PIN = 18#setting the servo pin
ADC_ADDRESS = 0x48#setting the adc address
JOYSTICK_X_CHANNEL = 6#setting the joystick x channel
PWM_FREQ = 50#setting the pwm frequency
MIN_PULSE_MS = 0.6#setting the minimum pulse width
MAX_PULSE_MS = 2.4#setting the maximum pulse width

GPIO.setmode(GPIO.BCM)#setting the mode to BCM
GPIO.setwarnings(False)#setting the warnings to false

GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setting the button pin as input
GPIO.setup(SERVO_PIN, GPIO.OUT)#setting the servo pin as output

bus = smbus.SMBus(1)#setting the bus

servo_pwm = GPIO.PWM(SERVO_PIN, PWM_FREQ)#setting the servo pin as pwm
servo_pwm.start(0)#starting the servo pin

servo_on = False#setting the servo to off
last_button_state = 1#setting the last button state to 1

def read_adc(channel):
    """
    Read one analog channel from the ADC.

    channel = which ADC input we want to read
    for example 0, 4, or 6
    """

    # Build the command byte for this ADC chip.
    # 0x84 is the basic control value.
    # The rest puts the channel number into the correct bit positions.
    command = 0x84 | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)

    # Ask the ADC at ADC_ADDRESS to return 1 byte for that command.
    # The returned value is usually between 0 and 255.
    return bus.read_byte_data(ADC_ADDRESS, command)
def adc_to_angle(adc_value):#converting the adc value to angle
    return (adc_value/255.0)*180#converting the adc value to angle

def angle_to_duty_cycle(angle):#converting the angle to duty cycle
    angle = max(0,min(180,angle))#clamping the angle between 0 and 180
    pulse_width_ms = MIN_PULSE_MS + (angle/180.0)*(MAX_PULSE_MS-MIN_PULSE_MS)#calculating the pulse width
    return (pulse_width_ms/20.0)*100.0#converting the pulse width to duty cycle

try:
    while True:
        current_button_state = GPIO.input(BUTTON)#reading the button state
        if current_button_state == 0 and last_button_state == 1:#checking if the button is pressed
            servo_on = not servo_on#changing the servo state
            time.sleep(0.2)#waiting for 0.2 seconds
        last_button_state = current_button_state#setting the last button state to current button state
        if servo_on:#checking if the servo is on
            adc_value = read_adc(JOYSTICK_X_CHANNEL)#reading the adc value
            angle = adc_to_angle(adc_value)#converting the adc value to angle
            duty_cycle = angle_to_duty_cycle(angle)#converting the angle to duty cycle
            servo_pwm.ChangeDutyCycle(duty_cycle)#changing the servo duty cycle

            print(f" SERVO ON | ADC: {adc_value:3} | Angle: {angle:5.1f}° | Duty Cycle: {duty_cycle:5.1f}%")
            time.sleep(0.05)#waiting for 0.05 seconds
        else:
            servo_pwm.ChangeDutyCycle(0)#setting the servo duty cycle to 0%
            print(" SERVO OFF")
        time.sleep(0.1)
except KeyboardInterrupt:
    servo_pwm.stop()
    GPIO.cleanup()
    print("Servo stopped by user")

        
    
