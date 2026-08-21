# BCD 7-Segment Auto-Off Logger

## Goal

Build a Raspberry Pi program that reads a 4-bit BCD thumbwheel/input, shows the
decimal value on a 4-digit 7-segment display, turns the display on/off with a
button, uses a potentiometer to control auto-off time, and logs active values to
CSV.

## Hardware

- BCD pins, LSB to MSB: GPIO 16, 20, 21, 26
- Toggle button: GPIO 7
- 74HC595 data pin: GPIO 22
- 74HC595 latch pin: GPIO 27
- 74HC595 clock pin: GPIO 17
- ADS7830 address: 0x48
- Potentiometer ADC channel: 4

## Required behavior

- Read the BCD input as a decimal value from 0 to 15.
- When the BCD value changes, turn the display on and show the new value.
- Pressing the button toggles the display on/off.
- The potentiometer sets the auto-off time:
  - low to middle values map roughly from 5 to 30 seconds
  - middle to high values map roughly from 30 to 60 seconds
  - very high values mean manual mode, so no auto-off
- While the display is on, append one CSV row per second:
  - timestamp
  - BCD value
  - display state
  - auto-off setting
- On Ctrl+C, blank the display, close the CSV file, close I2C, and clean GPIO.

## Clean version

Use `main.py` for the full refactored solution. It separates the assignment into
small classes:

- `BcdInput`: reads the four BCD bits and combines them into one value.
- `AutoOffControl`: converts potentiometer readings into auto-off seconds.
- `FourDigitDisplay`: controls the 74HC595 and 7-segment display.
- `CsvLogger`: writes flushed CSV rows.
- `BcdSevenSegmentApp`: coordinates the full application loop.

## Exam copy order

If you need to recreate this quickly in an exam, copy these pieces first:

1. `BCDInput`
2. `AutoOffTimer`
3. `ShiftRegister`
4. `SevenSegmentDisplay`
5. `ButtonToggle`
6. `CSVLogger`
7. the main loop from `exam_copy_paste_kit/examples/bcd_7seg_auto_off_logger.py`
