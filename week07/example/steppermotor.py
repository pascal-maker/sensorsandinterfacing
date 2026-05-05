from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)  # use Broadcom GPIO numbering

# the 4 GPIO pins connected to IN1-IN4 of the stepper driver board (e.g. ULN2003)
pins = (19, 13, 6, 5)
GPIO.setup(pins, GPIO.OUT)  # configure all four pins as outputs

# half-step sequence: each tuple activates a combination of coils
# cycling through these 8 patterns in order rotates the shaft forward one full step-cycle
STEP_DELAY = 0.002  # seconds per step — 28BYJ-48 needs at least 2 ms to track reliably

steps = (
    (1, 0, 0, 0),  # coil 1 only
    (1, 1, 0, 0),  # coils 1 and 2
    (0, 1, 0, 0),  # coil 2 only
    (0, 1, 1, 0),  # coils 2 and 3
    (0, 0, 1, 0),  # coil 3 only
    (0, 0, 1, 1),  # coils 3 and 4
    (0, 0, 0, 1),  # coil 4 only
    (1, 0, 0, 1),  # coils 4 and 1
)

try:
    # --- forward rotation ---
    # repeat the full step sequence 512 times to complete roughly one revolution
    for n in range(512):#
        for step in steps:                      # apply each coil pattern in order
            for i in range(4):
                GPIO.output(pins[i], step[i])  # drive each pin high or low
            sleep(STEP_DELAY)                        # delay between steps controls speed

    # --- reverse rotation ---
    # walk the same step sequence backwards to reverse the shaft direction
    for n in range(512):
        for step in reversed(steps):            # reverse order = reverse direction
            for i in range(4):
                GPIO.output(pins[i], step[i])
            sleep(STEP_DELAY)

    print("Stepper motor stopped")

except KeyboardInterrupt:
    print("Stepper motor stopped by user")

finally:
    GPIO.cleanup()  # release all GPIO pins regardless of how the script exits
