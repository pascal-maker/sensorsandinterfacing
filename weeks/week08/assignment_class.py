"""Reusable class-based solution for the Week 08 potentiometer assignment."""

from pathlib import Path
import sys
import time

import RPi.GPIO as GPIO

# Make the shared hardware package available when this file is run directly.
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from hardware import ADS7830


class LEDBarGraph:
    """Control a 10-LED bar through two chained 74HC595 registers."""

    def __init__(self, data_pin=22, clock_pin=17, latch_pin=27):
        self.data_pin = data_pin
        self.clock_pin = clock_pin
        self.latch_pin = latch_pin
        GPIO.setup(
            (self.data_pin, self.clock_pin, self.latch_pin),
            GPIO.OUT,
            initial=GPIO.LOW,
        )

    def _pulse(self, pin):
        """Create one rising clock pulse on a shift-register pin."""
        GPIO.output(pin, GPIO.HIGH)
        GPIO.output(pin, GPIO.LOW)

    def _write_byte(self, value):
        """Send eight bits, most-significant bit first."""
        for bit_position in range(7, -1, -1):
            bit = (value >> bit_position) & 1
            GPIO.output(self.data_pin, bit)
            self._pulse(self.clock_pin)

    def _write_16_bits(self, value):
        """Send a pattern to two chained registers and update their outputs."""
        self._write_byte((value >> 8) & 0xFF)
        self._write_byte(value & 0xFF)
        self._pulse(self.latch_pin)

    def show(self, level, fill=False):
        """Show a level from 1 to 10 in single-LED or filled-bar mode."""
        level = max(1, min(10, level))
        pattern = (1 << level) - 1 if fill else 1 << (level - 1)
        self._write_16_bits(pattern)

    def clear(self):
        """Switch off every LED."""
        self._write_16_bits(0)


class Week08Assignment:
    """Read A2 and control the LED bar, buzzer pitch, and mode button."""

    def __init__(self, button_pin=20, buzzer_pin=12, adc_channel=2):
        self.button_pin = button_pin
        self.buzzer_pin = buzzer_pin
        self.adc_channel = adc_channel
        self.fill_mode = False

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.buzzer_pin, GPIO.OUT, initial=GPIO.LOW)

        self.adc = ADS7830(address=0x48)
        self.led_bar = LEDBarGraph()
        self.buzzer_pwm = GPIO.PWM(self.buzzer_pin, 100)
        self.buzzer_pwm.start(50)

        # A falling edge occurs when the pull-up button is pressed to ground.
        GPIO.add_event_detect(
            self.button_pin,
            GPIO.FALLING,
            callback=self.toggle_mode,
            bouncetime=300,
        )

    def toggle_mode(self, channel):
        """Switch between one illuminated LED and a filled LED bar."""
        self.fill_mode = not self.fill_mode
        mode = "FILL" if self.fill_mode else "SINGLE"
        print(f"GPIO {self.button_pin} pressed: {mode} mode")

    @staticmethod
    def scale_to_level(analog_value):
        """Map an 8-bit ADC reading (0-255) into the range 1-10."""
        return 1 + (analog_value * 10 // 256)

    @staticmethod
    def scale_to_frequency(analog_value):
        """Map an 8-bit ADC reading to a buzzer pitch of 100-1100 Hz."""
        return 100 + int(analog_value / 255 * 1000)

    def update(self):
        """Take one reading and update all outputs."""
        analog_value = self.adc.read_raw(self.adc_channel)
        level = self.scale_to_level(analog_value)
        frequency = self.scale_to_frequency(analog_value)

        self.led_bar.show(level, self.fill_mode)
        self.buzzer_pwm.ChangeFrequency(frequency)

        mode = "FILL" if self.fill_mode else "SINGLE"
        print(
            f"ADC={analog_value:3} | LED={level:2} | "
            f"Freq={frequency:4}Hz | Mode={mode}"
        )

    def run(self):
        """Update continuously until the user presses Ctrl+C."""
        print("Turn the A2 potentiometer; press GPIO 20 to change LED mode.")
        try:
            while True:
                self.update()
                time.sleep(0.05)
        except KeyboardInterrupt:
            print("\nWeek 08 assignment stopped")
        finally:
            self.close()

    def close(self):
        """Stop sound, clear LEDs, and release every hardware resource."""
        if self.buzzer_pwm is not None:
            self.buzzer_pwm.stop()
            self.buzzer_pwm = None
        GPIO.output(self.buzzer_pin, GPIO.LOW)
        self.led_bar.clear()
        self.adc.close()
        GPIO.cleanup()


if __name__ == "__main__":
    assignment = Week08Assignment()
    assignment.run()
