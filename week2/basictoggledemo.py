import RPi.GPIO as GPIO
import time
LED = 17
BTN = 20
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
led_state = False
GPIO.output(LED, led_state)
previous_btn_state = GPIO.input(BTN)
try:
    while True:
        current_state = GPIO.input(BTN)
        if previous_btn_state == 1 and current_state == 0:
            led_state = not led_state
            GPIO.output(LED, led_state)
            print(f"Led is now {'ON' if led_state else 'OFF'}")
            time.sleep(0.05) #debounce delay
        previous_btn_state = current_state
        time.sleep(0.01)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()