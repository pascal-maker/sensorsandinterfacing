import time
from RPi import GPIO
GPIO.setmode(GPIO.BCM)
led_pin = 17
btn = 20
GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(led_pin, GPIO.OUT)
n_presses = 0
led_state = 0
GPIO.output(led_pin, led_state)
previous_btn_state = GPIO.input(btn)
try:
    
    while True:
        btn_state = GPIO.input(btn)
        if previous_btn_state == 1 and btn_state == 0:
            led_state = not led_state
            GPIO.output(led_pin, led_state)
            n_presses = n_presses + 1
            print("Button pressed {} times".format(led_state))
            print('Pressed {} times'.format(n_presses))
            time.sleep(0.2)
        previous_btn_state = btn_state
        time.sleep(0.01)
except KeyboardInterrupt:
    print("ctrl +c pressed")    
finally:
    print("Cleanup") 
    GPIO.cleanup()   
            
#The script starts with the LED turned off and stores the initial button state in previous_btn_state.
# Inside the loop, it keeps reading the current button state. When the button changes from released (1) to pressed (0), the script recognizes this as a real button press.
# It then toggles the LED state, updates the LED output, and increases the press counter. 
# Finally, it saves the current button state as the new previous state for the next loop.