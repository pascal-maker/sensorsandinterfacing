# Reconstructed Practical Exam Assignment

## Title

Potentiometer Data Logger With 8x8 LED Matrix History

## Goal

Build a Raspberry Pi program that reads an analog potentiometer through an ADS7830 ADC, displays the measurements on an 8x8 LED matrix, logs the data to a CSV file, and creates a graph when the program stops.

## Hardware

| Component | Purpose |
|---|---|
| Raspberry Pi | Main controller |
| ADS7830 ADC | Reads the analog potentiometer value |
| Potentiometer | Provides a changing analog input |
| 8x8 LED matrix | Displays recent potentiometer values |
| Shift register | Drives the LED matrix |
| Push button | Toggles the LED matrix on and off |

## Wiring Used In The Refactored Code

| GPIO / Channel | Component |
|---|---|
| ADS7830 channel 4 | Potentiometer input |
| GPIO 22 | Shift register data |
| GPIO 17 | Shift register clock |
| GPIO 27 | Shift register latch |
| GPIO 20 | Push button |

GPIO 20 is used for the button because GPIO 17 is already used as the shift-register clock pin.

## Required Behaviour

1. Read the potentiometer value once every second.
2. The potentiometer value must be in the range `0` to `255`.
3. Convert each value into a vertical column on the 8x8 LED matrix.
4. A low value should light few or no LEDs in the column.
5. A high value should light more LEDs in the column.
6. Each second, shift the previous matrix values left.
7. Insert the newest potentiometer value as the rightmost column.
8. After 8 seconds, the full matrix should show the last 8 readings.
9. Use a button callback to toggle the LED matrix on and off.
10. When the matrix is switched off, clear all LEDs.
11. Log every potentiometer reading to a CSV file.
12. Flush the CSV after every write so data is not lost if the program crashes.
13. When the program exits, save a graph of potentiometer value over time.
14. Clean up GPIO and close the ADC safely on exit.

## Expected Output Files

The program writes output files inside `praticalexam2/data/`.

| File | Purpose |
|---|---|
| `potentiometer_log.csv` | Timestamped raw potentiometer readings |
| `potentiometer_timing.png` | Graph of potentiometer readings over time |

## Program Structure

The solution should separate hardware into reusable classes:

- `Adc.py`: low-level ADS7830 reading
- `Potentiometer.py`: potentiometer wrapper around one ADC channel
- `Shiftregister1.py`: 16-bit shift-register output
- `Ledmatrix.py`: 8x8 LED matrix buffer and drawing
- `Button.py`: GPIO button callback handling
- `Csvlogger.py`: CSV logging with immediate flush
- `main_potentiometer_matrix final.py`: final application logic

## Inferred Exam Question

Create a Python application for the Raspberry Pi that uses a potentiometer and an 8x8 LED matrix. The application must read the potentiometer through an ADC every second and display the value as a scrolling graph on the LED matrix. Use a push button with a callback to turn the matrix display on or off. Log all potentiometer values to a CSV file without losing data on crashes. When the program is stopped, generate a PNG graph of the recorded values over time.
