from RPi import GPIO
import time

btn_1 = 20
btn_2 = 21
btn_3 = 26
btn_4 = 16
buttons = [btn_1, btn_2, btn_3, btn_4]
led = 17
mode = "off"

GPIO.setmode(GPIO.BCM)

for btn in buttons:#setup the buttons
    GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setup the buttons

GPIO.setup(led, GPIO.OUT)#setup the led

try:
    while True:
        # 1. Kijk of een knop is ingedrukt en pas mode aan
        for btn in buttons:
            state = GPIO.input(btn)

            if state == 0:#if the button is pressed
                if btn == btn_1:#if the first button is pressed
                    mode = "off"
                    print("LED OFF")
                elif btn == btn_2:#if the second button is pressed
                    mode = "on"
                    print("LED ON")
                elif btn == btn_3:#if the third button is pressed
                    mode = "blink_slow"
                    print("Blink slow")
                elif btn == btn_4:#if the fourth button is pressed
                    mode = "blink_fast"
                    print("Blink fast")

        # 2. Voer de huidige mode uit
        if mode == "off":#if the mode is off
            GPIO.output(led, GPIO.LOW)
            time.sleep(0.01)

        elif mode == "on":#if the mode is on
            GPIO.output(led, GPIO.HIGH)
            time.sleep(0.01)

        elif mode == "blink_slow":#if the mode is blink_slow
            GPIO.output(led, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(led, GPIO.LOW)
            time.sleep(0.5)

        elif mode == "blink_fast":#if the mode is blink_fast
            GPIO.output(led, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(led, GPIO.LOW)
            time.sleep(0.1)

finally:
    GPIO.cleanup()