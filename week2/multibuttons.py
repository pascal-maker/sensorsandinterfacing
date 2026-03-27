import time 
import RPI.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

LED1 = 9
LED2 = 10

LED3 = 11

BUTTON1 = 20

BUTTON2 = 21

GPIO.setup(LED1,GPIO.OUT)
GPIO.setup(LED2,GPIO.OUT)
GPIO.setup(LED3,GPIO.OUT)

GPIO.setup(BUTTON1,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON2,GPIO.IN,pull_up_down=GPIO.PUD_UP)

state = 0 #store the state we are in
previous_button1_state = GPIO.HIGH#store the previous state of button 1

GPIO.output(LED1,GPIO.LOW)
GPIO.output(LED2,GPIO.LOW)
GPIO.output(LED3,GPIO.LOW)

try:
    while True:
        current_button1_state = GPIO.input(BUTTON1)
        current_button2_state = GPIO.input(BUTTON2)

        if current_button2_state == GPIO.LOW:#if button 2 is pressed, turn on all leds
            all_leds_state = GPIO.input(LED1)
            GPIO.output(LED1,all_leds_state)
            GPIO.output(LED2,all_leds_state)
            GPIO.output(LED3,all_leds_state)
            time.sleep(0.1)
        else:
            if previous_button1_state == GPIO.HIGH and current_button1_state == GPIO.LOW:#if button was not pressed and now it is pressed
                state += 1#increment the state
                if state > 3:#if the state is greater than 3, reset it to 0
                    state = 0
                time.sleep(0.2)
            previous_button1_state = current_button1_state#store the previous state of button 1
            GPIO.output(LED1,GPIO.LOW)#turn off all leds
            GPIO.output(LED2,GPIO.LOW)
            GPIO.output(LED3,GPIO.LOW)
            if state == 1:#if the state is 1, turn on led 1
                GPIO.output(LED1,GPIO.HIGH)
            elif state == 2:#if the state is 2, turn on led 2
                GPIO.output(LED2,GPIO.HIGH)
            elif state == 3:#if the state is 3, turn on led 3
                GPIO.output(LED3,GPIO.HIGH)
            elif state == 4:#if the state is 4, turn off all leds
                GPIO.output(LED1,GPIO.LOW)
                GPIO.output(LED2,GPIO.LOW)
                GPIO.output(LED3,GPIO.LOW)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
