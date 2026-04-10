import time
import RPi.GPIO as GPIO
import smbus

# =========================================================
# CONSTANTS
# =========================================================

# I2C address of the ADC
ADC_ADDRESS = 0x48

# Potentiometer channel
POT_CHANNEL = 4

# GPIO pins
SERVO_PIN = 18
BUTTON_PIN = 17

# Servo settings
PWM_FREQUENCY = 50          # 50 Hz is standard for servos
MIN_PULSE_MS = 0.6          # pulse width for 0 degrees
MAX_PULSE_MS = 2.4          # pulse width for 180 degrees

# LCD settings
LCD_COLUMNS = 16
LCD_CANDIDATE_ADDRESSES = (0x27, 0x3F)

# =========================================================
# LCD CLASS
# =========================================================

class I2cLcd:
    """
    Class for a 16x2 LCD with I2C backpack in 4-bit mode.
    """

    # RS modes
    LCD_CHR = 0x01   # sending character data
    LCD_CMD = 0x00   # sending command data

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
        Pulse the Enable bit so the LCD reads the nibble.
        """
        self._write_byte(data | self.ENABLE)
        time.sleep(0.0005)
        self._write_byte(data & ~self.ENABLE)
        time.sleep(0.0001)

    def _write_4_bits(self, value):
        """
        Send one 4-bit nibble to the LCD.
        """
        self._write_byte(value)
        self._toggle_enable(value)

    def send(self, value, mode):
        """
        Send one full byte in 4-bit mode:
        first upper nibble, then lower nibble.
        """
        high = mode | (value & 0xF0)
        low = mode | ((value << 4) & 0xF0)

        self._write_4_bits(high)
        self._write_4_bits(low)

    def command(self, value):
        """
        Send a command byte to the LCD.
        """
        self.send(value, self.LCD_CMD)

    def write_char(self, value):
        """
        Send one character to the LCD.
        """
        self.send(value, self.LCD_CHR)

    def _initialize(self):
        """
        Initialize the LCD in 4-bit mode.
        """
        time.sleep(0.05)

        # Force LCD into 4-bit mode
        self._write_4_bits(0x30)
        time.sleep(0.005)
        self._write_4_bits(0x30)
        time.sleep(0.001)
        self._write_4_bits(0x30)
        self._write_4_bits(0x20)

        # Function set, display on, entry mode, clear
        self.command(0x28)   # 4-bit, 2 lines, 5x8 dots
        self.command(0x0C)   # display ON, cursor OFF
        self.command(0x06)   # auto-increment cursor
        self.clear()

    def clear(self):
        """
        Clear the LCD screen.
        """
        self.command(0x01)
        time.sleep(0.002)

    def write_line(self, text, line_number):
        """
        Write text to line 1 or line 2.
        """
        text = text.ljust(LCD_COLUMNS)[:LCD_COLUMNS]
        line_address = self.LCD_LINE_1 if line_number == 1 else self.LCD_LINE_2
        self.command(line_address)

        for char in text:
            self.write_char(ord(char))


def create_lcd(bus):
    """
    Try common I2C addresses for the LCD.
    Return an LCD object if found, otherwise None.
    """
    for address in LCD_CANDIDATE_ADDRESSES:
        try:
            bus.write_quick(address)
            return I2cLcd(bus, address)
        except OSError:
            continue
    return None

# =========================================================
# GPIO + I2C SETUP
# =========================================================

GPIO.setmode(GPIO.BCM)

# Set up servo pin as output
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Set up button pin with internal pull-up resistor
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Open I2C bus
bus = smbus.SMBus(1)

# Try to create LCD object
lcd = create_lcd(bus)

# Start servo PWM
servo_pwm = GPIO.PWM(SERVO_PIN, PWM_FREQUENCY)
servo_pwm.start(0)

# System state
system_on = True

# Track previous state so we do not keep rewriting the LCD unnecessarily
last_state = None

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def read_adc(channel):
    """
    Read one analog value (0..255) from the ADC.
    """
    if channel < 0 or channel > 7:
        raise ValueError("ADC channel must be between 0 and 7")

    # Build command byte for this ADC chip
    command = 0x84 | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)
    return bus.read_byte_data(ADC_ADDRESS, command)


def map_value_to_angle(adc_value):
    """
    Convert ADC value (0..255) to servo angle (0..180).
    """
    return int((adc_value / 255.0) * 180)


def angle_to_duty_cycle(angle):
    """
    Convert servo angle (0..180) to PWM duty cycle.
    """
    angle = max(0, min(180, angle))  # clamp angle to safe range

    pulse_width_ms = MIN_PULSE_MS + (angle / 180.0) * (MAX_PULSE_MS - MIN_PULSE_MS)

    # Servo period is 20 ms at 50 Hz
    return (pulse_width_ms / 20.0) * 100.0


def set_servo_angle(angle):
    """
    Move the servo to the requested angle.
    """
    duty_cycle = angle_to_duty_cycle(angle)
    servo_pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.1)                # allow servo to move
    servo_pwm.ChangeDutyCycle(0)   # stop sending signal to reduce jitter


def show_status(adc_value=None, angle=None, message=None):
    """
    Show status on the LCD if available.
    If no LCD is found, print to the terminal.
    """
    if lcd is None:
        if message:
            print(message)
        elif adc_value is not None and angle is not None:
            print(f"Analog: {adc_value:3} | Angle: {angle:3}")
        return

    # Show a message screen
    if message:
        lcd.write_line(message[:LCD_COLUMNS], 1)
        lcd.write_line("Press button", 2)
        return

    # Show normal live values
    lcd.write_line(f"Analog: {adc_value:3}", 1)
    lcd.write_line(f"Angle : {angle:3}", 2)


def toggle_system(channel):
    """
    Button interrupt callback:
    toggle the system ON or OFF.
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

GPIO.add_event_detect(
    BUTTON_PIN,
    GPIO.FALLING,
    callback=toggle_system,
    bouncetime=300
)

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
        # -------------------------
        # System ON
        # -------------------------
        if system_on:
            adc_value = read_adc(POT_CHANNEL)         # read potentiometer on A4
            angle = map_value_to_angle(adc_value)     # convert 0..255 to 0..180
            set_servo_angle(angle)                    # move servo
            show_status(adc_value=adc_value, angle=angle)  # show values on LCD

            print(f"A{POT_CHANNEL}: {adc_value:3} | Angle: {angle:3}")
            last_state = "ON"

        # -------------------------
        # System OFF
        # -------------------------
        else:
            # Only update LCD once when switching to OFF
            if last_state != "OFF":
                show_status(message="System OFF")
                last_state = "OFF"

        time.sleep(0.2)

except KeyboardInterrupt:
    print("Program stopped by user.")

finally:
    # Clear LCD before closing
    if lcd is not None:
        lcd.clear()
        lcd.write_line("Goodbye", 1)

    # Stop PWM and clean up GPIO/I2C
    servo_pwm.stop()
    bus.close()
    GPIO.cleanup()
    print("Cleanup done.")