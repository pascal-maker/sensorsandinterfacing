import time
import RPi.GPIO as GPIO
import smbus

BUTTON = 26
SERVO = 18
ADC_ADDRESS = 0x48
CHANNEL = 6

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SERVO, GPIO.OUT)

bus = smbus.SMBus(1)
pwm = GPIO.PWM(SERVO, 50)
pwm.start(0)

servo_on = False
last_button = 1

def read_adc(channel):
    command = 0x84 | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)
    return bus.read_byte_data(ADC_ADDRESS, command)

try:
    while True:
        button = GPIO.input(BUTTON)

        if last_button == 1 and button == 0:
            servo_on = not servo_on
            time.sleep(0.2)

        last_button = button

        if servo_on:
            adc = read_adc(CHANNEL)
            angle = adc / 255 * 180
            duty = 3 + (angle / 180) * 9
            pwm.ChangeDutyCycle(duty)
            print("ON", adc, angle)
        else:
            pwm.ChangeDutyCycle(0)
            print("OFF")

        time.sleep(0.05)

except KeyboardInterrupt:
    pwm.stop()
    bus.close()
    GPIO.cleanup()