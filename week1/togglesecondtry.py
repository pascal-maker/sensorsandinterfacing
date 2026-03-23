import time
from RPi import GPIO

GPIO.setmode(GPIO.BCM)
btn = 20
led = 17
previous_state = GPIO.HIGH
led_state = False

GPIO.setup(btn,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(led,GPIO.OUT)

try:
    while True:
        current_state  = GPIO.input(btn) # Read the current state of the button
        if current_state == GPIO.LOW and previous_state == GPIO.HIGH:#check if the button is pressed and was previously not pressed
            led_state = not led_state # Toggle the LED state
            GPIO.output(led,led_state)  # Update the LED with the new state
            print('The value of pin {0} is {1}'.format(btn,current_state)) 
        previous_state = current_state# Update the previous state for the next iteration
        time.sleep(0.5)
        
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()