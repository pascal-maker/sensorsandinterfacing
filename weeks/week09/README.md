# Week 09 — Shift Registers, Displays, LED Matrix, and Keypad

Week 9 uses two chained 74HC595 shift registers to control a four-digit
seven-segment display and an 8×8 LED matrix. It also includes the final matrix
drawing assignment and a separate 4×4 keypad exercise.

## Programs

Run commands from the repository root:

```bash
cd /home/pi/sensorsandinterfacing
```

### Display demonstrations

```bash
python weeks/week09/main.py
```

This demonstrates:

1. One character on one seven-segment digit.
2. The same character on all four digits.
3. One character moving through the digits one at a time.
4. Unique hexadecimal characters on the four digits.
5. Continuous multiplexing in a background thread.
6. Passing new strings through a queue.
7. Counter methods.
8. A custom letter-A pattern on the LED matrix.

### LED-matrix drawing assignment

```bash
python weeks/week09/assignment.py
```

The program provides a blinking cursor on the 8×8 matrix. Four buttons move the
cursor, and the joystick click toggles the selected pixel. A toggled pixel stays
on after the cursor moves. Clicking it again erases it.

### Keypad exercise

```bash
python weeks/week09/keypad_test.py
```

The program scans the 4×4 keypad and prints each newly pressed key.

## Current file structure

| File | Responsibility |
|---|---|
| `shift_register.py` | Low-level 74HC595 bit shifting and latching |
| `fourdigit7segmentclass.py` | Four-digit hexadecimal display and counter |
| `displaythread.py` | Background refresh thread and value queue |
| `led_matrix.py` | 8×8 pixel storage and row multiplexing |
| `assignment.py` | Final cursor drawing and erasing program |
| `keypad.py` | Reusable 4×4 keypad scanner |
| `keypad_test.py` | Standalone keypad test |
| `main.py` | Seven-segment and LED-matrix demonstrations |
| `archive/` | Older scripts and overlapping explanations kept for reference |

## Wiring

All pin numbers use BCM numbering.

### Shared shift registers

| Signal | GPIO |
|---|---:|
| DS — serial data | 22 |
| SHCP — shift clock | 17 |
| STCP — storage/latch clock | 27 |

### Matrix assignment controls

| Control | GPIO |
|---|---:|
| Up | 20 |
| Down | 21 |
| Left | 26 |
| Right | 16 |
| Joystick click | 7 |

### Keypad

| Function | GPIO pins |
|---|---|
| Rows | 16, 20, 21, 26 |
| Columns | 19, 13, 6, 5 |

The keypad and matrix assignment reuse several pins, so run them as separate
exercises rather than at the same time.

## Shift-register bit order

The `ShiftRegister` class supports both directions:

```python
ShiftRegister.MSB_TO_LSB
ShiftRegister.LSB_TO_MSB
```

The default is MSB-to-LSB, which is used by the LED bar and seven-segment
display. This board's two-register LED-matrix cascade also works MSB-first; its
main difference is active-low column selection:

```python
shift_register.shift_out_16bit(
    value,
    direction=ShiftRegister.MSB_TO_LSB,
)
```

## Four-digit display API

Create the objects:

```python
from shift_register import ShiftRegister
from fourdigit7segmentclass import FourDigit7Segment

shift_register = ShiftRegister()
display = FourDigit7Segment(shift_register, common_anode=True)
```

The font accepts strings containing `0`–`9`, `A`–`F`, `-`, and spaces.

```python
display.putValue("1A2F")
display.putValue("12", align="LEFT")       # "12  "
display.putValue("12", align="RIGHT")      # "  12"
display.putFilledValue("12")                # "0012"
display.putFilledValue("12", "-", "LEFT") # "12--"
```

Counter methods:

```python
display.setCounter(10)
display.increment()
display.decrement()
```

The physical display requires continuous multiplexing. Use `DisplayThread` when
the main program must perform other work:

```python
from displaythread import DisplayThread

display_thread = DisplayThread(display)
display_thread.start()
display_thread.put("ABCD")

# Always stop the thread before GPIO cleanup or before another display starts
# using the same shift register.
display_thread.stop()
```

## LED-matrix data

`LedMatrix8x8.row_data` contains eight bytes—one byte for every row. Each bit in
a row byte represents one column pixel.

```python
matrix.row_data[3] = 0b00010000
```

Useful methods:

```python
matrix.toggle_pixel(x, y)
matrix.get_pixel(x, y)
matrix.clear()
matrix.refresh_once()
matrix.blank()
```

The matrix is multiplexed one row at a time. Calling `refresh_once()` repeatedly
makes all rows appear illuminated concurrently through persistence of vision.

## Exam reminders

- `<<` moves a bit left and is useful for selecting a digit, row, or pixel.
- `&` masks unwanted bits.
- `|` combines two bit patterns.
- `^` toggles a bit, making the same operation draw and erase a pixel.
- `~value & 0xFF` inverts exactly eight bits for active-low hardware.
- Always stop refresh threads and blank displays before `GPIO.cleanup()`.
- Do not let the seven-segment thread and matrix write to the same shift register
  simultaneously.
