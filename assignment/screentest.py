#!/usr/bin/env python3

# smbus = for I2C communication with the LCD
import smbus

# time = for small delays
import time

# RPi.GPIO = to read the joystick button on GPIO7
import RPi.GPIO as GPIO


# =========================================================
# LCD SETTINGS
# =========================================================

# I2C address of the LCD
# Usually 0x27 or 0x3F
I2C_ADDR = 0x27

# LCD has 16 characters per line
LCD_WIDTH = 16

# Mode when sending data to LCD
# LCD_CHR = normal character
# LCD_CMD = LCD command
LCD_CHR = 1
LCD_CMD = 0

# Start addresses of line 1 and line 2
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0

# LCD control bits
ENABLE = 0b00000100   # enable bit
RS = 0b00000001       # register select bit


# =========================================================
# JOYSTICK BUTTON SETTINGS
# =========================================================

# The joystick button is connected to GPIO7
JOY_BUTTON = 7

# We start on screen 1
current_screen = 1

# This flag tells us if we need to redraw the LCD
# In the beginning it is True, because we want to show screen 1 immediately
screen_changed = True


# =========================================================
# I2C BUS
# =========================================================

# Open I2C bus 1 on the Raspberry Pi
bus = smbus.SMBus(1)


# =========================================================
# LCD FUNCTIONS
# =========================================================

def lcd_toggle_enable(bits):
    """
    Send a short pulse on the ENABLE bit.
    The LCD only reads data when ENABLE is pulsed.
    """

    # small delay before pulse
    time.sleep(0.0005)

    # set ENABLE high
    bus.write_byte(I2C_ADDR, bits | ENABLE)

    # small delay while ENABLE is high
    time.sleep(0.0005)

    # set ENABLE low again
    bus.write_byte(I2C_ADDR, bits & ~ENABLE)

    # small delay after pulse
    time.sleep(0.0005)


def lcd_send_byte(bits, mode):
    """
    Send one byte to the LCD.
    Because the LCD works in 4-bit mode,
    we send the byte in 2 parts:
    - high nibble
    - low nibble
    """

    # Take upper 4 bits
    # Add mode (command or character)
    # Add backlight bit (0x08)
    high_bits = mode | (bits & 0xF0) | 0x08

    # Shift lower 4 bits to the left
    # Add mode and backlight bit
    low_bits = mode | ((bits << 4) & 0xF0) | 0x08

    # Send upper 4 bits first
    bus.write_byte(I2C_ADDR, high_bits)
    lcd_toggle_enable(high_bits)

    # Then send lower 4 bits
    bus.write_byte(I2C_ADDR, low_bits)
    lcd_toggle_enable(low_bits)


def lcd_init():
    """
    Initialize the LCD in 4-bit mode.
    These commands are standard startup commands for the LCD.
    """

    lcd_send_byte(0x33, LCD_CMD)   # initialize
    lcd_send_byte(0x32, LCD_CMD)   # set to 4-bit mode
    lcd_send_byte(0x06, LCD_CMD)   # cursor move direction
    lcd_send_byte(0x0C, LCD_CMD)   # display on, cursor off
    lcd_send_byte(0x28, LCD_CMD)   # 2 lines, 5x8 font
    lcd_send_byte(0x01, LCD_CMD)   # clear display

    # give LCD a little time
    time.sleep(0.005)


def lcd_string(message, line):
    """
    Print a string on one LCD line.
    The message is padded with spaces so old text disappears.
    """

    # Make sure the text is exactly 16 chars
    # If shorter, fill with spaces
    message = message.ljust(LCD_WIDTH, " ")

    # Send the line address (line 1 or line 2)
    lcd_send_byte(line, LCD_CMD)

    # Send every character one by one
    for ch in message[:LCD_WIDTH]:
        lcd_send_byte(ord(ch), LCD_CHR)


def lcd_clear():
    """
    Clear the LCD screen.
    """
    lcd_send_byte(0x01, LCD_CMD)
    time.sleep(0.005)


# =========================================================
# BUTTON CALLBACK FUNCTION
# =========================================================

def button_callback(channel):
    """
    This function runs automatically when the joystick button is pressed.
    'channel' is the pin number that triggered the interrupt.
    """

    # We want to change these global variables
    global current_screen, screen_changed

    # Go to next screen
    current_screen += 1

    # If we go past screen 6, go back to screen 1
    if current_screen > 6:
        current_screen = 1

    # Tell the main loop that LCD must update
    screen_changed = True

    # Also print current screen in terminal for debugging
    print(f"Switched to screen {current_screen}")


# =========================================================
# GPIO SETUP
# =========================================================

# Use BCM numbering
GPIO.setmode(GPIO.BCM)

# Set GPIO7 as input with internal pull-up resistor
# That means:
# - not pressed = HIGH (1)
# - pressed = LOW (0)
GPIO.setup(JOY_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Add interrupt on falling edge
# Falling edge means: signal goes from HIGH to LOW
# That is exactly what happens when button is pressed
GPIO.add_event_detect(
    JOY_BUTTON,
    GPIO.FALLING,
    callback=button_callback,
    bouncetime=200
)

# Initialize LCD once
lcd_init()


# =========================================================
# MAIN LOOP
# =========================================================

try:
    while True:

        # Only update LCD when screen changed
        if screen_changed:

            # Clear old content
            lcd_clear()

            # Show screen number on first line
            lcd_string(f"Screen {current_screen}", LCD_LINE_1)

            # Show extra text on second line
            lcd_string("Joystick switch", LCD_LINE_2)

            # Reset flag
            screen_changed = False

        # small delay so loop is not too fast
        time.sleep(0.1)


# =========================================================
# STOP PROGRAM CLEANLY
# =========================================================

except KeyboardInterrupt:
    # clear LCD when stopping
    lcd_clear()

    # release GPIO pins
    GPIO.cleanup()

    print("\nStopped")