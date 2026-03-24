from RPi import GPIO
import time

btn_1 = 20
btn_2 = 21

led_1 = 9
led_2 = 10
led_3 = 11

GPIO.setmode(GPIO.BCM)

GPIO.setup(btn_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(led_1, GPIO.OUT)
GPIO.setup(led_2, GPIO.OUT)
GPIO.setup(led_3, GPIO.OUT)

step = 0                  # 0 = all off, 1 = led1, 2 = led2, 3 = led3
previous_btn1_state = 1   # pull-up: not pressed = 1
blink_state = False

try:
    while True:
        btn1_state = GPIO.input(btn_1)
        btn2_state = GPIO.input(btn_2)

        # BUTTON 2: while held, blink all LEDs together
        if btn2_state == 0:
            blink_state = not blink_state

            if blink_state:
                GPIO.output(led_1, GPIO.HIGH)
                GPIO.output(led_2, GPIO.HIGH)
                GPIO.output(led_3, GPIO.HIGH)
            else:
                GPIO.output(led_1, GPIO.LOW)
                GPIO.output(led_2, GPIO.LOW)
                GPIO.output(led_3, GPIO.LOW)

            time.sleep(0.2)

        else:
            # when button 2 is released, all LEDs off
            GPIO.output(led_1, GPIO.LOW)
            GPIO.output(led_2, GPIO.LOW)
            GPIO.output(led_3, GPIO.LOW)

            # BUTTON 1: detect one clean press with edge detection
            if previous_btn1_state == 1 and btn1_state == 0:
                step += 1

                if step == 1:
                    GPIO.output(led_1, GPIO.HIGH)
                    GPIO.output(led_2, GPIO.LOW)
                    GPIO.output(led_3, GPIO.LOW)
                    print("LED 1 ON")

                elif step == 2:
                    GPIO.output(led_1, GPIO.LOW)
                    GPIO.output(led_2, GPIO.HIGH)
                    GPIO.output(led_3, GPIO.LOW)
                    print("LED 2 ON")

                elif step == 3:
                    GPIO.output(led_1, GPIO.LOW)
                    GPIO.output(led_2, GPIO.LOW)
                    GPIO.output(led_3, GPIO.HIGH)
                    print("LED 3 ON")

                elif step == 4:
                    GPIO.output(led_1, GPIO.LOW)
                    GPIO.output(led_2, GPIO.LOW)
                    GPIO.output(led_3, GPIO.LOW)
                    print("ALL LEDS OFF")
                    step = 0

                time.sleep(0.05)  # debounce

            previous_btn1_state = btn1_state
            time.sleep(0.01)

except KeyboardInterrupt:
    print("Stopped with Ctrl+C")

finally:
    GPIO.cleanup()
    print("GPIO cleaned up")