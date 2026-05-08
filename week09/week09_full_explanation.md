# Week 09 — Full Script Explanations

---

# Script 1 — shift_register.py

## What is a shift register?
The Raspberry Pi doesn't have enough GPIO pins to control 16 LEDs directly.
A shift register solves this: you send data **one bit at a time** over 3 pins,
and it outputs all 16 bits at once on 16 separate pins.

Think of it like a conveyor belt — you place one box at a time on the belt,
and when you press a button, all boxes slide off at once.

## The 3 pins
| Pin | GPIO | Name | Job |
|-----|------|------|-----|
| DS  | 22   | Data | Sends one bit at a time into the register |
| SHCP| 17   | Clock | Each pulse shifts data one position along |
| STCP| 27   | Latch | Copies all stored bits to the outputs at once |

## pulse()
```python
def pulse(self, pin):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(0.000001)   # 1 microsecond
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.000001)
```
Sets a pin HIGH then LOW very briefly.
The 1 microsecond delay gives the chip enough time to register the signal.
Too fast and the chip misses it.
Used for both the clock pin (SHCP) and latch pin (STCP).

## shift_byte_out()
```python
def shift_byte_out(self, byte, direction=MSB_TO_LSB):
    byte &= 0xFF
    for i in bit_range:
        GPIO.output(self.ds, (byte >> i) & 1)
        self.pulse(self.shcp)
```
Sends 8 bits one at a time to the data pin.

**`(byte >> i) & 1` explained:**
```
byte     = 10110010
           76543210  ← bit positions

i=7: 10110010 >> 7 = 00000001  → & 1 = 1  (send 1)
i=6: 10110010 >> 6 = 00000010  → & 1 = 0  (send 0)
i=5: 10110010 >> 5 = 00000101  → & 1 = 1  (send 1)
...
```
`>> i` moves the target bit to position 0.
`& 1` keeps only that last bit, giving exactly 0 or 1.
That single bit is sent to the data pin, then the clock is pulsed.

**MSB vs LSB direction:**
- MSB_TO_LSB: sends bit 7 first down to bit 0 (left to right)
- LSB_TO_MSB: sends bit 0 first up to bit 7 (right to left)
Wrong direction = wrong LEDs light up because the shift register is a chain.

## shift_out_16bit()
```python
def shift_out_16bit(self, value, direction=LSB_TO_MSB):
    value &= 0xFFFF
    msb = (value >> 8) & 0xFF   # upper 8 bits
    lsb = value & 0xFF           # lower 8 bits
    # send lsb first, then msb (or reversed depending on direction)
    self.pulse(self.stcp)        # latch at the very end
```
We have TWO chained 8-bit shift register chips = 16 outputs total.
So we must call shift_byte_out twice — once for each chip.

**Why latch only at the end?**
While bits are being clocked in, the LEDs do not change.
Only when STCP is pulsed do all 16 outputs update simultaneously.
This prevents flickering or partial updates being visible.

---

# Script 2 — led_matrix.py (LedMatrix8x8)

## What is it?
Controls an 8x8 grid of LEDs (64 LEDs total).
Uses the shift register to send row and column data.

## row_data
```python
self.row_data = [0x00] * 8
```
A list of 8 bytes — one byte per row.
Each byte has 8 bits — one bit per column (LED in that row).
```
row_data[0] = 0b00000000  → row 0, all LEDs off
row_data[3] = 0b00000101  → row 3, LEDs at column 0 and 2 are ON
```

## toggle_pixel()
```python
self.row_data[y] ^= (1 << x)
```
`^=` is XOR — flips a single bit.
- If the bit was 0 (LED off) → becomes 1 (LED on)
- If the bit was 1 (LED on) → becomes 0 (LED off)

This is toggle — not just turn on. If you click the same pixel twice it goes
back off.

## get_pixel()
```python
return (self.row_data[y] >> x) & 1
```
Same trick as shift_byte_out:
`>> x` moves the target bit to position 0, `& 1` reads it.
Returns 1 if LED is on, 0 if off.

## refresh_once()
```python
for row in range(8):
    row_byte = 1 << row        # which row to activate
    col_byte = self.row_data[row]  # which LEDs in that row are on

    if cursor_visible and cursor_y == row:
        col_byte ^= (1 << cursor_x)  # temporarily add cursor

    col_byte = ~col_byte & 0xFF    # invert for common anode

    value = (col_byte << 8) | row_byte
    self.shift_register.shift_out_16bit(value, direction=LSB_TO_MSB)
    time.sleep(0.0005)
```
This is **multiplexing** — only one row is ON at a time.
Cycles through all 8 rows at 0.5ms each = full refresh every 4ms = 250Hz.
So fast the eye sees all rows lit simultaneously.

**Why invert col_byte?**
The matrix is common anode — column pins must be LOW (0) to light up.
But row_data stores 1 = on. So we flip all bits to match hardware.
`~col_byte` flips all bits. `& 0xFF` keeps it as a valid 8-bit number.

**How the cursor works without storing it:**
The cursor is never saved in row_data.
Inside refresh_once(), `col_byte ^= (1 << cursor_x)` temporarily flips the
cursor pixel in a local variable before sending to the shift register.
row_data stays unchanged. When cursor_visible is False, the flip doesn't
happen and the cursor disappears. No stored state needed.

## blank()
```python
self.shift_register.shift_out_16bit(0x00FF, direction=LSB_TO_MSB)
```
`0x00FF` = lower 8 bits all HIGH, upper 8 bits all LOW.
Turns off all columns and activates no rows = all LEDs off.

---

# Script 3 — assignment.py (main program)

## What does it do?
A pixel editor on the 8x8 LED matrix.
- Joystick UP/DOWN/LEFT/RIGHT moves a blinking cursor
- Joystick CLICK toggles the pixel at the cursor position ON or OFF
- Works like MS Paint on a tiny LED screen

## GPIO button pins
| Button | GPIO |
|--------|------|
| UP     | 20   |
| DOWN   | 21   |
| LEFT   | 26   |
| RIGHT  | 16   |
| CLICK  | 7    |

All buttons use `pull_up_down=GPIO.PUD_UP` — the pin reads HIGH when not
pressed, LOW when pressed.

## pressed()
```python
return GPIO.input(btn) == GPIO.LOW
```
Returns True when the button is pressed.
LOW = pressed because of the pull-up resistor setup.

## Debounce
```python
if now - last_move > MOVE_DEBOUNCE:  # 0.18 seconds
```
Mechanical buttons physically bounce — they make and break contact several
times in milliseconds when pressed. Without debounce one press registers
multiple times. The 0.18s gap ensures each press counts only once.

## Blink logic
```python
if now - last_blink > BLINK_PERIOD:   # 0.3 seconds
    cursor_visible = not cursor_visible
    last_blink = now
```
Every 0.3 seconds, cursor_visible flips between True and False.
refresh_once() uses cursor_visible to decide whether to draw the cursor.
Result: cursor blinks at ~1.6 times per second.
`BLINK_PERIOD` directly controls the speed.

## Edge detection (joystick click)
```python
if last_joy_state == GPIO.HIGH and joy_state == GPIO.LOW:
    matrix.toggle_pixel(cursor_x, cursor_y)
```
This detects a **falling edge** — the moment the button goes from released
(HIGH) to pressed (LOW). Checking both old and new state means the pixel
toggles exactly once per click, not on every loop while held down.

## last_joy_state
```python
last_joy_state = GPIO.HIGH  # starts as released
```
Stores the joystick state from the previous loop iteration.
Compared with the current state to detect the moment of press.

## Cursor reset on move
```python
if moved:
    cursor_visible = True
    last_blink = now
```
When you move the cursor it immediately becomes visible and the blink timer
resets. Stops the cursor from being invisible right after you move it.

## finally block
```python
finally:
    matrix.blank()
    GPIO.cleanup()
```
Runs no matter what — even if an error occurs.
Blanks the display and releases all GPIO pins cleanly.

---

# Script 4 — fourdigit7segmentclass.py (FourDigit7Segment)

## What is it?
Controls a 4-digit 7-segment display (like a calculator or microwave display).
Uses the shift register to send segment and digit data.

## Segment layout
```
 AAA
F   B
F   B
 GGG
E   C
E   C
 DDD   DP = decimal point
```
Each segment is one bit in a byte:
```
bit: 7   6   5   4   3   2   1   0
     DP  G   F   E   D   C   B   A
```

## Segment constants
```python
A = 1<<0   # 0b00000001
B = 1<<1   # 0b00000010
...
G = 1<<6   # 0b01000000
```
Each constant places a single 1 bit at a unique position.
Combined with `|` to turn on multiple segments:
```
digit 1 = B|C = 0b00000110  (right side bars only)
digit 8 = A|B|C|D|E|F|G = 0b01111111  (all segments)
```

## CATHODE_SEGMENTS
Lookup table: character → which segments to turn on.
```python
0: A|B|C|D|E|F   # all except middle bar
1: B|C           # right side only
" ": 0           # nothing = blank
```
Built for common cathode where 1 = segment ON.

## DIGITS
```python
DIGITS = { 0: 0b0001, 1: 0b0010, 2: 0b0100, 3: 0b1000 }
```
Selects which of the 4 digit positions to activate.
Only one bit set = only one digit ON at a time (multiplexing).

## segment_byte()
```python
pattern = self.CATHODE_SEGMENTS.get(char, 0)
if self._common_anode:
    pattern = ~pattern & 0xFF
```
Looks up the segment pattern. If common anode, inverts all bits because
common anode uses 0 = ON instead of 1 = ON.
`& 0xFF` keeps it as a valid 8-bit number (Python's ~ gives negative otherwise).

## show_one_digit()
```python
value = (digit_byte << 8) | segment_byte
self._sr.shift_out_16bit(value)
```
Packs two bytes into one 16-bit number:
- Upper 8 bits = which digit position (from DIGITS)
- Lower 8 bits = which segments to light up (from segment_byte)

## refresh_once()
```python
for index, char in enumerate(self.current_text):
    self.show_one_digit(index, char)
    time.sleep(0.001)
```
Multiplexing — lights one digit for 1ms, moves to next.
4 digits × 1ms = 4ms per full cycle = 250Hz.
Must run in a loop or thread to keep display visible.

## putValue() vs putFilledValue()
```python
putValue("42")          → "  42"   (padded with spaces)
putFilledValue("42")    → "0042"   (padded with zeros, default fill_char="0")
putFilledValue("42", fill_char="-") → "--42"
```
Both align left or right. Both update current_text which refresh_once() reads.

## Counter methods
```python
setCounter(0)   # self.counter = 0  → shows "0000"
increment()     # self.counter += 1 → shows "0001"
decrement()     # self.counter -= 1 → shows "0000"
```
Every method does two things: change self.counter, then call putFilledValue
to update the display immediately.

---

# Bit operations quick reference

| Operation | Symbol | Example | Result |
|-----------|--------|---------|--------|
| Bit shift left  | `<<` | `1<<3` | `0b00001000` |
| Bit shift right | `>>` | `10110010>>3` | `00010110` |
| AND  | `&`  | `1111 & 0101` | `0101` — keeps only matching 1s |
| OR   | `\|` | `0011 \| 0101` | `0111` — turns on any 1 |
| XOR  | `^`  | `0011 ^ 0101` | `0110` — flips where different |
| NOT  | `~`  | `~0b00000110` | negative in Python → use `& 0xFF` |

## 10110010 >> 3 fully worked out
```
Start:   1 0 1 1 0 0 1 0
         7 6 5 4 3 2 1 0

Shift right 3 positions → drop bits 0,1,2 from the right, fill left with 0s

Result:  0 0 0 1 0 1 1 0
         7 6 5 4 3 2 1 0

10110010 >> 3 = 00010110
```
The 3 rightmost bits (0, 1, 0) are discarded.
Three zeros fill in on the left.
