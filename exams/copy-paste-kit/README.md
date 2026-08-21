# Exam Copy Paste Kit

This folder is a small parts bin for Raspberry Pi sensor/display exam questions.
Copy the class files you need, then copy one matching example from `examples/`.

## Usual wiring from your previous work

- ADC address: `0x48`
- Potentiometer channel: `2`
- Joystick X channel: `6`
- Joystick Y channel: `5`
- Joystick button: GPIO `7`
- Separate push button: GPIO `20`
- 74HC595 data/latch/clock pins: GPIO `22`, `27`, `17`

On Raspberry Pi 5, GPIO 7 can conflict with SPI CE1. If the joystick button fails,
disable SPI or move the button pin in the code.

## Files

- `adc_reader.py`: ADS7830/Freenove ADC reader.
- `bcd_input.py`: 4-bit BCD/thumbwheel reader.
- `auto_off_timer.py`: Potentiometer-controlled auto-off/manual timer.
- `joystick.py`: Joystick X/Y plus direction helper.
- `button_toggle.py`: Button with debounced callback and toggle state.
- `csv_logger.py`: CSV writer that flushes immediately.
- `shift_register.py`: 74HC595 helper.
- `seven_segment_display.py`: Multiplexed 3- or 4-digit 7-segment display.
- `led_bar_graph.py`: LED bar graph patterns.
- `led_matrix_8x8.py`: 8x8 matrix refresh thread and graph/cursor helpers.

## Fast puzzle recipes

- Potentiometer + CSV: `examples/pot_csv.py`
- Joystick + CSV + button toggle: `examples/joystick_csv_toggle.py`
- Potentiometer + 3 digit display + CSV + button toggle: `examples/pot_3digit_csv_button.py`
- Potentiometer + LED bar graph + button toggle: `examples/pot_bargraph_toggle.py`
- Joystick + matrix cursor + button toggle + CSV: `examples/joystick_matrix_csv_toggle.py`
- BCD + 4 digit display + button toggle + auto-off + CSV: `examples/bcd_7seg_auto_off_logger.py`

## Common copy-paste order

1. Import and setup GPIO.
2. Make input object: `ADCReader`, `Potentiometer`, or `Joystick`.
3. Make output object: `SevenSegmentDisplay`, `LedBarGraph`, or `LedMatrix8x8`.
4. Make `CSVLogger` if logging is required.
5. Use `try/except KeyboardInterrupt/finally` and call `cleanup()`.
