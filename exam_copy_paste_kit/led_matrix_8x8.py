import threading
import time


class LedMatrix8x8:
    """8x8 matrix helper. Column select is high; row LEDs are active-low."""

    def __init__(self, shift_register, refresh_seconds=0.001):
        self.shift_register = shift_register
        self.refresh_seconds = refresh_seconds
        self.columns = [0x00] * 8
        self.enabled = True
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._refresh_loop, daemon=True)

    def start(self):
        self.thread.start()

    def set_enabled(self, enabled):
        with self.lock:
            self.enabled = enabled

    def clear(self):
        self.shift_register.write_16_bits(0x00FF)

    def set_columns(self, columns):
        with self.lock:
            self.columns = list(columns[:8]) + [0x00] * max(0, 8 - len(columns))

    def push_graph_value(self, value, max_value=255):
        led_count = round((value / max_value) * 8)
        led_count = max(0, min(8, led_count))
        column_bits = (1 << led_count) - 1 if led_count else 0x00

        with self.lock:
            self.columns.pop(0)
            self.columns.append(column_bits)

        return led_count

    def show_cursor(self, x, y):
        x = max(0, min(7, int(x)))
        y = max(0, min(7, int(y)))
        columns = [0x00] * 8
        columns[x] = 1 << y
        self.set_columns(columns)

    def _refresh_loop(self):
        column_select = [1 << column for column in range(8)]

        while not self.stop_event.is_set():
            with self.lock:
                enabled = self.enabled
                columns = list(self.columns)

            if not enabled:
                self.clear()
                time.sleep(0.05)
                continue

            for x, column_bits in enumerate(columns):
                data_word = (column_select[x] << 8) | (~column_bits & 0xFF)
                self.shift_register.write_16_bits(data_word)
                time.sleep(self.refresh_seconds)

        self.clear()

    def cleanup(self):
        self.stop_event.set()
        self.thread.join(timeout=1)
        self.clear()
