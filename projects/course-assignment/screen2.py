import smbus2 as smbus  # smbus2 lets Python talk to I2C devices like the LCD
import time              # used to add delays between LCD operations
import RPi.GPIO as GPIO  # used to read the button pins

# --- LCD Constants ---
I2C_ADDR = 0x27   # I2C address of the LCD backpack — Pi uses this to target the correct device
LCD_WIDTH = 16    # LCD has 16 characters per row

# Mode constants passed to lcd_send_byte() to set the RS pin
LCD_CHR = 1  # character mode: byte is text to display (RS=1)
LCD_CMD = 0  # command mode: byte is an instruction like clear or move cursor (RS=0)

# DDRAM addresses for each row — sending these as a command moves the cursor to that row
LCD_LINE_1 = 0x80  # start of row 1
LCD_LINE_2 = 0xC0  # start of row 2

# --- LCD Control Pin Bitmasks ---
# Binary notation makes it clear which individual bit (pin) is being set.

# ENABLE = bit 2 (0b00000100)
# The LCD ignores data on its pins until ENABLE is pulsed HIGH then LOW.
# It only reads on the falling edge (HIGH→LOW) — like ringing a doorbell.
ENABLE = 0b00000100

# RS = bit 0 (0b00000001) — Register Select
# RS=0 → command (e.g. clear screen), RS=1 → character (e.g. print 'A')
# OR'd into every byte before sending so the LCD knows what type of data follows.
RS = 0b00000001

# --- Button GPIO Pin Numbers (BCM numbering) ---
BUTTON_1 = 20
BUTTON_2 = 21
BUTTON_3 = 16
BUTTON_4 = 26

bus = smbus.SMBus(1)  # open I2C bus 1 — the standard bus on modern Raspberry Pis


def setup_buttons():
    # BCM mode means we refer to pins by their GPIO number (e.g. GPIO20),
    # not by their physical position on the board.
    GPIO.setmode(GPIO.BCM)

    # Each button pin is configured as an input with an internal pull-up resistor.
    # The pull-up holds the pin at 3.3V (HIGH) by default.
    # When the button is pressed it connects the pin to GND, making it LOW.
    # So: not pressed = HIGH, pressed = LOW.
    GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def lcd_toggle_enable(bits):
    # The LCD only reads data on the falling edge of ENABLE (HIGH→LOW).
    # Without this pulse the LCD ignores everything on the data pins entirely.
    # The 0.5ms delays are critical — the LCD is much slower than the Pi CPU.
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, bits | ENABLE)   # set ENABLE HIGH
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, bits & ~ENABLE)  # set ENABLE LOW — LCD reads on this falling edge
    time.sleep(0.0005)


def lcd_send_byte(bits, mode):
    # The I2C backpack only has 4 data lines wired to the LCD, so one full byte
    # must be sent as two 4-bit chunks (nibbles) — upper nibble first, then lower.

    # Upper nibble: keep top 4 bits with & 0xF0, OR in mode and backlight bit (0x08)
    high_bits = mode | (bits & 0xF0) | 0x08

    # Lower nibble: shift bottom 4 bits left by 4 so they sit in the upper position,
    # then OR in mode and backlight bit
    low_bits = mode | ((bits << 4) & 0xF0) | 0x08

    # 0x08 keeps the backlight on. Remove it and the display logic still works
    # but the screen goes dark — a classic debugging trap.

    bus.write_byte(I2C_ADDR, high_bits)
    lcd_toggle_enable(high_bits)  # pulse ENABLE so LCD reads the upper nibble

    bus.write_byte(I2C_ADDR, low_bits)
    lcd_toggle_enable(low_bits)   # pulse ENABLE so LCD reads the lower nibble


def lcd_init():
    # The HD44780 controller does not know its configuration after power-on.
    # This sequence forces it into a known state before use.
    lcd_send_byte(0x33, LCD_CMD)  # wake up and reset — sends "3" twice to settle the controller
    lcd_send_byte(0x32, LCD_CMD)  # switch from 8-bit mode down to 4-bit mode
    # Without these first two bytes, initialization is flaky on some displays.
    lcd_send_byte(0x06, LCD_CMD)  # entry mode: cursor moves right after each character
    lcd_send_byte(0x0C, LCD_CMD)  # display ON, cursor OFF, blinking OFF
    lcd_send_byte(0x01, LCD_CMD)  # clear the display (slowest command — needs extra wait)
    time.sleep(0.002)             # wait for the clear to finish before sending more commands


def lcd_string(message, line):
    # Pad message to exactly 16 characters with spaces.
    # Without this, leftover characters from a longer previous message stay on screen.
    message = message.ljust(LCD_WIDTH)

    lcd_send_byte(line, LCD_CMD)       # move cursor to the start of the chosen row
    for i in range(LCD_WIDTH):
        lcd_send_byte(ord(message[i]), LCD_CHR)  # ord() converts each character to its ASCII number


def lcd_clear():
    # Command 0x01 tells the LCD to erase everything on the display.
    # The sleep gives the LCD time to finish before the next command arrives.
    lcd_send_byte(0x01, LCD_CMD)
    time.sleep(0.002)


def read_buttons_bits():
    # With pull-up resistors, GPIO.LOW means the button IS pressed.
    # We convert that into 1 (pressed) or 0 (not pressed) for each button.
    b1 = 1 if GPIO.input(BUTTON_1) == GPIO.LOW else 0
    b2 = 1 if GPIO.input(BUTTON_2) == GPIO.LOW else 0
    b3 = 1 if GPIO.input(BUTTON_3) == GPIO.LOW else 0
    b4 = 1 if GPIO.input(BUTTON_4) == GPIO.LOW else 0
    return b1, b2, b3, b4


def make_nibble(b1, b2, b3, b4):
    # Combine 4 individual bits into one number using bit shifting and OR.
    # Each button is assigned a bit position:
    #   b1 → bit 3 (value 8)
    #   b2 → bit 2 (value 4)
    #   b3 → bit 1 (value 2)
    #   b4 → bit 0 (value 1)
    # << moves a bit left by that many positions. | combines them into one value.
    # Example: b1=1, b2=0, b3=1, b4=1 → 1000 | 0000 | 0010 | 0001 = 1011 = 11
    value = (b1 << 3) | (b2 << 2) | (b3 << 1) | b4
    return value


def format_screen(value):
    # Build the two lines of text to show on the LCD for a given nibble value.
    binary_text = f"0b{value:04b}"        # e.g. "0b1011"
    hex_text = f"0x{value:01x}"           # e.g. "0xb"

    # Line 1: binary on the left, hex right-aligned to fill 16 characters
    line1 = binary_text + hex_text.rjust(16 - len(binary_text))

    # Line 2: decimal value right-aligned across the full 16 characters
    line2 = str(value).rjust(16)

    # Example LCD output for value 11:
    #   0b1011       0xb
    #                 11
    return line1, line2


def run(stop_event):
    lcd_init()       # configure the LCD before writing anything
    setup_buttons()  # configure GPIO pins for all four buttons

    # Start at -1 so the LCD always updates on the very first loop iteration
    last_value = -1 # we can never have -1 we have values from 0 to 15 so we can initialse it to -1  to take it out
    while not stop_event.is_set():
        b1, b2, b3, b4 = read_buttons_bits()       # read all four buttons
        value = make_nibble(b1, b2, b3, b4)         # combine into a single nibble value

        # Only refresh the LCD when the button state actually changes.
        # Without this check the display would flicker and update constantly.
        if value != last_value:
            line1, line2 = format_screen(value)
            lcd_clear()
            lcd_string(line1, LCD_LINE_1)  # show binary and hex on top row
            lcd_string(line2, LCD_LINE_2)  # show decimal on bottom row

            # Print to terminal for debugging
            print(f"Button states (b1 to b4): {b1} {b2} {b3} {b4}  Value: {value}")

            last_value = value  # remember current value to compare on next iteration

        time.sleep(0.1)  # short delay reduces CPU load and acts as basic debounce protection


if __name__ == "__main__":
    # Only run when this file is executed directly, not when imported by another script.
    import threading

    # threading.Event is used instead of a plain boolean because it is thread-safe —
    # a plain variable has no guarantee that changes are visible across threads immediately.
    stop_event = threading.Event()

    try:
        run(stop_event)
    except KeyboardInterrupt:
        # Ctrl+C sets the stop signal so the loop exits cleanly instead of crashing.
        # Without this the LCD would stay frozen with old text and GPIO cleanup may not run.
        stop_event.set()
        lcd_clear()
