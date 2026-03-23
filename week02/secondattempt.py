from RPi import GPIO
import time

GPIO.setmode(GPIO.BCM)

btn1 = 20
btn2 = 21

led1 = 9
led2 = 10
led3 = 11

# State for button 1 cycle
mode = 0#whichledisactif
previous_state_btn1 = GPIO.HIGH#edgedetction
show_mode = False#nietconstantopnieuwprinten

# State for button 2 blinking
all_blink_state = False#blinkaanblinkuit
last_toggle_time = time.time()#blinktsnelheid
btn2_was_pressed = False#loslatenherkennen

GPIO.setup(btn1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(led1, GPIO.OUT)
GPIO.setup(led2, GPIO.OUT)
GPIO.setup(led3, GPIO.OUT)

def set_all(a, b, c):
    GPIO.output(led1, a)
    GPIO.output(led2, b)
    GPIO.output(led3, c)

try:
    while True:
        # Button 1: edge detection
        current_state_btn1 = GPIO.input(btn1)

        if current_state_btn1 == GPIO.LOW and previous_state_btn1 == GPIO.HIGH:#nieuwedruk
            mode = (mode + 1) % 4#volgendestapindecyclus
            show_mode = True#erietsvernadert
            print("Button 1 pressed -> mode =", mode)
            time.sleep(0.05)  # small debounce

        previous_state_btn1 = current_state_btn1

        # Button 2: while held, blink all LEDs together
        if GPIO.input(btn2) == GPIO.LOW:#button2wordtvastgehuden
            if not btn2_was_pressed:#onthoudtofhijactiefwas
                print("Button 2 pressed -> blinking all LEDs")

            btn2_was_pressed = True

            if time.time() - last_toggle_time >= 0.2:#tijdopmonieuwteknipperen
                all_blink_state = not all_blink_state#wisseltussenaanenuit
                set_all(all_blink_state, all_blink_state, all_blink_state)#zetalleledstegelijkaan
                print("All LEDs blink state:", all_blink_state)
                last_toggle_time = time.time()

        else:
            # Button 2 was just released
            if btn2_was_pressed:#detecteertloslatenenzetalesuit
                set_all(GPIO.LOW, GPIO.LOW, GPIO.LOW)
                btn2_was_pressed = False
                show_mode = False
                print("Button 2 released -> all LEDs off")

            # Normal mode display from button 1
            elif show_mode:
                if mode == 0:
                    set_all(GPIO.LOW, GPIO.LOW, GPIO.LOW)
                    print("Mode 0 -> all LEDs off")

                elif mode == 1:
                    set_all(GPIO.HIGH, GPIO.LOW, GPIO.LOW)
                    print("Mode 1 -> LED1 on")

                elif mode == 2:
                    set_all(GPIO.LOW, GPIO.HIGH, GPIO.LOW)
                    print("Mode 2 -> LED2 on")

                elif mode == 3:
                    set_all(GPIO.LOW, GPIO.LOW, GPIO.HIGH)
                    print("Mode 3 -> LED3 on")

                show_mode = False  # stop printing same mode every loop

        time.sleep(0.01)

except KeyboardInterrupt:
    print("Program stopped")

finally:
    GPIO.cleanup()