"""
Week 5 — Serial & I2C Communication
Classes: SerialTransmitter, I2CScanner, ServoMotor
"""

import RPi.GPIO as GPIO#Imports the RPi.GPIO library
import smbus #Imports the smbus library
import time #Imports the time library


class SerialTransmitter:#transmits bytes bit-by-bit over a single GPIO pin (MSB first)
    """
    Transmits bytes bit-by-bit over a single GPIO pin (MSB first).
    LED_TX flashes HIGH for 1, LOW for 0.
    """

    def __init__(self, tx_pin, bit_delay=0.2):#initializes the SerialTransmitter
        self.tx_pin = tx_pin#sets the tx pin
        self.bit_delay = bit_delay#sets the bit delay
        GPIO.setup(tx_pin, GPIO.OUT)#sets the tx pin as output
        GPIO.output(tx_pin, GPIO.LOW)#sets the tx pin to low

    def send_byte(self, byte):#sends one byte (integer 0-255) MSB first
        """Send one byte (integer 0–255) MSB first."""
        for bit_pos in range(7, -1, -1):#iterates through the bits of the byte
            bit = (byte >> bit_pos) & 1#gets the bit position
            GPIO.output(self.tx_pin, GPIO.HIGH if bit else GPIO.LOW)#outputs the bit
            time.sleep(self.bit_delay)#waits for the bit delay

    def send_string(self, text, char_delay=1.0):#sends a string to the serial
        """Send each character of a string as its ASCII byte."""
        for char in text:#iterates through the characters of the string
            ascii_val = ord(char)#gets the ASCII value of the character
            print(f"Sending '{char}' → {ascii_val} → {ascii_val:08b}")#prints the character, its ASCII value, and its binary representation
            self.send_byte(ascii_val)#sends the ASCII value of the character to the serial
            time.sleep(char_delay)#waits for the character delay
        print("Transmission complete.")#prints that the transmission is complete

    def idle(self):#sets the tx pin to low
        GPIO.output(self.tx_pin, GPIO.LOW) #sets the tx pin to low


class I2CScanner:#scans the I2C bus for connected devices
    """Scans the I2C bus for connected devices."""

    def __init__(self, bus_num=1):#initializes the I2CScanner
        self._bus = smbus.SMBus(bus_num)#sets the bus number

    def scan(self, start=0x03, end=0x77):#scans the I2C bus for connected devices
        """Return a list of hex address strings for found devices."""
        found = []
        for addr in range(start, end + 1):#iterates through the addresses of the I2C bus
            try:
                self._bus.write_quick(addr) #writes the address to the I2C bus
                found.append(hex(addr))#appends the address to the list
            except OSError:#if an OSError occurs
                pass#does nothing
        return found #returns the list of found addresses

    def close(self):#closes the I2C bus
        self._bus.close()


class ServoMotor:#controls a hobby servo via PWM (50 Hz)
    """
    Controls a hobby servo via PWM (50 Hz).
    Angle range: 0–180 degrees.
    """

    def __init__(self, pin, min_pulse_ms=0.6, max_pulse_ms=2.4, frequency=50):#initializes the ServoMotor
        self.pin = pin#sets the pin
        self.min_pulse = min_pulse_ms#sets the minimum pulse width
        self.max_pulse = max_pulse_ms#sets the maximum pulse width
        GPIO.setup(pin, GPIO.OUT)#sets the pin as output
        self._pwm = GPIO.PWM(pin, frequency)#creates a PWM instance
        self._pwm.start(0)#starts the PWM with 0% duty cycle
        

    def _angle_to_duty(self, angle):#converts an angle (0 to 180 degrees) to the matching duty cycle for the servo
        angle = max(0, min(180, angle))#keeps angle inside valid range
        pulse_ms = self.min_pulse + (angle / 180.0) * (self.max_pulse - self.min_pulse)#maps angle to pulse width
        return (pulse_ms / 20.0) * 100.0#converts pulse width to duty cycle percentage

    def set_angle(self, angle, hold_ms=500):#moves the servo to the given angle and holds it for the specified time
        """Move servo to angle (degrees), hold for hold_ms, then release."""
        duty = self._angle_to_duty(angle)#converts angle to duty cycle
        print(f"Servo → {angle}°  (duty {duty:.2f}%)")#prints the angle and duty cycle
        self._pwm.ChangeDutyCycle(duty)#changes the duty cycle
        time.sleep(hold_ms / 1000)#waits for the specified time
        self._pwm.ChangeDutyCycle(0)

    def sweep(self, start=0, end=180, step=30, hold_ms=800):#sweeps the servo from start to end angle in steps  
        """Sweep from start to end angle in steps."""
        angles = range(start, end + 1, step) if start < end else range(start, end - 1, -step)#determines the range of angles to sweep through
        for angle in angles:#iterates through the angles
            self.set_angle(angle, hold_ms)#sets the angle

    def stop(self):#stops the PWM
        self._pwm.stop()


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM) #sets the mode to BCM

    # Serial TX demo
    tx = SerialTransmitter(tx_pin=17)#initializes the SerialTransmitter
    try:#trys to send the string "Hello"
        tx.send_string("Hello")
    except KeyboardInterrupt:#if a KeyboardInterrupt occurs
        print("\nInterrupted.")#prints that the transmission was interrupted
    finally:#finally, it will close the I2C bus
        tx.idle()#sets the tx pin to low

    # I2C scan
    scanner = I2CScanner()#initializes the I2CScanner
    print("I2C devices found:", scanner.scan())#prints the list of found addresses
    scanner.close()#closes the I2C bus

    # Servo sweep
    servo = ServoMotor(pin=18)#initializes the ServoMotor
    try:#trys to sweep the servo
        servo.sweep(0, 180, step=30)#sweeps the servo from 0 to 180 degrees in steps of 30 degrees
        servo.sweep(180, 0, step=30)#sweeps the servo from 180 to 0 degrees in steps of 30 degrees
    except KeyboardInterrupt:#if a KeyboardInterrupt occurs
        pass#does nothing
    finally:#finally, it will stop the PWM
        servo.stop()#stops the PWM
        GPIO.cleanup()#cleans up the GPIO pins
