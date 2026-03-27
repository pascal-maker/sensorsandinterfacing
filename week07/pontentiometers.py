from RPi import GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

BTN_DC = 16
DC_PIN_1 = 14
DC_PIN_2 = 15

GPIO.setup(BTN_DC, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DC_PIN_1, GPIO.OUT)
GPIO.setup(DC_PIN_2, GPIO.OUT)

pwm1 = GPIO.PWM(DC_PIN_1, 1000)
pwm2 = GPIO.PWM(DC_PIN_2, 1000)
pwm1.start(0)
pwm2.start(0)

dc_state = 0
# 0 = OFF, 1 = LEFT, 2 = RIGHT

def read_adc(channel):
    # Replace this with your real ADC code
    return 128

def map_adc_to_percent(value):
    return int((value / 255) * 100)

def update_dc_motor():
    speed_raw = read_adc(0)   # potentiometer channel, adjust if needed
    speed = map_adc_to_percent(speed_raw)

    if dc_state == 0:
        pwm1.ChangeDutyCycle(0)
        pwm2.ChangeDutyCycle(0)
        print(f"DC MOTOR OFF | speed={speed}%")

    elif dc_state == 1:
        pwm1.ChangeDutyCycle(speed)
        pwm2.ChangeDutyCycle(0)
        print(f"DC MOTOR LEFT | speed={speed}%")

    elif dc_state == 2:
        pwm1.ChangeDutyCycle(0)
        pwm2.ChangeDutyCycle(speed)
        print(f"DC MOTOR RIGHT | speed={speed}%")

def toggle_dc(channel):
    global dc_state
    dc_state = (dc_state + 1) % 3
    update_dc_motor()

GPIO.add_event_detect(BTN_DC, GPIO.FALLING, callback=toggle_dc, bouncetime=250)

try:
    while True:
        update_dc_motor()
        sleep(0.2)

except KeyboardInterrupt:
    pwm1.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)
    pwm1.stop()
    pwm2.stop()
    pwm1 = None
    pwm2 = None
    GPIO.cleanup()