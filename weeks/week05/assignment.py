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


SERVO_PIN = 18
BUTTON_PIN = 20
POTENTIOMETER_CHANNEL = 4
ADC_ADDRESS = 0x48
LCD_ADDRESS = 0x27


def adc_value_to_angle(value):
    """Map the complete 8-bit ADC range to the servo's 0-to-180° range."""
    value = max(0, min(255, int(value)))
    return round(value * 180 / 255)


def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    adc = ADS7830(address=ADC_ADDRESS)
    lcd = LCD(address=LCD_ADDRESS)
    servo = ServoMotor(SERVO_PIN)
    button = Button(BUTTON_PIN, bouncetime=200)

    state_lock = threading.Lock()
    system_on = True

    def toggle_system(_button):
        nonlocal system_on
        with state_lock:
            system_on = not system_on
            active = system_on
        print("System ON" if active else "System OFF")

    button.when_pressed(toggle_system)
    previous_angle = None
    previous_active = None

    try:
        while True:
            with state_lock:
                active = system_on

            if active:
                adc_value = adc.read_raw(POTENTIOMETER_CHANNEL)
                angle = adc_value_to_angle(adc_value)

                if angle != previous_angle:
                    duty = servo.set_angle(angle)
                    previous_angle = angle
                else:
                    duty = servo.angle_to_duty_cycle(angle)

                lcd.write(f"Analog: {adc_value:3d}", f"Angle: {angle:3d} deg")
                print(f"ADC: {adc_value:3d} | Angle: {angle:3d}° | Duty: {duty:.2f}%")
            elif previous_active is not False:
                servo.release()
                lcd.write("System OFF", "")

            previous_active = active
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
    finally:
        button.close()
        servo.close()
        lcd.close(clear=True)
        adc.close()
        GPIO.cleanup()
        print("Cleanup complete")


if __name__ == "__main__":
    main()
