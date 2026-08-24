from __future__ import annotations

import threading
import time
from typing import Callable

from gpio_compat import GPIO


class ButtonService:#Button service class
	def __init__(#Constructor
		self,
		pin: int,#Button pin
		poll_interval: float = 0.02,#Button poll interval
		debounce_seconds: float = 0.05,#Button debounce seconds
	) -> None:  #
		self.pin = pin#Set button pin
		self.poll_interval = poll_interval#Set button poll interval
		self.debounce_seconds = debounce_seconds#Set button debounce seconds
		self._lock = threading.Lock()#Create button lock
		self._last_raw_pressed: bool | None = None#Button last raw pressed
		self._stable_pressed = False#Button stable pressed
		self._last_raw_change = time.monotonic()#Button last raw change

		GPIO.setwarnings(False)#Turn off warnings
		GPIO.setmode(GPIO.BCM)#Set button mode to BCM
		GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)#Set button pin to input with pull-up

	def is_pressed(self) -> bool:#Check if button is pressed
		with self._lock: #Lock to prevent race conditions
			raw_pressed = GPIO.input(self.pin) == GPIO.LOW#Check if button is pressed
			now = time.monotonic()#Get current time

			if self._last_raw_pressed is None:#Check if button was not pressed before
				self._last_raw_pressed = raw_pressed#Set last raw pressed to current raw pressed
				self._stable_pressed = raw_pressed#Set stable pressed to current raw pressed
				self._last_raw_change = now#Set last raw change to current time
				return self._stable_pressed

			if raw_pressed != self._last_raw_pressed:#Check if button was pressed before
				self._last_raw_pressed = raw_pressed#Set last raw pressed to current raw pressed
				self._last_raw_change = now#Set last raw change to current time
			elif self._stable_pressed != raw_pressed:#Check if button was pressed for debounce seconds
				if (now - self._last_raw_change) >= self.debounce_seconds:#Check if button was pressed for debounce seconds
					self._stable_pressed = raw_pressed#Set stable pressed to current raw pressed

			return self._stable_pressed#Return stable pressed

	def cleanup(self) -> None:#Cleanup button
		with self._lock: #Lock to prevent race conditions
			GPIO.cleanup(self.pin)#Cleanup button pin
		with self._lock:
			GPIO.cleanup(self.pin)

	def monitor(
		self,
		on_press: Callable[[], None],#Button press callback
		on_release: Callable[[], None],#Button release callback
	) -> None:#Monitor button
		was_pressed = False#Button was pressed

		try:#Try to monitor button
			while True:#Loop to monitor button
				is_pressed = self.is_pressed()#Check if button is pressed

				if is_pressed and not was_pressed:#Check if button was pressed
					on_press()

				if (not is_pressed) and was_pressed:#Check if button was released
					on_release()

				was_pressed = is_pressed#Set last pressed to current pressed
				time.sleep(self.poll_interval)#Wait for poll interval
		except KeyboardInterrupt:#Handle keyboard interrupt
			print("Stopping button reader.")
		finally:
			self.cleanup()


def main() -> None:
	button = ButtonService(pin=26)#Create button service instance
	print(f"Reading button on GPIO{button.pin}. Press Ctrl+C to stop.")#Print button pin
	button.monitor(
		on_press=lambda: print("Button pressed"),#Button press callback
		on_release=lambda: print("Button released"),#Button release callback
	)


if __name__ == "__main__":#Run main function if file is run as a script
	main()
