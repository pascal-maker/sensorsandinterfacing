import smbus2 as smbus  # smbus2 lets Python talk to I2C devices like the LCD
import threading         # used to create stop events for safe thread communication
import time              # used to add delays between LCD operations
import subprocess        # used to run Linux shell commands from Python

# --- Constants ---
I2C_ADDR = 0x27   # I2C address of the LCD backpack (PCF8574 chip)
LCD_WIDTH = 16    # LCD is 16 characters wide per row

# Mode constants — passed to lcd_send_byte() to tell the LCD what type of data follows
LCD_CHR = 1  # character mode: the byte is text to display
LCD_CMD = 0  # command mode: the byte is an instruction (clear, move cursor, etc.)

# DDRAM addresses for each row. The LCD maps row 1 to 0x80 and row 2 to 0xC0.
# Sending this address first moves the cursor to that row.
LCD_LINE_1 = 0x80  # start of row 1
LCD_LINE_2 = 0xC0  # start of row 2

# --- Control pin bitmasks ---
# Binary notation is used here so you can see exactly which bit is being set.

# ENABLE = bit 2 (0b00000100)
# The LCD ignores data sitting on its pins until ENABLE is pulsed HIGH then LOW.
# Think of it as ringing a bell: the LCD only reads on the falling edge (HIGH→LOW).
ENABLE = 0b00000100

# RS = bit 0 (0b00000001) — Register Select
# RS=0 → command mode (e.g. clear screen, move cursor)
# RS=1 → character mode (e.g. print the letter 'A')
# It is OR'd into every byte sent so the LCD knows what type of data is coming.
RS = 0b00000001

bus = smbus.SMBus(1)  # open I2C bus 1 (the standard bus on modern Raspberry Pis)


def lcd_toggle_enable(bits):
    # The LCD only reads data on the falling edge of the ENABLE pin (HIGH→LOW).
    # Without this pulse the LCD ignores everything on the data pins entirely.
    # The 0.5ms delays are critical — the LCD is much slower than the Pi CPU.
    # Without them the Pi moves on before the LCD has finished reading, producing garbage.
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, bits | ENABLE)   # set ENABLE HIGH
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, bits & ~ENABLE)  # set ENABLE LOW — LCD reads on this edge
    time.sleep(0.0005)


def lcd_send_byte(bits, mode):
    # The I2C backpack only has 4 data lines wired to the LCD, so one full byte (8 bits)
    # must be sent as two 4-bit chunks (nibbles) — upper nibble first, then lower.

    # Upper nibble: keep top 4 bits with & 0xF0, OR in mode (CMD or CHR), OR 0x08 for backlight
    high_bits = mode | (bits & 0xF0) | 0x08

    # Lower nibble: shift bottom 4 bits up by 4 so they occupy the upper position,
    # then OR in mode and backlight bit
    low_bits = mode | ((bits << 4) & 0xF0) | 0x08

    # 0x08 keeps the backlight transistor on. Remove it and the display logic still
    # works perfectly but the screen goes dark — a classic debugging trap.

    bus.write_byte(I2C_ADDR, high_bits)
    lcd_toggle_enable(high_bits)  # pulse ENABLE so LCD reads the upper nibble

    bus.write_byte(I2C_ADDR, low_bits)
    lcd_toggle_enable(low_bits)   # pulse ENABLE so LCD reads the lower nibble


def lcd_init():
    # The HD44780 controller does not know its configuration after power-on.
    # This sequence forces it into a known state before we can use it.

    lcd_send_byte(0x33, LCD_CMD)  # send "3" twice — wakes the controller and resets it
    lcd_send_byte(0x32, LCD_CMD)  # switches from 8-bit mode down to 4-bit mode
    # Without these first two bytes initialization is flaky on some displays.

    lcd_send_byte(0x06, LCD_CMD)  # entry mode: cursor moves right after each character
    lcd_send_byte(0x0C, LCD_CMD)  # display ON, cursor OFF, blinking OFF
    lcd_send_byte(0x28, LCD_CMD)  # 4-bit mode, 2 lines, 5×8 dot character size
    lcd_send_byte(0x01, LCD_CMD)  # clear the display (takes up to 1.6ms — slowest command)
    time.sleep(0.0005)            # wait for the clear to finish before sending more commands


def lcd_string(message, line):
    # Pad the message to exactly 16 characters with spaces.
    # Without this, leftover characters from a longer previous message remain on screen.
    message = message.ljust(LCD_WIDTH, " ")

    lcd_send_byte(line, LCD_CMD)          # move cursor to the start of the chosen row
    for ch in message[:LCD_WIDTH]:        # send each character one by one
        lcd_send_byte(ord(ch), LCD_CHR)   # ord() converts the character to its ASCII number


def lcd_clear():
    # Command 0x01 tells the LCD to erase everything on the display.
    # The sleep gives the LCD time to finish clearing before the next command arrives.
    lcd_send_byte(0x01, LCD_CMD)
    time.sleep(0.0005)


def get_ip_addresses():
    # Run the Linux command "ip a" from Python and capture its full text output.
    # text=True returns a string instead of bytes, so string methods like
    # splitlines(), strip(), and split() work correctly on the result.
    output = subprocess.check_output("ip a", shell=True, text=True)

    # Default values if an interface has no IP or is not connected
    wlan_ip = "Not Connected"
    eth_ip = "Not Connected"

    # State machine: track which network adapter section we are currently reading.
    # When we spot "wlan0:" or "eth0:", we update current_adapter.
    # The next "inet" line then belongs to whichever adapter is active.
    current_adapter = ""

    for line in output.splitlines():
        line = line.strip()  # remove leading/trailing whitespace for clean comparisons

        if "wlan0:" in line:
            current_adapter = "wlan0"       # entering the WiFi section
        elif "eth0:" in line:
            current_adapter = "eth0"        # entering the Ethernet section
        elif line.startswith("inet "):      # IPv4 address line
            # line looks like: "inet 192.168.1.15/24 brd ..."
            # split()[1] → "192.168.1.15/24"
            # split("/")[0] → "192.168.1.15"  (strips the subnet mask)
            ip_address = line.split()[1].split("/")[0]
            if current_adapter == "wlan0":
                wlan_ip = ip_address
            elif current_adapter == "eth0":
                eth_ip = ip_address

    return wlan_ip, eth_ip  # return both as a tuple


def wait_or_stop(stop_event, seconds):
    # Instead of sleeping the full duration in one go, sleep in 0.1s chunks.
    # This way the loop can react to a stop signal within 0.1s rather than
    # being stuck sleeping for the full period.
    steps = int(seconds / 0.1)
    for _ in range(steps):
        if stop_event.is_set():  # another thread has requested a stop
            return
        time.sleep(0.1)


def run(stop_event):
    lcd_init()  # configure the LCD before writing anything to it

    # Keep cycling through WiFi and LAN IPs until the stop signal is received.
    while not stop_event.is_set():
        wlan_ip, eth_ip = get_ip_addresses()

        # Show WiFi IP for 2 seconds
        lcd_clear()
        lcd_string("WiFi: ", LCD_LINE_1)
        lcd_string(wlan_ip, LCD_LINE_2)
        wait_or_stop(stop_event, 2)

        if stop_event.is_set():  # check again so we don't write LAN after being stopped
            break

        # Show LAN IP for 2 seconds
        lcd_clear()
        lcd_string("LAN: ", LCD_LINE_1)
        lcd_string(eth_ip, LCD_LINE_2)
        wait_or_stop(stop_event, 2)

    lcd_clear()  # wipe the screen before the function exits


if __name__ == "__main__":
    # threading.Event is used instead of a plain boolean because it is thread-safe —
    # a plain variable has no guarantee that changes are visible across threads immediately.
    stop_event = threading.Event()
    try:
        run(stop_event)
    except KeyboardInterrupt:
        # Ctrl+C sets the stop signal so the loop exits cleanly instead of crashing.
        stop_event.set()
        lcd_clear()
