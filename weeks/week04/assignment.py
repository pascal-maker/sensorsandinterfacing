import time

import RPi.GPIO as GPIO
import smbus


# RGB LED and button GPIO pins (BCM numbering).
R_PIN = 5
G_PIN = 6
B_PIN = 13
BUTTON_PIN = 20

# ADS7830 address and commands for potentiometers on AIN2, AIN3, and AIN4.
ADC_ADDRESS = 0x48
ADC_COMMANDS = [0x94, 0xD4, 0xA4]
VREF = 3.3

PWM_FREQUENCY = 1000

# This is a common-anode RGB LED. A duty cycle of 100% is completely off,
# so limiting it to 95% ensures that every segment retains a faint glow.
MAX_DUTY = 95


def read_adc(bus, command):
    """Return an ADS7830 channel's raw value and calculated voltage."""
    bus.write_byte(ADC_ADDRESS, command)
    bus.read_byte(ADC_ADDRESS)  # Discard the previous conversion result.
    raw_value = bus.read_byte(ADC_ADDRESS)
    voltage = raw_value * VREF / 255
    return raw_value, voltage


def adc_to_duty(raw_value):
    """Convert an ADC value to common-anode PWM without turning fully off."""
    inverted_duty = 100 - (raw_value * 100 / 255)
    return min(inverted_duty, MAX_DUTY)


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    for pin in (R_PIN, G_PIN, B_PIN):
        GPIO.setup(pin, GPIO.OUT)

    pwm_r = GPIO.PWM(R_PIN, PWM_FREQUENCY)
    pwm_g = GPIO.PWM(G_PIN, PWM_FREQUENCY)
    pwm_b = GPIO.PWM(B_PIN, PWM_FREQUENCY)
    pwms = (pwm_r, pwm_g, pwm_b)

    # Start with the dim glow used for the system's off state.
    for pwm in pwms:
        pwm.start(MAX_DUTY)

    bus = smbus.SMBus(1)
    system_on = True
    event_added = False

    def toggle_system(channel):
        """Toggle the system when the button generates a falling-edge event."""
        nonlocal system_on
        system_on = not system_on
        print("System ON" if system_on else "System OFF")

    try:
        # The pull-up button creates a falling edge when pressed.
        GPIO.add_event_detect(
            BUTTON_PIN,
            GPIO.FALLING,
            callback=toggle_system,
            bouncetime=200,
        )
        event_added = True

        while True:
            if system_on:
                readings = [
                    read_adc(bus, command) for command in ADC_COMMANDS
                ]

                for pwm, (raw_value, _) in zip(pwms, readings):
                    pwm.ChangeDutyCycle(adc_to_duty(raw_value))

                (red, vr), (green, vg), (blue, vb) = readings
                print(
                    f"R: {red:3d} ({vr:.2f} V)  "
                    f"G: {green:3d} ({vg:.2f} V)  "
                    f"B: {blue:3d} ({vb:.2f} V)"
                )
            else:
                # Keep all three segments faintly illuminated while off.
                for pwm in pwms:
                    pwm.ChangeDutyCycle(MAX_DUTY)

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nProgram stopped.")

    finally:
        if event_added:
            GPIO.remove_event_detect(BUTTON_PIN)
        for pwm in pwms:
            pwm.stop()
        bus.close()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
