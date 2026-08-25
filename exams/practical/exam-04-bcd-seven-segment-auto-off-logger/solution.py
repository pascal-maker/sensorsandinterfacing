import csv
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Helpful on Raspberry Pi 5 when RPi.GPIO is provided by rpi-lgpio.
os.environ.setdefault("RPI_LGPIO_CHIP", "0")

try:
    from RPi import GPIO
except ImportError as exc:
    raise SystemExit("Run this script on a Raspberry Pi with RPi.GPIO installed.") from exc

try:
    import smbus
except ImportError:
    import smbus2 as smbus


# Frozen dataclasses keep all hardware settings together and prevent accidental
# changes to GPIO pins, I2C addresses, and timing values while the app is running.
@dataclass(frozen=True)
class BcdConfig:
    """Four active-low input pins ordered from least to most significant bit."""
    pins: tuple[int, int, int, int] = (16, 20, 21, 26)
    active_low: bool = True


@dataclass(frozen=True)
class ButtonConfig:
    """Push-button pin and software debounce interval."""
    pin: int = 7
    debounce_ms: int = 250


@dataclass(frozen=True)
class ShiftRegisterConfig:
    """74HC595 pins and four-digit display characteristics."""
    data_pin: int = 22
    clock_pin: int = 17
    latch_pin: int = 27
    refresh_delay: float = 0.001
    common_anode: bool = True


@dataclass(frozen=True)
class AdcConfig:
    """ADS7830 potentiometer settings used to calculate auto-off time."""
    address: int = 0x48
    channel: int = 4
    read_interval: float = 0.2
    manual_threshold: int = 250


@dataclass(frozen=True)
class LoggerConfig:
    """CSV destination and interval between logged samples."""
    path: Path = Path(__file__).resolve().parent / "data" / "bcd_values.csv"
    interval: float = 1.0


# Each bit represents one physical segment of a seven-segment digit.
SEG_A = 1 << 0
SEG_B = 1 << 1
SEG_C = 1 << 2
SEG_D = 1 << 3
SEG_E = 1 << 4
SEG_F = 1 << 5
SEG_G = 1 << 6

# Combine segment bits to describe how decimal characters are drawn.
COMMON_CATHODE_SEGMENTS = {
    "0": SEG_A | SEG_B | SEG_C | SEG_D | SEG_E | SEG_F,
    "1": SEG_B | SEG_C,
    "2": SEG_A | SEG_B | SEG_D | SEG_E | SEG_G,
    "3": SEG_A | SEG_B | SEG_C | SEG_D | SEG_G,
    "4": SEG_B | SEG_C | SEG_F | SEG_G,
    "5": SEG_A | SEG_C | SEG_D | SEG_F | SEG_G,
    "6": SEG_A | SEG_C | SEG_D | SEG_E | SEG_F | SEG_G,
    "7": SEG_A | SEG_B | SEG_C,
    "8": SEG_A | SEG_B | SEG_C | SEG_D | SEG_E | SEG_F | SEG_G,
    "9": SEG_A | SEG_B | SEG_C | SEG_D | SEG_F | SEG_G,
    " ": 0,
}

# One digit-select bit activates one of the four multiplexed positions.
DIGIT_SELECT = (1 << 0, 1 << 1, 1 << 2, 1 << 3)
# ADS7830 command bytes for analog channels A0 through A7.
ADC_COMMANDS = (0x84, 0xC4, 0x94, 0xD4, 0xA4, 0xE4, 0xB4, 0xF4)


class BcdInput:
    """Read four GPIO inputs as one binary-coded-decimal value."""
    def __init__(self, config: BcdConfig) -> None:
        self.config = config

    def setup(self) -> None:
        for pin in self.config.pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def read_value(self) -> int:
        """Combine the four input bits into an integer from 0 through 15."""
        value = 0
        for bit_position, pin in enumerate(self.config.pins):
            raw = GPIO.input(pin)
            # Pull-up inputs are active-low: a grounded/LOW input means bit 1.
            bit = 1 - raw if self.config.active_low else raw
            # Shift the bit to its correct binary position and merge it.
            value |= bit << bit_position
        return value


class AutoOffControl:
    """Map potentiometer A4 to an automatic display shutoff duration."""
    def __init__(self, bus, config: AdcConfig) -> None:
        self.bus = bus
        self.config = config
        self.seconds: float | None = 5.0

    def read_raw(self) -> int:
        if not 0 <= self.config.channel < len(ADC_COMMANDS):
            raise ValueError("ADC channel must be between 0 and 7")
        return self.bus.read_byte_data(self.config.address, ADC_COMMANDS[self.config.channel])

    def update_from_potentiometer(self) -> int:
        raw_value = self.read_raw()
        self.seconds = self.raw_to_seconds(raw_value)
        return raw_value

    def raw_to_seconds(self, raw_value: int) -> float | None:
        """Scale ADC values to 5–60 seconds, or None for manual mode."""
        # Values at the top of the potentiometer range disable automatic off.
        if raw_value >= self.config.manual_threshold:
            return None

        # The lower half scales linearly from 5 to 30 seconds.
        if raw_value <= 128:
            return 5.0 + (raw_value / 128.0) * 25.0

        # The remaining automatic range scales from 30 to 60 seconds.
        scale = (raw_value - 128) / (self.config.manual_threshold - 128)
        return 30.0 + scale * 30.0


class FourDigitDisplay:
    """Multiplex a four-digit seven-segment display through two 74HC595s."""
    def __init__(self, config: ShiftRegisterConfig) -> None:
        self.config = config

    def setup(self) -> None:
        GPIO.setup(self.config.data_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.config.clock_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.config.latch_pin, GPIO.OUT, initial=GPIO.LOW)

    def show_number_once(self, value: int) -> None:
        """Refresh every digit once; the main loop repeats this continuously."""
        text = str(value).rjust(4)
        for digit_index, char in enumerate(text):
            self.show_digit(digit_index, char)
            time.sleep(self.config.refresh_delay)

    def show_digit(self, digit_index: int, char: str) -> None:
        digit_byte = DIGIT_SELECT[digit_index]
        self.write_16_bits((digit_byte << 8) | self.segment_byte(char))

    def blank(self) -> None:
        self.write_16_bits(0x0000)

    def segment_byte(self, char: str) -> int:
        pattern = COMMON_CATHODE_SEGMENTS.get(str(char), 0)
        # Common-anode displays use inverted logic: zero switches a segment on.
        return (~pattern & 0xFF) if self.config.common_anode else pattern

    def write_16_bits(self, value: int) -> None:
        """Shift digit-selection and segment bytes into the chained registers."""
        value &= 0xFFFF
        low_byte = value & 0xFF
        high_byte = (value >> 8) & 0xFF

        # Keep outputs unchanged while shifting, then latch both new bytes.
        GPIO.output(self.config.latch_pin, GPIO.LOW)
        self.write_byte(low_byte)
        self.write_byte(high_byte)
        GPIO.output(self.config.latch_pin, GPIO.HIGH)

    def write_byte(self, value: int) -> None:
        # This board expects each byte least-significant bit first.
        for bit_position in range(8):
            bit = (value >> bit_position) & 1
            GPIO.output(self.config.data_pin, bit)
            self.pulse_clock()

    def pulse_clock(self) -> None:
        GPIO.output(self.config.clock_pin, GPIO.HIGH)
        time.sleep(0.000001)
        GPIO.output(self.config.clock_pin, GPIO.LOW)
        time.sleep(0.000001)


class CsvLogger:
    """Append timestamped display readings to a CSV file."""
    def __init__(self, config: LoggerConfig) -> None:
        self.config = config
        self.file = None
        self.writer = None

    def open(self) -> None:
        # Create the data directory automatically and write a header only once.
        self.config.path.parent.mkdir(parents=True, exist_ok=True)
        is_new = not self.config.path.exists() or self.config.path.stat().st_size == 0
        self.file = self.config.path.open("a", newline="", encoding="utf-8")
        self.writer = csv.writer(self.file)

        if is_new:
            self.writer.writerow(["timestamp", "bcd_value", "display_on", "auto_off_seconds"])
            self.file.flush()

    def log(self, bcd_value: int, display_on: bool, auto_off_seconds: float | None) -> None:
        if self.writer is None or self.file is None:
            raise RuntimeError("CSV logger is not open")

        auto_off_text = "manual" if auto_off_seconds is None else f"{auto_off_seconds:.2f}"
        self.writer.writerow(
            [
                datetime.now().isoformat(timespec="seconds"),
                bcd_value,
                int(display_on),
                auto_off_text,
            ]
        )
        self.file.flush()

    def close(self) -> None:
        if self.file is not None:
            self.file.flush()
            self.file.close()
            self.file = None
            self.writer = None


class BcdSevenSegmentApp:
    """Coordinate GPIO events, display refresh, ADC timing, and CSV logging."""
    def __init__(self) -> None:
        self.bcd_config = BcdConfig()
        self.button_config = ButtonConfig()
        self.adc_config = AdcConfig()
        self.logger_config = LoggerConfig()

        self.bus = None
        self.bcd = BcdInput(self.bcd_config)
        self.display = FourDigitDisplay(ShiftRegisterConfig())
        self.auto_off = None
        self.logger = CsvLogger(self.logger_config)

        self.display_on = False
        self.current_bcd_value = 0
        self.auto_off_deadline: float | None = None
        self.last_pot_read = 0.0
        self.last_log_time = 0.0

    def setup(self) -> None:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        self.display.setup()
        self.bcd.setup()
        GPIO.setup(self.button_config.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.bus = smbus.SMBus(1)
        self.auto_off = AutoOffControl(self.bus, self.adc_config)
        self.logger.open()

        self.current_bcd_value = self.bcd.read_value()
        self.auto_off.update_from_potentiometer()
        self.setup_callbacks()

    def setup_callbacks(self) -> None:
        # A falling edge toggles the active-low push button once per press.
        GPIO.add_event_detect(
            self.button_config.pin,
            GPIO.FALLING,
            callback=self.toggle_display,
            bouncetime=self.button_config.debounce_ms,
        )

        # Watch both edges because every BCD switch can change from 0 to 1 or
        # from 1 to 0. A changed BCD value also switches the display back on.
        for pin in self.bcd_config.pins:
            GPIO.add_event_detect(
                pin,
                GPIO.BOTH,
                callback=self.on_bcd_changed,
                bouncetime=self.button_config.debounce_ms,
            )

    def run(self) -> None:
        print("BCD 7-segment exam program started.")
        print(f"CSV logging to: {self.logger_config.path}")
        print("Press Ctrl+C to stop.")

        try:
            while True:
                now = time.time()
                # These small non-blocking updates share one main loop. Display
                # refresh happens every pass; slower ADC/CSV work uses timers.
                self.update_auto_off_if_due(now)
                self.turn_off_if_deadline_passed(now)
                self.refresh_display_or_wait()
                self.log_if_due(now)

        except KeyboardInterrupt:
            print("\nStopped by user.")

        finally:
            self.cleanup()

    def update_auto_off_if_due(self, now: float) -> None:
        # Avoid reading I2C on every very-fast multiplexing iteration.
        if now - self.last_pot_read < self.adc_config.read_interval:
            return

        if self.auto_off is None:
            raise RuntimeError("Auto-off control is not initialized")

        self.auto_off.update_from_potentiometer()
        self.last_pot_read = now

    def turn_off_if_deadline_passed(self, now: float) -> None:
        # A None deadline represents manual mode and therefore never expires.
        if self.display_on and self.auto_off_deadline is not None and now >= self.auto_off_deadline:
            self.turn_display_off()
            print("Display auto-off")

    def refresh_display_or_wait(self) -> None:
        if self.display_on:
            # Rapid repetition makes all four multiplexed digits appear on.
            self.display.show_number_once(self.current_bcd_value)
        else:
            time.sleep(0.02)

    def log_if_due(self, now: float) -> None:
        # Record only while the display is active and only at the set interval.
        if now - self.last_log_time < self.logger_config.interval:
            return

        if self.display_on and self.auto_off is not None:
            self.logger.log(self.current_bcd_value, self.display_on, self.auto_off.seconds)

        self.last_log_time = now

    def toggle_display(self, channel=None) -> None:
        if self.display_on:
            self.turn_display_off()
        else:
            self.turn_display_on()

        print(f"Display {'ON' if self.display_on else 'OFF'}")

    def on_bcd_changed(self, channel=None) -> None:
        new_value = self.bcd.read_value()
        if new_value == self.current_bcd_value:
            return

        self.current_bcd_value = new_value
        self.turn_display_on()
        print(f"BCD changed: {self.current_bcd_value}")

    def turn_display_on(self) -> None:
        self.display_on = True
        self.schedule_auto_off()

    def turn_display_off(self) -> None:
        self.display_on = False
        self.auto_off_deadline = None
        self.display.blank()

    def schedule_auto_off(self) -> None:
        if self.auto_off is None or self.auto_off.seconds is None:
            # No deadline means the user must switch the display off manually.
            self.auto_off_deadline = None
        else:
            self.auto_off_deadline = time.time() + self.auto_off.seconds

    def cleanup(self) -> None:
        """Close the file and I2C bus, blank the display, and release GPIO."""
        self.logger.close()

        try:
            self.display.blank()
        except Exception:
            pass

        if self.bus is not None:
            try:
                self.bus.close()
            except AttributeError:
                pass

        GPIO.cleanup()
        print("Cleaned up GPIO, I2C, and CSV file.")


def main() -> None:
    app = BcdSevenSegmentApp()
    app.setup()
    app.run()


if __name__ == "__main__":
    main()
