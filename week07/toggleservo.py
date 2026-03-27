from RPi import GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

BTN_SERVO = 26
SERVO_PIN = 18

GPIO.setup(BTN_SERVO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SERVO_PIN, GPIO.OUT)

servo_pwm = GPIO.PWM(SERVO_PIN, 50)
servo_pwm.start(0)

servo_enabled = False

def read_adc(channel):
    # Replace this with your real ADC code
    return 128

def adc_to_angle(adc_value):
    return int((adc_value / 255) * 180)

def angle_to_duty(angle):
    return 2 + (angle / 18)

def toggle_servo(channel):
    global servo_enabled
    servo_enabled = not servo_enabled
    print("SERVO ON" if servo_enabled else "SERVO OFF")

GPIO.add_event_detect(BTN_SERVO, GPIO.FALLING, callback=toggle_servo, bouncetime=250)

try:
    while True:
        if servo_enabled:
            x_raw = read_adc(6)
            angle = adc_to_angle(x_raw)
            duty = angle_to_duty(angle)
            servo_pwm.ChangeDutyCycle(duty)
            print(f"SERVO angle={angle}° raw={x_raw}")
        else:
            servo_pwm.ChangeDutyCycle(0)

        sleep(0.1)

except KeyboardInterrupt:
    servo_pwm.ChangeDutyCycle(0)
    servo_pwm.stop()
    servo_pwm = None
    GPIO.cleanup()