# Week 09: LED Matrix and 7-Segment Display Interfacing

This project demonstrates how to control complex displays using a **74HC595 Shift Register** and **Multiplexing** techniques on a Raspberry Pi.

---

## 1. Core Hardware Concepts

### The 74HC595 Shift Register
The Shift Register allows us to control many output pins using only 3 GPIO pins from the Raspberry Pi:
*   **DS (Data):** Sends bits (0 or 1) one by one.
*   **SHCP (Shift Clock):** Tells the register to "move over" and accept the next bit.
*   **STCP (Latch Clock):** Tells the register to "display" all the stored bits on its output pins.

### Multiplexing
Since we are controlling multiple digits (7-segment) or rows (LED Matrix) that share the same data lines, we use **Multiplexing**. This involves switching between digits/rows so fast that the human eye perceives them as all being on at once (**Persistence of Vision**).

---

## 2. Software Architecture

The project is organized into modular classes for clean and reusable code:

### `ShiftRegister` Class
Handles the low-level "pulsing" of pins to move data into the hardware.
```python
def shift_byte_out(self, byte, direction=MSB_TO_LSB):
    for i in bit_range:
        bit = (byte >> i) & 1
        GPIO.output(DS, bit)
        self.pulse(SHCP)
```

### `LEDMatrix8x8` Class
Translates an 8x8 pattern into row and column bytes for the matrix.
```python
def refresh_once(self):
    for row_index, col_byte in enumerate(self.pattern):
        row_byte = self.ROWS[row_index]
        value = (row_byte << 8) | col_byte
        self._sr.shift_out_16bit(value)
```

### `DisplayThread` Class
Uses Python's `threading` module to keep the display refreshing in the background while the main program performs other tasks.
```python
def _run(self):
    while not self._stop_event.is_set():
        # Check for new data in the queue
        # Then refresh the display hardware
        self.display.refresh_once()
```

---

## 3. How to Use the System

In `main.py`, we initialize the hardware and start the background thread:

```python
# 1. Initialize hardware
shiftregister = ShiftRegister()
display = FourDigit7Segment(shiftregister)

# 2. Start the background refresh thread
display_thread = DisplayThread(display)
display_thread.start()

# 3. Simply "put" values to show them!
display_thread.put("1234")
```

---

## 4. Key Takeaways
1.  **Pin Efficiency:** Shift registers save GPIO pins.
2.  **Modular Design:** Separating hardware logic (`shiftregister.py`) from display logic (`ledmatrixclass.py`) makes the code easier to debug.
3.  **Threading:** Background threads are essential for multiplexed displays to prevent flickering when the main code is busy.
