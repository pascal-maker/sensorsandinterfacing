import time
from keypad import Keypad4x4

def main():
    # Create the keypad object — this sets up all GPIO pins (rows as inputs, cols as outputs)
    keypad = Keypad4x4()
    print("Keypad ready — press keys (Ctrl+C to exit)")

    last_key = None  # tracks the previously seen key so we only print on state changes

    try:
        while True:
            # scan() drives each column LOW in turn and reads all rows.
            # get_key() returns the single pressed key, or None if nothing / multiple pressed.
            # Example: pressing '1' drives col GPIO 19 LOW → row GPIO 16 reads LOW → returns '1'
            key = keypad.get_key()

            # Only print when the key state changes — avoids flooding the terminal
            # while a key is held down. When the key is released, key becomes None
            # and last_key resets, ready for the next press.
            if key != last_key:
                if key is not None:
                    print(f"Key pressed: {key}")
                last_key = key

            time.sleep(0.05)  # 50 ms poll rate — fast enough to catch short presses

    except KeyboardInterrupt:
        # Ctrl+C exits cleanly instead of crashing with a traceback
        print("Exiting...")
    finally:
        # Always runs — restores all GPIO pins to their default state
        keypad.cleanup()

if __name__ == "__main__":
    main()
