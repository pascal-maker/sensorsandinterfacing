# ButtonService — debounced digital input for a push button wired with a pull-up resistor.
#
# Wiring assumption: button connects GPIO pin to GND.
# The pull-up means the pin reads HIGH when open and LOW when pressed.
# Software debouncing filters out the brief voltage noise ("bounce") that occurs
# every time mechanical contacts make or break — without it you'd see multiple
# press/release events per physical press.
from __future__ import annotations

import threading
import time
from typing import Callable

from .gpio_compat import GPIO  # relative import keeps hardware/ self-contained


class ButtonService:
    def __init__(
        self,
        pin: int,
        poll_interval: float = 0.02,       # how often is_pressed() samples the pin (seconds)
        debounce_seconds: float = 0.05,    # signal must be stable for this long before accepted
    ) -> None:
        self.pin = pin
        self.poll_interval = poll_interval
        self.debounce_seconds = debounce_seconds

        self._lock = threading.Lock()                  # protects shared state when polled from multiple threads
        self._last_raw_pressed: bool | None = None     # previous raw reading (before debounce)
        self._stable_pressed = False                   # debounced (confirmed) state exposed to callers
        self._last_raw_change = time.monotonic()       # timestamp of the last raw state change

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)                                        # use Broadcom pin numbers
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)      # enable internal pull-up

    def is_pressed(self) -> bool:
        """Return the debounced button state. Safe to call from any thread."""
        with self._lock:
            raw = GPIO.input(self.pin) == GPIO.LOW   # LOW == pressed (pull-up wiring)
            now = time.monotonic()

            if self._last_raw_pressed is None:
                # First call — initialise all state from the current reading
                self._last_raw_pressed = raw
                self._stable_pressed = raw
                self._last_raw_change = now
                return self._stable_pressed

            if raw != self._last_raw_pressed:
                # Raw state changed — reset the debounce timer, don't update stable yet
                self._last_raw_pressed = raw
                self._last_raw_change = now
            elif self._stable_pressed != raw:
                # Raw state held long enough — promote to stable
                if (now - self._last_raw_change) >= self.debounce_seconds:
                    self._stable_pressed = raw

            return self._stable_pressed

    def cleanup(self) -> None:
        """Release the GPIO pin. Call this on shutdown."""
        with self._lock:
            GPIO.cleanup(self.pin)

    def monitor(self, on_press: Callable[[], None], on_release: Callable[[], None]) -> None:
        """Blocking loop that fires callbacks on press and release. Cleans up on exit."""
        was_pressed = False
        try:
            while True:
                pressed = self.is_pressed()
                if pressed and not was_pressed:
                    on_press()
                if not pressed and was_pressed:
                    on_release()
                was_pressed = pressed
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
