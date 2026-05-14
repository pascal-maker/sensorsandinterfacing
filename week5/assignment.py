import RPi.GPIO as GPIO#imports the RPi.GPIO library
import time#imports the time library
import smbus#imports the smbus library
import threading#imports the threading library

# =========================================================
# SETTINGS
# =========================================================

SERVO_PIN = 18#sets the servo pin
BUTTON_PIN = 20#sets the button pin

ADC_ADDR = 0x48#sets the ADC address
ADC_COMMAND = 0x44#sets the ADC command

PWM_FREQUENCY = 50#sets the PWM frequency

# LCD SETTINGS
LCD_ADDR = 0x27#sets the LCD address
LCD_WIDTH = 16#sets the LCD width

LCD_CHR = 1#sets the LCD character mode
LCD_CMD = 0#sets the LCD command mode

LCD_LINE_1 = 0x80#sets the LCD line 1
LCD_LINE_2 = 0xC0#sets the LCD line 2

ENABLE = 0b00000100#sets the enable pin


# =========================================================
# I2C + GPIO SETUP
# =========================================================

bus = smbus.SMBus(1)#initializes the I2C bus

GPIO.setwarnings(False)#disables warning messages
GPIO.setmode(GPIO.BCM)#sets the GPIO mode to BCM

GPIO.setup(SERVO_PIN, GPIO.OUT)#initializes the servo pin as output

GPIO.setup(#sets the button pin as input with pull-up enabled
    BUTTON_PIN,#
    GPIO.IN,
    pull_up_down=GPIO.PUD_UP#enables the pull-up resistor
)

servo = GPIO.PWM(SERVO_PIN, PWM_FREQUENCY)#initializes the PWM on the servo pin
servo.start(0)#starts the PWM

system_on = True#initializes the system_on variable to True

lock = threading.Lock()#creates a lock to prevent race conditions


# =========================================================
# LCD FUNCTIONS
# =========================================================

def lcd_toggle_enable(bits):#toggles the enable pin

    time.sleep(0.0005)#waits for 0.0005 seconds

    bus.write_byte(LCD_ADDR, (bits | ENABLE))#writes the enable pin to high
    time.sleep(0.0005)#waits for 0.0005 seconds

    bus.write_byte(LCD_ADDR, (bits & ~ENABLE))#writes the enable pin to low
    time.sleep(0.0005)#waits for 0.0005 seconds


def lcd_send_byte(bits, mode):#sends a byte to the LCD

    high_bits = mode | (bits & 0xF0) | 0x08#sets the high bits
    low_bits = mode | ((bits << 4) & 0xF0) | 0x08#sets the low bits

    bus.write_byte(LCD_ADDR, high_bits)#writes the high bits to the LCD
    lcd_toggle_enable(high_bits)#toggles the enable pin

    bus.write_byte(LCD_ADDR, low_bits)#writes the low bits to the LCD
    lcd_toggle_enable(low_bits)#toggles the enable pin


def lcd_init():#initializes the LCD

    lcd_send_byte(0x33, LCD_CMD)#sets the LCD to 8-bit mode
    lcd_send_byte(0x32, LCD_CMD)#sets the LCD to 4-bit mode

    lcd_send_byte(0x06, LCD_CMD)#turns on the LCD
    lcd_send_byte(0x0C, LCD_CMD)#turns on the cursor

    lcd_send_byte(0x28, LCD_CMD)#sets the LCD to 4-bit mode
    lcd_send_byte(0x01, LCD_CMD)#clears the LCD

    time.sleep(0.005)#waits for 0.005 seconds


def lcd_display_string(message, line):#displays a string on the LCD

    message = message.ljust(LCD_WIDTH)#pads the message with spaces

    lcd_send_byte(line, LCD_CMD)#sets the cursor position

    for char in message:#iterates through the characters of the message
        lcd_send_byte(ord(char), LCD_CHR)#sends the character to the LCD


# =========================================================
# ADC FUNCTION
# =========================================================

def read_adc():#reads the ADC value

    bus.write_byte(ADC_ADDR, ADC_COMMAND)#writes the ADC command to the I2C bus

    value = bus.read_byte(ADC_ADDR)#reads the ADC value from the I2C bus

    return value#returns the ADC value


# =========================================================
# BUTTON CALLBACK
# =========================================================

def toggle_system(channel):#toggles the system_on variable

    global system_on

    with lock:#acquires the lock
        system_on = not system_on#toggles the system_on variable

    if system_on:
        print("System ON")#prints that the system is on
    else:
        print("System OFF")#prints that the system is off


GPIO.add_event_detect(
    BUTTON_PIN,#detects the button press
    GPIO.FALLING,#detects the falling edge
    callback=toggle_system,#calls the toggle_system function
    bouncetime=200#sets the bouncetime to 200ms
)


# =========================================================
# SERVO FUNCTION
# =========================================================

def angle_to_duty(angle):#converts an angle to a duty cycle

    if angle < 0:#keeps angle inside valid range
        angle = 0#sets angle to 0 if it is negative

    if angle > 180:#keeps angle inside valid range
        angle = 180#sets angle to 180 if it is greater than 180

    duty = 2.5 + (angle / 180.0) * 10#converts angle to duty cycle

    return duty#returns the duty cycle


# =========================================================
# LCD INITIALIZATION
# =========================================================

lcd_init()#initializes the LCD


# =========================================================
# MAIN LOOP
# =========================================================

try:

    previous_angle = -1#initializes the previous_angle variable to -1

    while True:

        with lock:#acquires the lock
            active = system_on#checks if the system is on

        if active:#if the system is on

            adc_value = read_adc()#reads the ADC value

            angle = int((adc_value / 255) * 180)#converts ADC value to angle

            duty = angle_to_duty(angle)#converts angle to duty cycle

            if angle != previous_angle:#checks if the angle has changed

                servo.ChangeDutyCycle(duty)#changes the duty cycle

                time.sleep(0.3)#waits for 0.3 seconds

                servo.ChangeDutyCycle(0)#stops the servo

                previous_angle = angle#updates the previous_angle variable

            line1 = f"ADC:{adc_value:3d}"#formats the ADC value to be displayed on the first line
            line2 = f"Angle:{angle:3d}"#formats the angle to be displayed on the second line

            lcd_display_string(line1, LCD_LINE_1)#displays the first line on the LCD
            lcd_display_string(line2, LCD_LINE_2)#displays the second line on the LCD

            print(
                f"ADC: {adc_value} | "#formats the ADC value to be displayed on the first line
                f"Angle: {angle} | "#formats the angle to be displayed on the second line
                f"Duty: {duty:.2f}%"#formats the duty cycle to be displayed on the third line
            )

        else:#if the system is off

            servo.ChangeDutyCycle(0)#stops the servo

            lcd_display_string(
                "System OFF",
                LCD_LINE_1#displays "System OFF" on the first line
            )

            lcd_display_string(
                "",
                LCD_LINE_2#displays an empty string on the second line
            )

            print("System OFF")#prints that the system is off

        time.sleep(0.1)#waits for 0.1 seconds

except KeyboardInterrupt:#if a KeyboardInterrupt occurs

    print("Program stopped by user")#prints that the program was stopped by the user

finally:#finally, it will clean up the GPIO and bus

    servo.stop()#stops the servo

    GPIO.cleanup()#cleans up the GPIO

    bus.close()#closes the bus

    print("Cleanup complete")#prints that the cleanup is complete