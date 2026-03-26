import RPi.GPIO as GPIO
import time
BUTTON_1 = 20
BUTTON_2 = 21   
BUTTON_3  = 16
BUTTON_4 = 26
LED = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_1,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_2,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_3,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_4,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED,GPIO.OUT)
mode = "off"
try:
    while True:

      if GPIO.input(BUTTON_1) == GPIO.LOW:#we do input here because the button is connected to the ground and we are using pull up resistors
        time.sleep(0.05)
        print("Led on")
        mode = "on"

      elif GPIO.input(BUTTON_2) == GPIO.LOW:
        time.sleep(0.05)
        print(" Led off")    
        mode = "off"

      elif GPIO.input(BUTTON_3) == GPIO.LOW:
        time.sleep(0.2)
        mode = "blink faster"
        
      elif GPIO.input(BUTTON_4) == GPIO.LOW:
        time.sleep(0.2)
        mode = "blink slower"

      if mode == "on":
        GPIO.output(LED,GPIO.HIGH)
      elif mode == "off":
        GPIO.output(LED,GPIO.LOW)
      elif mode == "blink faster":
        GPIO.output(LED, not GPIO.input(LED))#we want to toogle so we take the opposute of the current state
        time.sleep(0.1)
      elif mode == "blink slower":
        GPIO.output(LED, not GPIO.input(LED))#we want to toogle so we take the opposute of the current state
        time.sleep(0.5)
        

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
   




