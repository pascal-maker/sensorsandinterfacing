# FourDigit7Segment Class — Full Explanation

## What does this script do?
This class controls a **4-digit 7-segment display** using a shift register.
Because the display needs 16 control lines (8 segments + 4 digit selects), we
can't wire it directly to GPIO pins — instead we use a shift register to send
data serially over 2-3 pins and get 16 parallel outputs.

---

## Part 1 — Segment bit constants

A 7-segment display looks like this — each segment has a letter name:

```
 AAA
F   B
F   B
 GGG
E   C
E   C
 DDD   (DP = decimal point, bottom right)
```

We control all segments with **one byte (8 bits)**, one bit per segment:

```
bit 7  bit 6  bit 5  bit 4  bit 3  bit 2  bit 1  bit 0
  DP     G      F      E      D      C      B      A
```

```python
A  = 1<<0  # = 0b00000001 — top horizontal bar
B  = 1<<1  # = 0b00000010 — top right vertical bar
C  = 1<<2  # = 0b00000100 — bottom right vertical bar
D  = 1<<3  # = 0b00001000 — bottom horizontal bar
E  = 1<<4  # = 0b00010000 — bottom left vertical bar
F  = 1<<5  # = 0b00100000 — top left vertical bar
G  = 1<<6  # = 0b01000000 — middle horizontal bar
DP = 1<<7  # = 0b10000000 — decimal point
```

**Why `1<<n`?** It is a bit shift. Each constant places a single `1` bit at a
unique position so they can be combined with `|` without overlapping.

Example — digit "1" only needs B and C (right side vertical bars):
```
B | C = 0b00000010 | 0b00000100 = 0b00000110
```
That byte is sent to the shift register, which drives exactly those two
segments HIGH and all others LOW.

---

## Part 2 — CATHODE_SEGMENTS dictionary

```python
CATHODE_SEGMENTS = {
    0: A|B|C|D|E|F,
    1: B|C,
    2: A|B|D|E|G,
    3: A|B|C|D|G,
    4: B|C|F|G,
    5: A|C|D|F|G,
    6: A|C|D|E|F|G,
    7: A|B|C,
    8: A|B|C|D|E|F|G,
    9: A|B|C|D|F|G,
    "A": A|B|C|E|F|G,
    ...
    " ": 0,
}
```

This is a lookup table: given a character, it returns the **byte that turns on
the correct segments** to display that character on a common cathode display.

Each entry uses `|` to combine segment bits. Whichever segments are included
will be turned ON; the rest stay OFF.

Visual breakdown of a few digits:

```
Digit 0 → A|B|C|D|E|F    all segments except G (no middle bar)
 _
|_|    segments: A(top) B(top-right) C(bot-right) D(bottom) E(bot-left) F(top-left)
|_|

Digit 1 → B|C             only right-side vertical bars
  |
  |

Digit 7 → A|B|C           top bar + right side only
 _
  |
  |

Digit 8 → A|B|C|D|E|F|G  all segments ON
 _
|_|
|_|

" " (space) → 0           no segments ON = blank display
```

**Why "CATHODE"?**
This table is built for **common cathode** displays where `1` = segment ON.
For common anode displays the logic is inverted — that is handled in
`segment_byte()`, not here.

**What if the character is not in the dictionary?**
```python
pattern = self.CATHODE_SEGMENTS.get(char, 0)
```
The `.get(char, 0)` returns `0` as default — all segments OFF (blank).

---

## Part 3 — DIGITS dictionary

```python
DIGITS = {
    0: 1<<0,   # = 0b00000001
    1: 1<<1,   # = 0b00000010
    2: 1<<2,   # = 0b00000100
    3: 1<<3,   # = 0b00001000
}
```

The physical display has 4 digit positions, numbered left to right:

```
[ digit 0 ] [ digit 1 ] [ digit 2 ] [ digit 3 ]
```

Each entry is a **bitmask that selects which digit is active**.
Only one bit is set per entry, meaning only one digit can be ON at a time.

```
DIGITS[0] = 0b00000001  → activate digit 0 (leftmost)
DIGITS[1] = 0b00000010  → activate digit 1
DIGITS[2] = 0b00000100  → activate digit 2
DIGITS[3] = 0b00001000  → activate digit 3 (rightmost)
```

**Why one bit per digit?**
The shift register's upper 8 bits are wired to the 4 digit select pins.
Setting exactly one bit HIGH tells the hardware which digit to power on.
The other 3 digits stay OFF while that digit is being drawn.

**How it connects to show_one_digit():**
```python
value = (digit_byte << 8) | segment_byte
```
- `digit_byte` goes into the upper 8 bits → selects the digit position
- `segment_byte` goes into the lower 8 bits → selects which segments light up

So the full 16-bit value sent to the shift register = "turn on digit X and
show these segments on it."

Example — display digit position 2, showing the number "4":
```
digit_byte  = DIGITS[2]        = 0b00000100
segment_byte = segments for 4  = 0b01100110  (B|C|F|G)
value = 0b0000010001100110
```
The shift register clocks this out and only digit 2 lights up, showing "4".

---

## Part 4 — __init__

```python
def __init__(self, shift_register, common_anode=True):
    self._sr = shift_register
    self._common_anode = common_anode
    self.current_text = " "
    self.counter = 0
```

This runs once when you create the object. It stores everything the class needs
to operate. Line by line:

**`self._sr = shift_register`**
Stores the ShiftRegister object passed in. Every time the display needs to show
something it calls `self._sr.shift_out_16bit(value)`. The class does not know
or care how the shift register works internally — it just uses it.

**`self._common_anode = common_anode`**
Stores whether the display is common anode or common cathode.
- Common cathode: segments turn ON when the pin is HIGH (`1`)
- Common anode: segments turn ON when the pin is LOW (`0`) — inverted logic
This flag is checked later in `segment_byte()` to decide whether to flip bits.

**`self.current_text = " "`**
The display starts blank. This is a 1-character space, not a 4-character string
yet — `putValue()` or `putFilledValue()` will set it to a proper 4-character
string before `refresh_once()` is called.

**`self.counter = 0`**
Internal integer used only by `setCounter()`, `increment()`, `decrement()`.
Stored here so the object remembers the current count between calls.

---

## Part 5 — segment_byte()

```python
def segment_byte(self, char):
    char = char.upper()
    pattern = self.CATHODE_SEGMENTS.get(char, 0)
    if self._common_anode:
        pattern = ~pattern & 0xFF
    return pattern
```

This method takes one character and returns the **8-bit byte** that tells the
shift register which segments to light up. Step by step:

**`char = char.upper()`**
Normalises the input so `"a"` and `"A"` both match the same key in
CATHODE_SEGMENTS. The dictionary only has uppercase keys.

**`pattern = self.CATHODE_SEGMENTS.get(char, 0)`**
Looks up the segment byte for the character. If the character is not in the
dictionary (e.g. `"$"`), it returns `0` — all segments OFF (blank digit).

**`if self._common_anode: pattern = ~pattern & 0xFF`**
CATHODE_SEGMENTS was built for common cathode where `1` = segment ON.
Common anode is the opposite: `0` = segment ON.
So we flip every bit with `~`:

```
Common cathode pattern for "1":  0b00000110  (B and C ON)
After ~:                         0b11111001  (but Python gives a negative number)
After & 0xFF:                    0b11111001  (masked to 8 bits = correct byte)
```

`& 0xFF` is essential — without it Python's `~` produces a negative integer
(because Python integers have no fixed size), and the shift register would
receive garbage data.

**`return pattern`**
Returns the final 8-bit byte, ready to be packed into the 16-bit value in
`show_one_digit()`.

---

## Part 6 — show_one_digit()

```python
def show_one_digit(self, digit_index, char):
    digit_byte = self.DIGITS[digit_index]
    segment_byte = self.segment_byte(char)
    value = (digit_byte << 8) | segment_byte
    self._sr.shift_out_16bit(value)
```

Builds a **16-bit value** to send to the shift register:
- Upper 8 bits = which digit to activate (`digit_byte << 8`)
- Lower 8 bits = which segments to light up (`segment_byte`)

Example: digit 1, character "2"
```
digit_byte  = 0b00000010  (digit 1)
segment_byte = 0b01011011  (segments for "2")
value = 0b0000001001011011
```
The shift register receives this and drives the display.

---

## Part 7 — refresh_once()

```python
def refresh_once(self):
    for index, char in enumerate(self.current_text):
        self.show_one_digit(index, char)
        time.sleep(0.001)
```

This is **multiplexing** in action:
- Only one digit is physically ON at a time
- We cycle through all 4 digits very fast (1ms per digit = 4ms total = 250Hz)
- The human eye cannot detect the switching, so it looks like all 4 are ON simultaneously
- If you call this only once, you see 4 digits flash briefly then nothing
- Must be called in a loop (or a thread) to maintain a visible display

---

## Part 8 — putValue() and putFilledValue()

```python
def putValue(self, text, align="RIGHT"):
    text = str(text).upper()[:4]
    if align == "LEFT":
        self.current_text = text.ljust(4)
    else:
        self.current_text = text.rjust(4)
```

- Converts input to string, uppercase, max 4 characters
- Pads with **spaces** to fill 4 positions
- `"42"` right-aligned → `"  42"` (spaces on left)
- `"42"` left-aligned  → `"42  "` (spaces on right)

```python
def putFilledValue(self, text, fill_char="0", align="RIGHT"):
    text = str(text).upper()[:4]
    if align == "LEFT":
        self.current_text = text.ljust(4, fill_char)
    else:
        self.current_text = text.rjust(4, fill_char)
```

Same as putValue but pads with a **chosen character** instead of spaces.
- `putFilledValue("42")` → `"0042"` (zero-padded, default fill_char="0")
- `putFilledValue("42", fill_char="-")` → `"--42"`

---

## Part 9 — setCounter(), increment(), decrement()

```python
def setCounter(self, value, align="RIGHT"):
    self.counter = int(value)
    self.putFilledValue(str(self.counter), fill_char="0", align="right")

def increment(self):
    self.counter += 1
    self.putFilledValue(str(self.counter), fill_char="0", align="right")

def decrement(self):
    self.counter -= 1
    self.putFilledValue(str(self.counter), fill_char="0", align="right")
```

All three methods do the same two steps: change `self.counter`, then call
`putFilledValue` to push the new number to the display.

**`setCounter(value)`** — jump to a specific number
```python
self.counter = int(value)
self.putFilledValue("42", fill_char="0")  # display shows "0042"
```
Call this once to set the starting point. `int(value)` converts the input in
case a string is passed in.

**`increment()`** — add 1
```python
self.counter += 1                         # 42 becomes 43
self.putFilledValue("43", fill_char="0")  # display shows "0043"
```
Every call adds 1 and immediately updates the display.

**`decrement()`** — subtract 1
```python
self.counter -= 1                         # 43 becomes 42
self.putFilledValue("42", fill_char="0")  # display shows "0042"
```
Opposite of increment.

**The pattern is always the same in all three:**
1. Change `self.counter` (set / add 1 / subtract 1)
2. Call `putFilledValue` to update `current_text` with zero-padding

`putFilledValue` updates `current_text`. Then `refresh_once()` running in the
background picks that up and shows it on the physical display.

**Example usage:**
```python
display.setCounter(0)   # shows 0000
display.increment()     # shows 0001
display.increment()     # shows 0002
display.decrement()     # shows 0001
```

**What if the number goes above 9999?**
`putFilledValue` does `str(text)[:4]` — it silently truncates to 4 characters.
So `10000` would show `1000` (the last digit is cut off).

---

## Full data flow summary

```
putValue("42")
    → current_text = "  42"

refresh_once()
    → digit 0: show_one_digit(0, " ")
        → digit_byte = 0b0001, segment_byte = 0x00
        → shift out 0b0000000100000000
    → digit 1: show_one_digit(1, " ")
        → ...
    → digit 2: show_one_digit(2, "4")
        → digit_byte = 0b0100, segment_byte = segments for "4"
        → shift out 16-bit value
    → digit 3: show_one_digit(3, "2")
        → digit_byte = 0b1000, segment_byte = segments for "2"
        → shift out 16-bit value
```

Each call lights one digit for 1ms, then moves to the next.
Called repeatedly in a thread → persistent multiplexed display.
