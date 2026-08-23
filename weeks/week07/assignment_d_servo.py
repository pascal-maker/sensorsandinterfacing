"""Assignment D: toggle a joystick-controlled servo with GPIO 26."""

# Path and sys make the repository's shared hardware package importable.
from pathlib import Path
import sys
import time

import RPi.GPIO as GPIO

# This script is in weeks/week07, two directories below the repository root.
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from hardware import ADS7830, ServoMotor

# GPIO 26 toggles control; ADS7830 channel 6 is the joystick X-axis.
BUTTON_PIN = 26
JOYSTICK_X_CHANNEL = 6
servo_enabled = False


def toggle_servo(channel):
    """Toggle joystick control once for each debounced button press."""
    global servo_enabled
    servo_enabled = not servo_enabled


def main():
    # Use Broadcom GPIO numbering and the Pi's internal button pull-up.
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # The ADC returns joystick position as an integer from 0 through 255.
    adc = ADS7830(address=0x48)
    # A hobby servo uses 50 Hz PWM; pulse limits define its useful angle range.
    servo = ServoMotor(pin=18, min_pulse_ms=0.6, max_pulse_ms=2.4)

    # FALLING means the active-low button has just been pressed.
    GPIO.add_event_detect(
        BUTTON_PIN, GPIO.FALLING, callback=toggle_servo, bouncetime=200
    )
    try:
        while True:
            if servo_enabled:
                # Map the full joystick range linearly onto 0 through 180 degrees.
                raw_value = adc.read_raw(JOYSTICK_X_CHANNEL)
                angle = raw_value / 255 * 180
                # Keep PWM active so the servo follows continuous joystick motion.
                duty_cycle = servo.set_angle(angle, move_time=0, release=False)
                print(
                    f"SERVO ON | ADC: {raw_value:3} | Angle: {angle:5.1f}° | "
                    f"Duty cycle: {duty_cycle:4.1f}%"
                )
            else:
                # A zero duty cycle stops sending pulses and reduces servo jitter.
                servo.release()
                print("SERVO OFF")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nServo stopped")
    finally:
        # Stop PWM before releasing I2C and all GPIO resources.
        servo.close()
        adc.close()
        GPIO.cleanup()


# Run only when executed directly, not when imported by another script.
if __name__ == "__main__":
    main()
