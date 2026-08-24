import time

import RPi.GPIO as GPIO
import smbus


# GPIO pin numbers use BCM numbering, not the physical header pin numbers.
# Each RGB LED color has its own GPIO pin so that it can be controlled with PWM.
R_PIN = 5
G_PIN = 6
B_PIN = 13
BUTTON_PIN = 20

# The ADS7830 converts each potentiometer's analogue voltage into an 8-bit
# digital value between 0 and 255. It is connected to I2C address 0x48.
ADC_ADDRESS = 0x48

# These commands select ADS7830 inputs AIN2, AIN3, and AIN4. The ADS7830 does
# not store its channel-selection bits in normal numerical order, so using
# 0x84 | (channel << 4) would select the wrong inputs for some channels. Using
# the correct commands explicitly makes each potentiometer select the intended
# red, green, or blue LED segment.
ADC_COMMANDS = [0x94, 0xD4, 0xA4]

# VREF is the ADC's maximum reference voltage. The potentiometer produces an
# analogue voltage between approximately 0 V and 3.3 V, and the ADC represents
# that voltage as a number from 0 to 255. VREF is only needed to convert that
# number back into volts for the terminal output; PWM can use the raw value.
VREF = 3.3

# A high PWM frequency prevents visible LED flickering.
PWM_FREQUENCY = 1000

# This is a common-anode RGB LED, so its PWM values work in reverse:
# 0% duty cycle is fully lit and 100% duty cycle is completely off.
# Limiting the duty cycle to 95% means the LED always has a faint glow.
MAX_DUTY = 95


def read_adc(bus, command):
    """Return an ADS7830 channel's raw value and calculated voltage."""
    # Tell the ADC which input channel should be converted.
    bus.write_byte(ADC_ADDRESS, command)

    # The first byte can still belong to the previous conversion, so discard it
    # and use the following byte as the current potentiometer measurement.
    bus.read_byte(ADC_ADDRESS)  # Discard the previous conversion result.
    raw_value = bus.read_byte(ADC_ADDRESS)

    # Scale the 0-255 ADC reading to an estimated voltage between 0 and VREF:
    #   0   means approximately 0 V
    #   255 means approximately 3.3 V
    # This voltage is printed for information and is not needed to control PWM.
    voltage = raw_value * VREF / 255
    return raw_value, voltage


def adc_to_duty(raw_value):
    """Convert an ADC value to common-anode PWM without turning fully off."""
    # Invert the value because a common-anode LED becomes brighter when the
    # duty cycle becomes lower.
    inverted_duty = 100 - (raw_value * 100 / 255)

    # Never return more than 95%, otherwise the segment could be fully off.
    return min(inverted_duty, MAX_DUTY)


def main():
    # Select BCM numbering and configure the button with an internal pull-up.
    # The input normally reads HIGH and becomes LOW when the button is pressed.
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Configure all three RGB LED connections as outputs.
    for pin in (R_PIN, G_PIN, B_PIN):
        GPIO.setup(pin, GPIO.OUT)

    # Create one independent PWM controller for each LED color.
    pwm_r = GPIO.PWM(R_PIN, PWM_FREQUENCY)
    pwm_g = GPIO.PWM(G_PIN, PWM_FREQUENCY)
    pwm_b = GPIO.PWM(B_PIN, PWM_FREQUENCY)
    pwms = (pwm_r, pwm_g, pwm_b)

    # Start each PWM channel at the faint-glow level.
    for pwm in pwms:
        pwm.start(MAX_DUTY)

    # Open I2C bus 1, which is the standard Raspberry Pi I2C bus.
    bus = smbus.SMBus(1)

    # This Boolean stores whether the potentiometers currently control the LED.
    system_on = True

    # Remember whether event detection was installed so cleanup remains safe if
    # an error occurs before GPIO.add_event_detect finishes.
    event_added = False

    def toggle_system(channel):
        """Toggle the system when the button generates a falling-edge event."""
        nonlocal system_on
        # This callback runs automatically whenever the button is pressed.
        # The channel argument is supplied by RPi.GPIO but is not needed here.
        system_on = not system_on
        print("System ON" if system_on else "System OFF")

    try:
        # Register an event instead of repeatedly polling the button. A falling
        # edge occurs when the pull-up input changes from HIGH to LOW.
        GPIO.add_event_detect(
            BUTTON_PIN,
            GPIO.FALLING,
            callback=toggle_system,
            # Ignore extra electrical transitions caused by button bounce.
            bouncetime=200,
        )
        event_added = True

        while True:
            if system_on:
                # Read all three potentiometers. Each item contains its raw ADC
                # value and its calculated voltage.
                readings = [
                    read_adc(bus, command) for command in ADC_COMMANDS
                ]

                # Match the three readings to red, green, and blue PWM.
                for pwm, (raw_value, _) in zip(pwms, readings):
                    pwm.ChangeDutyCycle(adc_to_duty(raw_value))

                # Display the readings so they can also be checked in a terminal.
                (red, vr), (green, vg), (blue, vb) = readings
                print(
                    f"R: {red:3d} ({vr:.2f} V)  "
                    f"G: {green:3d} ({vg:.2f} V)  "
                    f"B: {blue:3d} ({vb:.2f} V)"
                )
            else:
                # The system is off, but 95% duty keeps each color faintly lit.
                for pwm in pwms:
                    pwm.ChangeDutyCycle(MAX_DUTY)

            # A short pause reduces CPU and I2C usage while remaining responsive.
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nProgram stopped.")

    finally:
        # Always release hardware resources, even after an error or Ctrl+C.
        if event_added:
            GPIO.remove_event_detect(BUTTON_PIN)
        for pwm in pwms:
            pwm.stop()
        bus.close()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
