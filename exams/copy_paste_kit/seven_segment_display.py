import threading
import time


class SevenSegmentDisplay:
    """Multiplexed common-anode 7-segment display through two 74HC595 chips."""

    NUMBER_PATTERNS = {
        "0": 0xC0,
        "1": 0xF9,
        "2": 0xA4,
        "3": 0xB0,
        "4": 0x99,
        "5": 0x92,
        "6": 0x82,
        "7": 0xF8,
        "8": 0x80,
        "9": 0x90,
        "-": 0xBF,
        " ": 0xFF,
    }

    DIGIT_SELECT = [0x01, 0x02, 0x04, 0x08]

    def __init__(self, shift_register, digits=3, refresh_seconds=0.0002, blank_seconds=0.00005):
        self.shift_register = shift_register
        self.digits = digits
        self.refresh_seconds = refresh_seconds
        self.blank_seconds = blank_seconds
        self.text = "0" * digits
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._refresh_loop, daemon=True)

    def start(self):
        self.thread.start()

    def show_number(self, value):
        value = max(0, min((10 ** self.digits) - 1, int(value)))
        self.show_text(str(value).zfill(self.digits))

    def show_text(self, text):
        text = str(text)[-self.digits:].rjust(self.digits)
        with self.lock:
            self.text = text

    def _show_one_digit(self, index, character):
        digit_select = self.DIGIT_SELECT[index]
        pattern = self.NUMBER_PATTERNS.get(character, 0xFF)
        self.shift_register.write_16_bits((digit_select << 8) | pattern)
        time.sleep(self.refresh_seconds)
        self.shift_register.write_16_bits((digit_select << 8) | 0xFF)
        time.sleep(self.blank_seconds)

    def _refresh_loop(self):
        while not self.stop_event.is_set():
            with self.lock:
                text = self.text

            for index, character in enumerate(text):
                self._show_one_digit(index, character)

        self.clear()

    def clear(self):
        self.shift_register.write_16_bits(0x00FF)

    def cleanup(self):
        self.stop_event.set()
        self.thread.join(timeout=1)
        self.clear()
