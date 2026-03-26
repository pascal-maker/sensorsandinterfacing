import time 
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

LED1 = 9
LED2 = 10

LED3 = 11
BUTTON_pedestrian = 21 #pedestrian button




GPIO.setup(LED1,GPIO.OUT)
GPIO.setup(LED2,GPIO.OUT)
GPIO.setup(LED3,GPIO.OUT)

GPIO.setup(BUTTON_pedestrian,GPIO.IN,pull_up_down=GPIO.PUD_UP)


#start with all lights off
GPIO.output(LED1,GPIO.LOW)
GPIO.output(LED2,GPIO.LOW)
GPIO.output(LED3,GPIO.LOW)

#start with all lights off

try:
    while True:

        GPIO.output(LED1,GPIO.HIGH)
        GPIO.output(LED2,GPIO.LOW)
        GPIO.output(LED3,GPIO.LOW)
        print("Green trafic light")
        for i in range(50):# 50 loops of 0.1 seconds = maximum 5 seconds of green
            current_button1_state = GPIO.input(BUTTON_pedestrian)#find the state of the button
            if current_button1_state == GPIO.LOW:#if the button is pressed
                print("Pedestrian button pressed")#print the state of the button
                break#exit the loop
            time.sleep(0.1)#wait for 1 second

        
            
        GPIO.output(LED1,GPIO.LOW)#turn off the green light
        GPIO.output(LED2,GPIO.HIGH) #turn on the yellow light
        GPIO.output(LED3,GPIO.LOW) #turn off the red light
        print("Yellow trafic light")
        time.sleep(1)#wait for 1 second
        GPIO.output(LED2,GPIO.LOW)#turn off the yellow light
        GPIO.output(LED3,GPIO.HIGH)  #turn on the red light
        GPIO.output(LED1,GPIO.LOW)#turn off the green light
        print("Red trafic light")
        time.sleep(4)#wait for 4 seconds



       
           
            
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
