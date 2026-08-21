import RPi.GPIO as GPIO
import time

# --- Pin mapping (BCM numbering) ---
# Rows are inputs held HIGH by 1kΩ pull-up resistors on the PCB.
# When a key is pressed it physically connects that row wire to the driven column,
# pulling the row LOW — that's how the Pi detects which key was pressed.
ROWS = [16, 20, 21, 26]   # keypad pins 8, 7, 6, 5 (top row → bottom row)
COLS = [19, 13,  6,  5]   # keypad pins 4, 3, 2, 1 (left col → right col)

# Key layout — each entry matches the physical position on the 4x4 membrane keypad.
# KEYS[row][col] gives the character for the key at that intersection.
KEYS = [
    ['1', '2', '3', 'A'],  # top row
    ['4', '5', '6', 'B'],  # second row
    ['7', '8', '9', 'C'],  # third row
    ['*', '0', '#', 'D'],  # bottom row
]


class Keypad4x4:
    def __init__(self, rows=ROWS, cols=COLS, keys=KEYS):#constructor for the 4x4 keypad
        self._rows = rows #the rows of the keypad
        self._cols = cols#the columns of the keypad
        self._keys = keys#the keys of the keypad
        self._setup()#sets up the keypad

    def _setup(self):#sets up the keypad
        GPIO.setmode(GPIO.BCM)#sets the mode to BCM
        GPIO.setwarnings(False)#disables the warnings
        # Rows are inputs — the PCB already has 1kΩ pull-ups to 3.3V,
        # but software pull-ups are added too as a safety net
        for row in self._rows:#sets the rows as inputs
            GPIO.setup(row, GPIO.IN, pull_up_down=GPIO.PUD_UP)#sets the rows as inputs with pull up resistors
        # Columns are outputs, all held HIGH at startup.
        # Only one column is pulled LOW at a time during scanning.
        for col in self._cols:#sets the columns as outputs
            GPIO.setup(col, GPIO.OUT)#sets the columns as outputs
            GPIO.output(col, GPIO.HIGH)#sets the columns to HIGH

    def scan(self):
        # Column scanning:
        #   1. Pull one column LOW
        #   2. Read all 4 rows — a LOW reading means that key is pressed
        #      (the pressed key connects its row wire to the driven-LOW column)
        #   3. Restore the column HIGH before moving to the next one
        # Returns a list of all keys currently pressed (supports multi-press).
        pressed = []#list of pressed keys
        for col_idx, col_pin in enumerate(self._cols):#iterates through the columns
            GPIO.output(col_pin, GPIO.LOW)#drives the column LOW
            for row_idx, row_pin in enumerate(self._rows):#iterates through the rows
                if GPIO.input(row_pin) == GPIO.LOW:#if the row is LOW
                    pressed.append(self._keys[row_idx][col_idx])#adds the key to the list
            GPIO.output(col_pin, GPIO.HIGH) # restore before scanning next column
        return pressed

    def get_key(self):#returns a single key if exactly one is pressed
        # Returns None if nothing is pressed or if multiple keys are pressed at once
        # (multi-press state is ambiguous so it is ignored).
        pressed = self.scan()#scans the keypad
        return pressed[0] if len(pressed) == 1 else None#returns the key if exactly one is pressed

    def cleanup(self):#cleans up the keypad
        GPIO.cleanup()
