import RPi.GPIO as GPIO
import time

# --- Pin mapping (BCM numbering) ---
# Rows are inputs held HIGH by 1kΩ pull-up resistors on the PCB.
# When a key is pressed it physically connects that row wire to the driven column,
# pulling the row LOW — that's how the Pi detects which key was pressed.
# This board's keypad connector is physically reversed relative to the cable's
# printed pin order. Listing both groups in reverse maps the physical top-left
# key to "1" instead of the bottom-right key "D".
ROWS = [26, 21, 20, 16]   # input side of the keypad connector
COLS = [5, 6, 13, 19]     # output side of the keypad connector

# The connector's electrical row/column axes are transposed relative to the
# printed keypad. This lookup is therefore the transpose of the printed layout;
# the user still receives 123A / 456B / 789C / *0#D.
KEYS = [
    ['1', '4', '7', '*'],
    ['2', '5', '8', '0'],
    ['3', '6', '9', '#'],
    ['A', 'B', 'C', 'D'],
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
        """Scan every row/column intersection and return all pressed keys."""
        # A 4x4 keypad contains 16 switches arranged as four rows crossing four
        # columns. Pressing a key electrically joins one row to one column.
        # Scanning lets eight wires identify 16 switches without giving every
        # key its own GPIO input.

        # All row inputs normally read HIGH because they use pull-up resistors.
        # We test one column at a time by temporarily driving that column LOW.
        # If a key in that column is held, its connected row is pulled LOW too.
        pressed = []

        # enumerate() supplies both the list position and its GPIO pin. The
        # positions later select the corresponding entry in the KEYS table.
        for col_idx, col_pin in enumerate(self._cols):
            # Select only this column. Every other column remains HIGH.
            GPIO.output(col_pin, GPIO.LOW)

            # Allow the voltage to settle before sampling the row inputs. This
            # short delay helps avoid false readings immediately after switching.
            time.sleep(0.001)

            for row_idx, row_pin in enumerate(self._rows):
                # LOW means the selected column is connected to this row, so
                # the key at their intersection is physically being pressed.
                if GPIO.input(row_pin) == GPIO.LOW:
                    pressed.append(self._keys[row_idx][col_idx])

            # Deselect this column before testing the next one. Leaving it LOW
            # could create incorrect readings when another column is scanned.
            GPIO.output(col_pin, GPIO.HIGH)

        # Usually this is empty or contains one key. A list also lets scan()
        # report multiple simultaneous presses for programs that need them.
        return pressed

    def get_key(self):
        """Return one unambiguous pressed key, or None."""
        pressed = self.scan()

        # Exactly one detected key is safe to return. No key and multiple keys
        # both return None because this simple demo expects one press at a time.
        return pressed[0] if len(pressed) == 1 else None

    def cleanup(self):
        """Restore GPIO pins to their default state when the program ends."""
        GPIO.cleanup()


def run_demo():
    """Print each debounced key once; used by both runnable keypad scripts."""
    keypad = Keypad4x4()
    print("Keypad ready — press keys (Ctrl+C to exit)")
    print("Layout: 123A / 456B / 789C / *0#D")

    # Mechanical contacts bounce between connected and disconnected for a short
    # time. These variables require a reading to remain unchanged for 50 ms.
    stable_key = None       # Last accepted, debounced key state.
    candidate_key = None    # New raw state that might become stable.
    candidate_since = time.monotonic()  # When the candidate first appeared.
    debounce_seconds = 0.05  # 50 ms is long enough to filter typical bounce.

    try:
        while True:
            # raw_key is the immediate electrical result. It may briefly jump
            # between a character and None while a physical contact bounces.
            raw_key = keypad.get_key()

            # monotonic() measures elapsed time and cannot jump if the system
            # clock is corrected while this program is running.
            now = time.monotonic()

            # When the raw reading changes, begin timing a new candidate.
            if raw_key != candidate_key:
                candidate_key = raw_key
                candidate_since = now

            # Accept the candidate only if:
            #   1. it differs from the last accepted state, and
            #   2. it has remained unchanged for at least 50 ms.
            if (
                candidate_key != stable_key
                and now - candidate_since >= debounce_seconds
            ):
                stable_key = candidate_key

                # Print only confirmed presses. A confirmed None represents a
                # release; accepting it rearms the next key press but prints
                # nothing. Holding a key therefore produces only one message.
                if stable_key is not None:
                    print(f"Key pressed: {stable_key}")

            # Avoid a busy loop while keeping the keypad responsive.
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nKeypad stopped")
    finally:
        keypad.cleanup()


if __name__ == "__main__":
    run_demo()
