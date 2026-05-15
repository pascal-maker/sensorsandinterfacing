import time 
import RPi.GPIO as GPIO
import smbus

GPIO.setmode(GPIO.BCM)#setting the mode to BCM
GPIO.setwarnings(False) #setting the warnings to false

BUTTON = 16#setting the button pin
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setting the button pin as input

#DC motor pins
motorPin1 = 14#setting the motor pin 1
motorPin2 = 15#setting the motor pin 2

GPIO.setup(motorPin1, GPIO.OUT)#setting the motor pin 1 as output
GPIO.setup(motorPin2, GPIO.OUT)#setting the motor pin 2 as output

pwm1 = GPIO.PWM(motorPin1, 1000)#setting the motor pin 1 as pwm
pwm2 = GPIO.PWM(motorPin2, 1000)#setting the motor pin 2 as pwm

pwm1.start(0)#starting the motor pin 1
pwm2.start(0)#starting the motor pin 2

#ADC
ADC_ADDRESS = 0x48#setting the adc address
POT_CHANNEL = 3 #setting the pot channel
bus = smbus.SMBus(1)#setting the bus

# -----------------------------
# Modes
# -----------------------------
OFF = 0#setting the mode to off
LEFT = 1#setting the mode to left
RIGHT = 2#setting the mode to right

mode = OFF#setting the mode to off
last_button_state = 1#setting the last button state to 1
COMMANDS = [
    0x84, 0xC4, 0x94, 0xD4,# commands to read adc values for each channel
    0xA4, 0xE4, 0xB4, 0xF4#
]

def read_adc(channel):#function to read the adc value
    command = COMMANDS[channel]#setting the command for the adc
    bus.write_byte(ADC_ADDRESS, command)#writing the command to the adc
    return bus.read_byte(ADC_ADDRESS)#returning the adc value
# -----------------------------
# Main loop
# -----------------------------

try:
    while True:
        current_button_state = GPIO.input(BUTTON)#reading the button state
        if current_button_state == 0 and last_button_state == 1:#checking if the button is pressed
            mode = (mode + 1) % 3#changing the mode
            time.sleep(0.2)#waiting for 0.2 seconds
        last_button_state = current_button_state#setting the last button state to current button state
        
        adc_value = read_adc(POT_CHANNEL)#reading the adc value
        speed = (adc_value / 255.0) * 100.0#calculating the speed
        
        if mode == OFF:#checking the mode
            pwm1.ChangeDutyCycle(0)#setting the motor pin 1 to 0% duty cycle
            pwm2.ChangeDutyCycle(0)#setting the motor pin 2 to 0% duty cycle
        elif mode == LEFT:#checking the mode
            pwm1.ChangeDutyCycle(speed)#setting the motor pin 1 to speed% duty cycle
            pwm2.ChangeDutyCycle(0)#setting the motor pin 2 to 0% duty cycle
        elif mode == RIGHT:#checking the mode
            pwm1.ChangeDutyCycle(0)#setting the motor pin 1 to 0% duty cycle
            pwm2.ChangeDutyCycle(speed)#setting the motor pin 2 to speed% duty cycle
        print(f"Mode: {mode} | ADC: {adc_value:3} | Speed: {speed:5.1f}%")#printing the mode and speed
        time.sleep(0.1)#waiting for 0.1 seconds
except KeyboardInterrupt:
    print("Motor stopped by user")
    pwm1.stop()
    pwm2.stop()
    bus.close()
    GPIO.cleanup()
#A4 for channel 6 & channel 2 A a2 is for channel 1 and channel 5 channel 0 and 3 with joystick on gpio button     