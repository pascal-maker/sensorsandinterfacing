import RPi.GPIO as GPIO
import time 
GPIO.setmode(GPIO.BCM)
btn_1 = 20
btn_2 = 21
btn_3 = 16
btn_4 = 26
LED = 17
GPIO.setup(btn_1,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn_2,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn_3,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn_4,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED,GPIO.OUT)
mode = "off"
try:
    while True:

      if GPIO.input(btn_1) == GPIO.LOW:#we do input here because the button is connected to the ground and we are using pull up resistors
        time.sleep(0.05)
        print("Led on")
        mode = "on"

      elif GPIO.input(btn_2) == GPIO.LOW:
        time.sleep(0.05)
        print(" Led off")    
        mode = "off"

      elif GPIO.input(btn_3) == GPIO.LOW:
        time.sleep(0.2)
        mode = "blink faster"
        
      elif GPIO.input(btn_4) == GPIO.LOW:
        time.sleep(0.2)
        mode = "blink slower"

      if mode == "on":
        GPIO.output(LED,GPIO.HIGH)
      elif mode == "off":
        GPIO.output(LED,GPIO.LOW)
      elif mode == "blink faster":
        GPIO.output(LED, not GPIO.input(LED))
        print("blink faster button pressed")
        #we want to toogle so we take the opposite of the current state not led _state is always for toggling
        time.sleep(0.1)
      elif mode == "blink slower":
        print("blink slower button pressed")
        GPIO.output(LED, not GPIO.input(LED))#we want to toogle so we take the opposite of the current state not led _state is always for toggling
        time.sleep(0.5)
        

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
   
