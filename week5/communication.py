"""
Week 5 — Serial & I2C Communication
Classes: SerialTransmitter, I2CScanner, ServoMotor
"""

import RPi.GPIO as GPIO
import smbus
import time


class SerialTransmitter:
    """
    Transmits bytes bit-by-bit over a single GPIO pin (MSB first).
    LED_TX flashes HIGH for 1, LOW for 0.
    """

    def __init__(self, tx_pin, bit_delay=0.2):
        self.tx_pin = tx_pin
        self.bit_delay = bit_delay
        GPIO.setup(tx_pin, GPIO.OUT)
        GPIO.output(tx_pin, GPIO.LOW)

    def send_byte(self, byte):
        """Send one byte (integer 0–255) MSB first."""
        for bit_pos in range(7, -1, -1):
            bit = (byte >> bit_pos) & 1
            GPIO.output(self.tx_pin, GPIO.HIGH if bit else GPIO.LOW)
            time.sleep(self.bit_delay)

    def send_string(self, text, char_delay=1.0):
        """Send each character of a string as its ASCII byte."""
        for char in text:
            ascii_val = ord(char)
            print(f"Sending '{char}' → {ascii_val} → {ascii_val:08b}")
            self.send_byte(ascii_val)
            time.sleep(char_delay)
        print("Transmission complete.")

    def idle(self):
        GPIO.output(self.tx_pin, GPIO.LOW)


class I2CScanner:
    """Scans the I2C bus for connected devices."""

    def __init__(self, bus_num=1):
        self._bus = smbus.SMBus(bus_num)

    def scan(self, start=0x03, end=0x77):
        """Return a list of hex address strings for found devices."""
        found = []
        for addr in range(start, end + 1):
            try:
                self._bus.write_quick(addr)
                found.append(hex(addr))
            except OSError:
                pass
        return found

    def close(self):
        self._bus.close()


class ServoMotor:
    """
    Controls a hobby servo via PWM (50 Hz).
    Angle range: 0–180 degrees.
    """

    def __init__(self, pin, min_pulse_ms=0.6, max_pulse_ms=2.4, frequency=50):
        self.pin = pin
        self.min_pulse = min_pulse_ms
        self.max_pulse = max_pulse_ms
        GPIO.setup(pin, GPIO.OUT)
        self._pwm = GPIO.PWM(pin, frequency)
        self._pwm.start(0)

    def _angle_to_duty(self, angle):
        angle = max(0, min(180, angle))
        pulse_ms = self.min_pulse + (angle / 180.0) * (self.max_pulse - self.min_pulse)
        return (pulse_ms / 20.0) * 100.0

    def set_angle(self, angle, hold_ms=500):
        """Move servo to angle (degrees), hold for hold_ms, then release."""
        duty = self._angle_to_duty(angle)
        print(f"Servo → {angle}°  (duty {duty:.2f}%)")
        self._pwm.ChangeDutyCycle(duty)
        time.sleep(hold_ms / 1000)
        self._pwm.ChangeDutyCycle(0)

    def sweep(self, start=0, end=180, step=30, hold_ms=800):
        """Sweep from start to end angle in steps."""
        angles = range(start, end + 1, step) if start < end else range(start, end - 1, -step)
        for angle in angles:
            self.set_angle(angle, hold_ms)

    def stop(self):
        self._pwm.stop()


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)

    # Serial TX demo
    tx = SerialTransmitter(tx_pin=17)
    try:
        tx.send_string("Hello")
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        tx.idle()

    # I2C scan
    scanner = I2CScanner()
    print("I2C devices found:", scanner.scan())
    scanner.close()

    # Servo sweep
    servo = ServoMotor(pin=18)
    try:
        servo.sweep(0, 180, step=30)
        servo.sweep(180, 0, step=30)
    except KeyboardInterrupt:
        pass
    finally:
        servo.stop()
        GPIO.cleanup()
