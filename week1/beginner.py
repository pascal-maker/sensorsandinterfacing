from RPi import GPIO
import time
btn = 20
led = 17
previous_state = 1 # 1 means button is not pressed
led_state = False # False means LED is OFF
GPIO.setmode(GPIO.BCM)

GPIO.setup(btn,GPIO.IN ,pull_up_down=GPIO.PUD_UP)

GPIO.setup(led,GPIO.OUT)

try:
    while True:
                current_state = GPIO.input(btn)# 0 means button is pressed
               
                if previous_state ==1 and current_state == 0:# button is pressed
                    led_state = not led_state
                    if led_state:
                        print("LED is ON")
                        GPIO.output(led,GPIO.HIGH)
                    else:
                        print("LED is OFF")
                        GPIO.output(led,GPIO.LOW)
                previous_state = current_state
                time.sleep(0.1)
                

     
    
finally:
    GPIO.cleanup()    
    
  
        
    