import time
from RPi import GPIO

# Use BCM GPIO numbering
GPIO.setmode(GPIO.BCM)

# Button and LED pin numbers
btn_bottom = 21
btn_top = 20
btn_right = 16
btn_left = 26
led = 17

# Start mode and LED state
mode = "off"
led_state = False
last_toggle_time = time.time()

# Set all buttons as input with internal pull-up resistor
GPIO.setup(btn_bottom, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn_top, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn_left, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn_right, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set LED as output
GPIO.setup(led, GPIO.OUT)

try:
    while True:
        # -----------------------------
        # Check which button is pressed
        # -----------------------------
        # With pull-up:
        # pressed = LOW
        # released = HIGH

        if GPIO.input(btn_bottom) == GPIO.LOW:
            mode = "off"      # bottom button -> LED off

        elif GPIO.input(btn_top) == GPIO.LOW:
            mode = "on"       # top button -> LED always on

        elif GPIO.input(btn_left) == GPIO.LOW:
            mode = "slow"     # left button -> slow blinking

        elif GPIO.input(btn_right) == GPIO.LOW:
            mode = "fast"     # right button -> fast blinking

        # -----------------------------
        # LED behavior based on mode
        # -----------------------------
        if mode == "off":
            GPIO.output(led, GPIO.LOW)   # turn LED off

        elif mode == "on":
            GPIO.output(led, GPIO.HIGH)  # turn LED on

        elif mode == "slow":
            # Blink only every 0.5 seconds
            if time.time() - last_toggle_time >= 0.5:
                led_state = not led_state           # change on to off, or off to on
                GPIO.output(led, led_state)         # update LED
                last_toggle_time = time.time()      # remember when we toggled

        elif mode == "fast":
            # Blink only every 0.1 seconds
            if time.time() - last_toggle_time >= 0.1:
                led_state = not led_state           # change on to off, or off to on
                GPIO.output(led, led_state)         # update LED
                last_toggle_time = time.time()      # remember when we toggled

        # Small pause so the loop does not run too fast
        time.sleep(0.05)

except KeyboardInterrupt:
    # Stop program with Ctrl+C
    pass

finally:
    # Reset GPIO pins neatly when program ends
    GPIO.cleanup()