import RPi.GPIO as GPIO
import time
import threading

#-- Pins ---
BCD_PINS = [16, 20, 21, 26] 
LED_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.HIGH)


for pin in BCD_PINS:
    GPIO.setup(pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    
bcd_value = 0
lock = threading.Lock()

def read_bcd():
    value = 0
    for i,pin in enumerate(BCD_PINS):
        bit = 1 - GPIO.input(pin)  
        value |= bit << i
    return value
def bcd_changed(channel):
    global bcd_value 
    
    new_value = read_bcd()
    
    with lock:
        bcd_value = new_value
    
    
    if new_value <=9:
        print(f"BCD changed -> {new_value}")    
    else:
        print(f"Invalid bcd value -> {new_value}")
    
    # Read the 4 BCD inputs, combine them into one number,
# and update the shared BCD value whenever an input changes.
   
for pin in BCD_PINS:
    GPIO.add_event_detect(pin,GPIO.BOTH,callback=bcd_changed,bouncetime=50)  
    
bcd_value = read_bcd()
print(f"Start BCD value: {bcd_value}")     
try:
    while True:
        with lock:
            value = bcd_value
        if 0 <= value <=9:
            if value == 0:
                time.sleep(1)
            else:
                delay = 1/(value + 1)  
                
                for _ in range(value):
                    time.sleep(delay)
                    GPIO.output(LED_PIN,not GPIO.input(LED_PIN))
                
                time.sleep(delay)    
                
        else:
            print(f"Invalid BCD value: {value}")
            time.sleep(1)
except  KeyboardInterrupt:
    for pin in BCD_PINS:
        GPIO.remove_event_detect(pin)
    GPIO.cleanup()                   

# Watch the BCD inputs with events, store the latest BCD digit,
# and use that value to toggle the LED that many times within 1 second.            