"""
Week 4 — PWM & ADC
Classes: PWMLed, ADS7830, RGBLed
"""

import RPi.GPIO as GPIO
import smbus
import time


class PWMLed:
    """Single LED controlled via PWM (0–100 % brightness)."""

    def __init__(self, pin, frequency=1000):
        GPIO.setup(pin, GPIO.OUT)
        self._pwm = GPIO.PWM(pin, frequency)
        self._pwm.start(0)

    def set_brightness(self, percent):
        """Set brightness 0–100 %."""
        percent = max(0, min(100, percent))
        self._pwm.ChangeDutyCycle(percent)

    def stop(self):
        self._pwm.stop()


class ADS7830:
    """
    Driver for the ADS7830 8-channel, 8-bit ADC over I2C.
    Default I2C address: 0x48.
    VREF: 5.0 V.
    """

    _CHANNEL_COMMANDS = {
        0: 0x84, 1: 0xC4,
        2: 0x94, 3: 0xD4,
        4: 0xA4, 5: 0xE4,
        6: 0xB4, 7: 0xF4,
    }

    def __init__(self, address=0x48, bus_num=1, vref=5.0):
        self.address = address
        self.vref = vref
        self._bus = smbus.SMBus(bus_num)

    def read_raw(self, channel):
        """Return raw ADC value (0–255) for the given channel."""
        if channel not in self._CHANNEL_COMMANDS:
            raise ValueError(f"Invalid channel {channel}. Choose 0–7.")
        cmd = self._CHANNEL_COMMANDS[channel]
        self._bus.write_byte(self.address, cmd)
        return self._bus.read_byte(self.address)

    def read_voltage(self, channel):
        """Return voltage in volts for the given channel."""
        return self.read_raw(channel) * self.vref / 255

    def close(self):
        self._bus.close()


class RGBLed:
    """
    Common-anode RGB LED driven by three PWM channels.
    Because it's common-anode, lower duty cycle = brighter.
    """

    def __init__(self, pin_r, pin_g, pin_b, frequency=1000):
        for pin in (pin_r, pin_g, pin_b):
            GPIO.setup(pin, GPIO.OUT)
        self._r = GPIO.PWM(pin_r, frequency)
        self._g = GPIO.PWM(pin_g, frequency)
        self._b = GPIO.PWM(pin_b, frequency)
        self._r.start(100)
        self._g.start(100)
        self._b.start(100)

    def set_color(self, r, g, b):
        """
        Set color using 0–255 values per channel.
        Inverts to duty cycle for common-anode wiring.
        """
        self._r.ChangeDutyCycle(100 - r * 100 / 255)
        self._g.ChangeDutyCycle(100 - g * 100 / 255)
        self._b.ChangeDutyCycle(100 - b * 100 / 255)

    def off(self):
        self._r.ChangeDutyCycle(100)
        self._g.ChangeDutyCycle(100)
        self._b.ChangeDutyCycle(100)

    def stop(self):
        self._r.stop()
        self._g.stop()
        self._b.stop()


# ---------------------------------------------------------------------------
# Demo — mirrors week4/assignmentsolution.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)

    adc = ADS7830()
    rgb = RGBLed(pin_r=5, pin_g=6, pin_b=13)
    system_on = True

    btn_pin = 20
    GPIO.setup(btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def toggle(channel):
        global system_on
        system_on = not system_on
        print("System ON" if system_on else "System OFF")

    GPIO.add_event_detect(btn_pin, GPIO.FALLING, callback=toggle, bouncetime=200)

    try:
        while True:
            if system_on:
                r = adc.read_raw(2)
                g = adc.read_raw(3)
                b = adc.read_raw(4)
                rgb.set_color(r, g, b)
                print(f"R:{r}  G:{g}  B:{b}")
            else:
                rgb.off()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.remove_event_detect(btn_pin)
        rgb.stop()
        adc.close()
        GPIO.cleanup()
