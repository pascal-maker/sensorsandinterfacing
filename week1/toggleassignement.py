from RPi import GPIO
import time 
btn = 20 
led = 17
GPIO.setmode(GPIO.BCM)

GPIO.setup(btn,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(led,GPIO.OUT)

previous_value = GPIO.input(btn) # read the value

try:
    while True:
        current_value = GPIO.input(btn)
        if previous_value == GPIO.HIGH and current_value == GPIO.LOW:# if the value changes from high to low from not off to on  GPIO.high means off and GPIO.low means on
            print("Turn on led")
            GPIO.output(led,not previous_value)
            time.sleep(0.01)
        elif previous_value == GPIO.LOW and current_value == GPIO.HIGH:# if the value changes from low to high from on to off GPIO.low means on and GPIO.high means off
            print("Turn off LED")
            GPIO.output(led,not previous_value)
            time.sleep(0.01)
        previous_value = current_value    # update the previous value
except KeyboardInterrupt:            
    pass
finally:
    GPIO.cleanup()


            

        




