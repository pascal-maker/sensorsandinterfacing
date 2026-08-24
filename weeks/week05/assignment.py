"""Week 5: control a servo with potentiometer A4 and show values on an LCD."""

from pathlib import Path
import sys
import threading
import time

import RPi.GPIO as GPIO

# Support direct execution from the repository root and module execution.
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from hardware import ADS7830, Button, LCD, ServoMotor


# =========================================================
# HARDWARE SETTINGS
# =========================================================

# BCM pin numbers used for the servo signal and push button.
SERVO_PIN = 18
BUTTON_PIN = 20

# The potentiometer is connected to analog input A4 of the ADS7830.
POTENTIOMETER_CHANNEL = 4

# Default I2C addresses of the ADS7830 ADC and PCF8574 LCD backpack.
ADC_ADDRESS = 0x48
LCD_ADDRESS = 0x27


def adc_value_to_angle(value):
    """Map the complete 8-bit ADC range to the servo's 0-to-180° range."""
    # Clamp unexpected values so the requested servo angle always remains safe.
    value = max(0, min(255, int(value)))

    # ADC 0 becomes 0°, ADC 255 becomes 180°, and values between are linear.
    return round(value * 180 / 255)


def main():
    # Use Broadcom GPIO numbering, matching SERVO_PIN and BUTTON_PIN above.
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # Each class performs the low-level setup for one hardware component.
    adc = ADS7830(address=ADC_ADDRESS)
    lcd = LCD(address=LCD_ADDRESS)
    servo = ServoMotor(SERVO_PIN)
    button = Button(BUTTON_PIN, bouncetime=200)

    # The GPIO button callback can run while the main loop is reading this
    # value. A lock prevents both pieces of code from changing it together.
    state_lock = threading.Lock()
    system_on = True

    def toggle_system(_button):
        """Switch the complete system on or off after a button press."""
        nonlocal system_on
        with state_lock:
            system_on = not system_on
            active = system_on
        print("System ON" if active else "System OFF")

    # Register the function above as the debounced button-press callback.
    button.when_pressed(toggle_system)

    # Remember the last state so hardware is updated only when necessary.
    previous_angle = None
    previous_active = None

    try:
        while True:
            with state_lock:
                active = system_on

            if active:
                # Read A4 as a number from 0 through 255 and convert it to an
                # angle covering the servo's complete 0-to-180-degree range.
                adc_value = adc.read_raw(POTENTIOMETER_CHANNEL)
                angle = adc_value_to_angle(adc_value)

                # Moving only when the angle changes reduces servo jitter and
                # avoids blocking for the servo movement delay unnecessarily.
                if angle != previous_angle:
                    duty = servo.set_angle(angle)
                    previous_angle = angle
                else:
                    duty = servo.angle_to_duty_cycle(angle)

                # The LCD driver pads both rows to 16 characters, clearing any
                # characters left from the previous update.
                lcd.write(f"Analog: {adc_value:3d}", f"Angle: {angle:3d} deg")
                print(f"ADC: {adc_value:3d} | Angle: {angle:3d}° | Duty: {duty:.2f}%")
            elif previous_active is not False:
                # Perform these actions once when the system changes to off.
                servo.release()
                lcd.write("System OFF", "")

            previous_active = active

            # Limit I2C traffic and CPU usage to roughly ten updates per second.
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
    finally:
        # Always release PWM, I2C, event detection, and GPIO resources—even if
        # the program is stopped with Ctrl+C or encounters an error.
        button.close()
        servo.close()
        lcd.close(clear=True)
        adc.close()
        GPIO.cleanup()
        print("Cleanup complete")


if __name__ == "__main__":
    main()
