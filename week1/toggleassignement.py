import RPi.GPIO as GPIO
import time
BUTTON = 20
LED = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON,GPIO.IN,pull_up_down=GPIO.PUD_UP)

previous_state = GPIO.HIGH#beforetheloop starts, we assume the button is not pressed
#with PUD_UP, a button that is not pressed reads HIGH
led_state = GPIO.LOW#the led starts as off

try:
    while True:
        current_state = GPIO.input(BUTTON)#read the button state
        if current_state == GPIO.LOW and previous_state == GPIO.HIGH:#detects a falling edge    # Detect a falling edge:
    # the button was not pressed before (HIGH)
    # and is now pressed (LOW).
    # So this is a new button press.
    # Toggle the LED state and update the LED output.
            led_state = not led_state#toggle the led state
            GPIO.output(LED,led_state)#update the led
        previous_state = current_state
        time.sleep(0.01)
except KeyboardInterrupt:
    pass
finally:
    

  
        
    
