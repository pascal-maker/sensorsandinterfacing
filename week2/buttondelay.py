import RPi.GPIO as GPIO
import time

led_pin = 17
btn = 20
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)

led_state = False
GPIO.output(led_pin, led_state)
previous_btn_state = GPIO.input(btn)
try:
    while True:
        btn_state = GPIO.input(btn)
        if previous_btn_state == 1 and btn_state == 0:
            led_state = not led_state
            GPIO.output(led_pin, led_state)
            print(f"Button pressed, LED is now {'ON' if led_state else 'OFF'}")
            #small delay to debounce the button
            time.sleep(0.05)
        previous_btn_state = btn_state
        time.sleep(0.01)
        
except KeyboardInterrupt:
    print("Exiting program")
finally:
    GPIO.cleanup()


#This script is almost the same as the previous toggle script, but it adds a debounce delay after a button press is detected.
# This helps stop one physical press from being read as multiple presses because of contact bounce.
# It still uses edge detection, so the LED only toggles when the button changes from released to pressed.    

#This script is almost the same as the previous toggle script, but it adds a debounce delay after a button press is detected. This helps stop one physical press from being read as multiple presses because of contact bounce. It still uses edge detection, so the LED only toggles when the button changes from released to pressed.


#0.05 seconds = debounce delay after a detected press

#0.01 seconds = small loop pause(to reduce CPU usage)