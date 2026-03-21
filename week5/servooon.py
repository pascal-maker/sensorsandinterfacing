import time
import RPi.GPIO as GPIO

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus


# -----------------------------
# Settings
# -----------------------------
LCD_ADDR = 0x27
ADC_ADDR = 0x48

SERVO_PIN = 18
BUTTON_PIN = 20

USE_BUTTON = True
A4_CHANNEL = 4

PWM_FREQUENCY = 50
MIN_PULSE_MS = 0.6
MAX_PULSE_MS = 2.4


# -----------------------------
# LCD class
# -----------------------------
class LCD:
    LCD_WIDTH = 16

    LCD_CHR = 0x01
    LCD_CMD = 0x00

    LCD_LINE_1 = 0x80
    LCD_LINE_2 = 0xC0

    LCD_BACKLIGHT = 0x08
    ENABLE = 0x04

    E_PULSE = 0.0002
    E_DELAY = 0.0002

    def __init__(self, i2c_addr=LCD_ADDR, bus_id=1):
        self.addr = i2c_addr
        self.bus = SMBus(bus_id)
        self.lcd_init()

    def write_byte(self, bits):
        self.bus.write_byte(self.addr, bits)

    def send_byte_with_e_toggle(self, bits):
        self.write_byte(bits | self.ENABLE)
        time.sleep(self.E_PULSE)
        self.write_byte(bits & ~self.ENABLE)
        time.sleep(self.E_DELAY)

    def set_data_bits(self, value, mode):
        ms_nibble = (value & 0xF0) | mode | self.LCD_BACKLIGHT
        ls_nibble = ((value << 4) & 0xF0) | mode | self.LCD_BACKLIGHT

        self.send_byte_with_e_toggle(ms_nibble)
        self.send_byte_with_e_toggle(ls_nibble)

    def send_instruction(self, value):
        self.set_data_bits(value, self.LCD_CMD)
        if value in (0x01, 0x02):
            time.sleep(0.002)

    def send_character(self, value):
        if isinstance(value, str):
            value = ord(value)
        self.set_data_bits(value, self.LCD_CHR)

    def lcd_init(self):
        time.sleep(0.05)

        # force 4-bit mode
        self.send_byte_with_e_toggle(0x30 | self.LCD_BACKLIGHT)
        time.sleep(0.005)
        self.send_byte_with_e_toggle(0x30 | self.LCD_BACKLIGHT)
        time.sleep(0.001)
        self.send_byte_with_e_toggle(0x30 | self.LCD_BACKLIGHT)
        time.sleep(0.001)
        self.send_byte_with_e_toggle(0x20 | self.LCD_BACKLIGHT)
        time.sleep(0.001)

        # normal init
        self.send_instruction(0x28)
        self.send_instruction(0x0C)
        self.send_instruction(0x01)
        self.send_instruction(0x06)

    def clear(self):
        self.send_instruction(0x01)

    def send_string(self, message, line):
        self.send_instruction(line)
        message = str(message).ljust(self.LCD_WIDTH)[:self.LCD_WIDTH]

        for char in message:
            self.send_character(char)

    def close(self):
        self.bus.close()


# -----------------------------
# ADC read
# -----------------------------
def read_adc(bus, channel):
    # read 1 channel from ADC
    command = 0x84 | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)
    return bus.read_byte_data(ADC_ADDR, command)


# -----------------------------
# Servo helpers
# -----------------------------
def analog_to_angle(value):
    # convert 0-255 to 0-180
    return int((value / 255) * 180)


def angle_to_duty_cycle(angle):
    # convert angle to duty cycle
    pulse_ms = MIN_PULSE_MS + (angle / 180) * (MAX_PULSE_MS - MIN_PULSE_MS)
    return (pulse_ms / 20) * 100


def set_servo_angle(pwm, angle):
    duty = angle_to_duty_cycle(angle)
    pwm.ChangeDutyCycle(duty)


# -----------------------------
# Main program
# -----------------------------
def main():
    bus = SMBus(1)
    lcd = LCD(LCD_ADDR)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SERVO_PIN, GPIO.OUT)

    if USE_BUTTON:
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    pwm = GPIO.PWM(SERVO_PIN, PWM_FREQUENCY)
    pwm.start(0)

    system_on = True
    last_button_state = GPIO.HIGH

    try:
        while True:
            # button to switch on/off
            if USE_BUTTON:
                current_button_state = GPIO.input(BUTTON_PIN)

                if last_button_state == GPIO.HIGH and current_button_state == GPIO.LOW:
                    system_on = not system_on
                    time.sleep(0.2)   # debounce

                last_button_state = current_button_state

            if system_on:
                analog_value = read_adc(bus, A4_CHANNEL)
                angle = analog_to_angle(analog_value)

                set_servo_angle(pwm, angle)

                lcd.send_string(f"A4 value: {analog_value:3d}", lcd.LCD_LINE_1)
                lcd.send_string(f"Angle: {angle:3d} deg", lcd.LCD_LINE_2)

            else:
                pwm.ChangeDutyCycle(0)
                lcd.send_string("System OFF", lcd.LCD_LINE_1)
                lcd.send_string("Press button", lcd.LCD_LINE_2)

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nProgram stopped.")

    finally:
        pwm.stop()
        lcd.clear()
        lcd.close()
        bus.close()
        GPIO.cleanup()


if __name__ == "__main__":
    main()