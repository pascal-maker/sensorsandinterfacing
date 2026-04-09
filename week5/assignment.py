import time
import RPi.GPIO as GPIO
import smbus

# =========================================================
# CONSTANTS
# =========================================================

ADC_ADDRESS = 0x48#
POT_CHANNEL = 4

SERVO_PIN = 18
BUTTON_PIN = 17

PWM_FREQUENCY = 50
MIN_PULSE_MS = 0.6
MAX_PULSE_MS = 2.4

LCD_COLUMNS = 16
LCD_CANDIDATE_ADDRESSES = (0x27, 0x3F)

# =========================================================
# LCD CLASS
# =========================================================

class I2cLcd:
    """
    LCD class for a 16x2 LCD with I2C backpack in 4-bit mode.
    """

    # RS values
    LCD_CHR = 0x01
    LCD_CMD = 0x00

    # Start addresses of line 1 and line 2
    LCD_LINE_1 = 0x80
    LCD_LINE_2 = 0xC0

    # Control bits
    ENABLE = 0x04
    BACKLIGHT = 0x08

    def __init__(self, bus, address):
        self.bus = bus
        self.address = address
        self.backlight = self.BACKLIGHT
        self._initialize()

    def _write_byte(self, data):
        """
        Send one raw byte to the LCD backpack.
        """
        self.bus.write_byte(self.address, data | self.backlight)

    def _toggle_enable(self, data):
        """
        Pulse the Enable pin so the LCD reads the data.
        """
        self._write_byte(data | self.ENABLE)
        time.sleep(0.0005)
        self._write_byte(data & ~self.ENABLE)
        time.sleep(0.0001)

    def _write_4_bits(self, value):
        """
        Send one 4-bit nibble.
        """
        self._write_byte(value)
        self._toggle_enable(value)

    def send(self, value, mode):
        """
        Send one full byte in 4-bit mode:
        - first upper nibble
        - then lower nibble
        """
        high = mode | (value & 0xF0)
        low = mode | ((value << 4) & 0xF0)
        self._write_4_bits(high)
        self._write_4_bits(low)

    def command(self, value):
        """
        Send command byte to LCD.
        """
        self.send(value, self.LCD_CMD)

    def write_char(self, value):
        """
        Send one character byte to LCD.
        """
        self.send(value, self.LCD_CHR)

    def _initialize(self):
        """
        Initialize the LCD in 4-bit mode.
        """
        time.sleep(0.05)

        self._write_4_bits(0x30)
        time.sleep(0.005)

        self._write_4_bits(0x30)
        time.sleep(0.001)

        self._write_4_bits(0x30)
        self._write_4_bits(0x20)

        self.command(0x28)  # 4-bit, 2 lines, 5x8 font
        self.command(0x0C)  # display on, cursor off
        self.command(0x06)  # entry mode
        self.clear()

    def clear(self):
        """
        Clear display.
        """
        self.command(0x01)
        time.sleep(0.002)

    def write_line(self, text, line_number):
        """
        Write one text string to line 1 or 2.
        """
        text = text.ljust(LCD_COLUMNS)[:LCD_COLUMNS]
        line_address = self.LCD_LINE_1 if line_number == 1 else self.LCD_LINE_2
        self.command(line_address)

        for char in text:
            self.write_char(ord(char))


def create_lcd(bus):
    """
    Try common LCD I2C addresses.
    Returns LCD object if found, otherwise None.
    """
    for address in LCD_CANDIDATE_ADDRESSES:
        try:
            bus.write_quick(address)
            return I2cLcd(bus, address)
        except OSError:
            continue
    return None

# =========================================================
# SETUP
# =========================================================

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

bus = smbus.SMBus(1)
lcd = create_lcd(bus)

servo_pwm = GPIO.PWM(SERVO_PIN, PWM_FREQUENCY)
servo_pwm.start(0)

system_on = True

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def read_adc(channel):
    """
    Read one analog value from the ADC.
    """
    if channel < 0 or channel > 7:
        raise ValueError("ADC channel must be between 0 and 7")

    command = 0x84 | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)
    return bus.read_byte_data(ADC_ADDRESS, command)


def map_value_to_angle(adc_value):
    """
    Convert ADC value 0..255 to angle 0..180.
    """
    return int((adc_value / 255.0) * 180)


def angle_to_duty_cycle(angle):
    """
    Convert angle to PWM duty cycle for servo.
    """
    angle = max(0, min(180, angle))
    pulse_width_ms = MIN_PULSE_MS + (angle / 180.0) * (MAX_PULSE_MS - MIN_PULSE_MS)
    return (pulse_width_ms / 20.0) * 100.0


def set_servo_angle(angle):
    """
    Move servo to the requested angle.
    """
    duty_cycle = angle_to_duty_cycle(angle)
    servo_pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.1)
    servo_pwm.ChangeDutyCycle(0)


def show_status(adc_value=None, angle=None, message=None):
    """
    Show current state on LCD if available,
    otherwise print to terminal.
    """
    if lcd is None:
        if message:
            print(message)
        elif adc_value is not None and angle is not None:
            print(f"Analog: {adc_value:3} | Angle: {angle:3}")
        return

    if message:
        lcd.write_line(message[:LCD_COLUMNS], 1)
        lcd.write_line("Press button", 2)
        return

    lcd.write_line(f"Analog: {adc_value:3}", 1)
    lcd.write_line(f"Angle : {angle:3}", 2)


def toggle_system(channel):
    """
    Button callback:
    toggle system on/off.
    """
    global system_on
    system_on = not system_on

    if system_on:
        show_status(message="System ON")
    else:
        servo_pwm.ChangeDutyCycle(0)
        show_status(message="System OFF")

    print("System on:", system_on)

# =========================================================
# BUTTON INTERRUPT
# =========================================================

GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=toggle_system, bouncetime=300)

# =========================================================
# MAIN PROGRAM
# =========================================================

try:
    if lcd is None:
        print("LCD not detected at 0x27 or 0x3F. Showing values in terminal.")
    else:
        show_status(message="System ON")
        time.sleep(1)

    while True:
        if system_on:
            adc_value = read_adc(POT_CHANNEL)
            angle = map_value_to_angle(adc_value)
            set_servo_angle(angle)
            show_status(adc_value=adc_value, angle=angle)

            print(f"A{POT_CHANNEL}: {adc_value:3} | Angle: {angle:3}")

        else:
            show_status(message="System OFF")

        time.sleep(0.2)

except KeyboardInterrupt:
    print("Program stopped by user.")

finally:
    if lcd is not None:
        lcd.clear()
        lcd.write_line("Goodbye", 1)

    servo_pwm.stop()
    bus.close()
    GPIO.cleanup()
    print("Cleanup done.")