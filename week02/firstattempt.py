from RPi import GPIO
import time
GPIO.setmode(GPIO.BCM)

btn = 20
led = 17

GPIO.setup(btn,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(led,GPIO.OUT)

led_state = False #led staat altijd uit eerst
previous_state = GPIO.HIGH # als in de vorige state de knop stond ingedrukt
GPIO.output(led,led_state)
try:
    while True:
        current_state = GPIO.input(btn)
        if current_state == GPIO.LOW and previous_state == GPIO.HIGH:#als de cureent status zegt knop ingedrukt en vorige status  knop  ingedruktstond en 
            led_state = not led_state#dan gaat het led niet aan
            GPIO.output(led,led_state)  # Toggle the LED state
            # If it was off, turn it on
            # If it was on, turn it off
            print("LED toggled to",led_state)
            time.sleep(0.05)
        
        previous_state = current_state
        time.sleep(0.1)    
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()    