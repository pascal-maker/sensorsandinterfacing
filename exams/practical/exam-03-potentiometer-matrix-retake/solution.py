"""Practical exam 3: potentiometer logger with an 8x8 LED matrix.

Read an ADS7830 potentiometer once per second, append each reading to CSV,
and display the latest eight readings as vertical bars. A button toggles the
matrix without stopping data collection.
"""

from collections import deque
import csv
from datetime import datetime
from pathlib import Path
from threading import Event, Lock, Thread
from time import sleep

from RPi import GPIO
import smbus

from shift_register import ShiftRegister


class PotentiometerMatrixLogger:
    """Coordinate ADC sampling, CSV logging, and LED-matrix refresh."""

    ADC_ADDRESS = 0x48
    ADC_COMMAND = 0x94  # ADS7830 channel 2, single-ended input
    BUTTON_PIN = 20
    SAMPLE_INTERVAL = 1.0
    MATRIX_REFRESH_DELAY = 0.001

    def __init__(self, csv_path=None):
        base_dir = Path(__file__).resolve().parent
        self.csv_path = Path(csv_path or base_dir / "data" / "potentiometer-log.csv")
        self.shift_register = ShiftRegister()
        self.i2c = smbus.SMBus(1)
        self.history = deque(maxlen=8)
        self.matrix_enabled = True
        self._state_lock = Lock()
        self._stop_event = Event()
        self._display_thread = Thread(target=self._refresh_matrix, daemon=True)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            self.BUTTON_PIN,
            GPIO.FALLING,
            callback=self.toggle_matrix,
            bouncetime=200,
        )

    @staticmethod
    def value_to_bar(value):
        """Convert an ADC value from 0..255 to an eight-bit vertical bar."""
        led_count = round(max(0, min(255, value)) / 255 * 8)
        return (1 << led_count) - 1 if led_count else 0

    def read_adc(self):
        """Read the configured ADS7830 channel exactly once."""
        return self.i2c.read_byte_data(self.ADC_ADDRESS, self.ADC_COMMAND)

    def record_value(self, value):
        """Add a reading to the bounded matrix history."""
        with self._state_lock:
            self.history.append(self.value_to_bar(value))

    def toggle_matrix(self, _channel):
        """GPIO callback that enables or disables the display."""
        with self._state_lock:
            self.matrix_enabled = not self.matrix_enabled
            enabled = self.matrix_enabled
        if not enabled:
            self.clear_matrix()
        print(f"Matrix {'ON' if enabled else 'OFF'}")

    def clear_matrix(self):
        """Turn every LED off."""
        self.shift_register.shift_out_16_bits(0x00FF)

    def _refresh_matrix(self):
        """Continuously multiplex a snapshot of the latest eight readings."""
        while not self._stop_event.is_set():
            with self._state_lock:
                enabled = self.matrix_enabled
                patterns = list(self.history)

            if not enabled or not patterns:
                self.clear_matrix()
                sleep(self.MATRIX_REFRESH_DELAY)
                continue

            padded_patterns = [0] * (8 - len(patterns)) + patterns
            for column, pattern in enumerate(padded_patterns):
                row_selector = (1 << column) << 8
                column_bits = ~pattern & 0xFF
                self.shift_register.shift_out_16_bits(row_selector | column_bits)
                sleep(self.MATRIX_REFRESH_DELAY)

    def run(self):
        """Run until interrupted, logging a timestamp and value each second."""
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        is_new_file = not self.csv_path.exists() or self.csv_path.stat().st_size == 0
        self._display_thread.start()

        with self.csv_path.open("a", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            if is_new_file:
                writer.writerow(["timestamp", "potentiometer_value"])
                csv_file.flush()

            while not self._stop_event.is_set():
                value = self.read_adc()
                timestamp = datetime.now().isoformat(timespec="seconds")
                writer.writerow([timestamp, value])
                csv_file.flush()
                self.record_value(value)
                print(f"{timestamp}: {value}")
                self._stop_event.wait(self.SAMPLE_INTERVAL)

    def close(self):
        """Stop refresh work and release hardware resources."""
        self._stop_event.set()
        if self._display_thread.is_alive():
            self._display_thread.join(timeout=1)
        self.clear_matrix()
        if hasattr(self.i2c, "close"):
            self.i2c.close()
        GPIO.cleanup()


def main():
    application = PotentiometerMatrixLogger()
    try:
        application.run()
    except KeyboardInterrupt:
        print("\nStopping practical exam 3.")
    finally:
        application.close()


if __name__ == "__main__":
    main()
