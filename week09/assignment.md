# Week 09 Assignment: LED Matrix Interfacing & Multiplexing

## Objective
The goal of this assignment is to interface a Raspberry Pi with an **8x8 LED Matrix** using a **74HC595 Shift Register**. You will learn how to overcome GPIO limitations using serial-to-parallel conversion and how to display complex patterns using **Multiplexing** and **Persistence of Vision (POV)**.
ou need to build two reusable display classes using your existing ShiftRegister class.

Part 1: 4-digit 7-segment display

Goal:

Use 2 shift registers:
- one controls segments A B C D E F G DP
- one controls digits DIG1 DIG2 DIG3 DIG4

You must learn:

segments byte = what character to show
digit byte    = where to show it
16-bit value  = digit byte << 8 | segments byte

Because it is multiplexing, you must keep refreshing:

show digit 1 briefly
show digit 2 briefly
show digit 3 briefly
show digit 4 briefly
repeat fast
Part 2: LED matrix

Goal:

Use 2 shift registers:
- one controls rows
- one controls columns

You must learn:

row byte = active row
col byte = LEDs in that row
16-bit value = row byte << 8 | col byte

For your LED matrix, the teacher says you may need:

LSB_TO_MSB
---

## 1. Hardware Requirements
*   1x Raspberry Pi
*   1x 74HC595 Shift Register
*   1x 8x8 LED Matrix (Common Anode recommended)
*   5x Pushbuttons or 1x Joystick (Up, Down, Left, Right, Click)
*   Jumper wires and Breadboard

---

## 2. Wiring Diagram (Default Configuration)

### Shift Register to Raspberry Pi
| 74HC595 Pin | Name | GPIO Pin (BCM) |
| :--- | :--- | :--- |
| 14 | DS (Data) | 22 |
| 12 | STCP (Latch) | 17 |
| 11 | SHCP (Clock) | 27 |

### Joystick/Buttons to Raspberry Pi
| Button | GPIO Pin (BCM) |
| :--- | :--- |
| UP | 5 |
| DOWN | 6 |
| LEFT | 13 |
| RIGHT | 19 |
| CLICK | 7 |

---

## 3. Core Concepts

### A. Serial-to-Parallel Conversion
Since an 8x8 matrix requires 16 pins (8 rows, 8 columns) to control, using direct GPIO would waste almost all of the Pi's pins. The **74HC595 Shift Register** allows us to send data serially (one bit at a time) and output it in parallel (8 bits at once). By daisy-chaining two registers, we can control all 16 pins using only **3 GPIO pins**.

### B. Multiplexing
In an 8x8 matrix, all LEDs in a row share a common positive (anode) or negative (cathode) connection. To show a full image, we:
1.  Set the pattern for **Row 1**.
2.  Turn **Row 1** ON.
3.  Wait a very short time (e.g., 1ms).
4.  Turn **Row 1** OFF.
5.  Repeat for Rows 2 through 8.

### C. Persistence of Vision (POV)
By cycling through the rows faster than 60Hz, the human brain merges the individual row flashes into a single, steady 8x8 image.

---

## 4. Software Tasks

### Task 1: The Driver (`shift_register.py`)
Implement a class that handles the low-level bit-banging:
*   `shift_byte_out(byte)`: Sends 8 bits to the DS pin, pulsing SHCP for each bit.
*   `shift_out_16bit(value)`: Sends two bytes and then pulses STCP to update the display.

### Task 2: The Display Logic (`led_matrix.py`)
Create a class to manage the 8x8 grid:
*   `toggle_pixel(x, y)`: Flips the state of a specific LED in a memory array.
*   `refresh_once()`: Performs one full scan of all 8 rows.

### Task 3: The Interaction (`week09main.py`)
Write a main loop that:
1.  Checks the joystick inputs to move a virtual cursor.
2.  Blinks the cursor every 300ms using a timer.
3.  Toggles a pixel when the joystick is clicked.
4.  Continuously calls `refresh_once()` to keep the LEDs lit.

---

## 5. Verification
1.  Run the code: `python3 week09main.py`
2.  Verify you can move the blinking dot using the buttons.
3.  Verify that clicking the joystick "paints" a dot on the matrix.
4.  The matrix should not have visible flickering (if flickering is present, reduce the `time.sleep` in the refresh function).
