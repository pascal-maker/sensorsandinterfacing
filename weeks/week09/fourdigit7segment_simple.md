# FourDigit7Segment — Simple Explanation

## What does it do?
This class controls a 4-digit display (like on a microwave) using a shift register.
We can't wire all the segments directly to the Pi — there are too many pins needed.
So we use a shift register: send data over 2-3 pins, get 16 outputs.

---

## Segment constants (A, B, C ... G, DP)
A 7-segment display has 7 bars and a dot. Each bar has a name:
```
 AAA
F   B
 GGG
E   C
 DDD   (DP = the dot)
```
We control all 8 with one byte. Each letter gets its own bit:
```python
A = 1<<0  # bit 0
B = 1<<1  # bit 1
G = 1<<6  # bit 6
```
We combine them with `|` to turn multiple segments on at once.
That byte goes to the shift register which turns those pins HIGH.

---

## CATHODE_SEGMENTS
A lookup table. You give it a character, it gives back which segments to turn on.
```python
0: A|B|C|D|E|F   # all bars except the middle one = looks like 0
1: B|C            # just the right side bars = looks like 1
" ": 0            # nothing on = blank
```

---

## DIGITS
Tells the hardware which of the 4 digit positions to turn on.
Only 1 digit is on at a time:
```python
0: 0b0001   # leftmost digit
1: 0b0010
2: 0b0100
3: 0b1000   # rightmost digit
```

---

## __init__
Runs once when you create the object. Stores:
- the shift register (used to send data to the display)
- whether it's common anode or cathode (affects how bits are sent)
- current text (starts blank)
- a counter (used by increment/decrement)

---

## segment_byte()
Converts one character into the correct byte to send to the display.
1. Makes the character uppercase so "a" and "A" both work
2. Looks it up in CATHODE_SEGMENTS
3. If common anode: flips all the bits (`~pattern & 0xFF`)
   because common anode has inverted logic — 0 means ON instead of 1

---

## show_one_digit()
Turns on one digit showing one character.
Packs digit + segments into one 16-bit number and sends it to the shift register:
```
upper 8 bits = which digit position
lower 8 bits = which segments to light up
```

---

## refresh_once()
Loops through all 4 digits, showing each one for 1ms.
This is called **multiplexing** — only 1 digit is physically on at a time
but it switches so fast (250 times per second) your eye sees all 4 at once.
Must run in a loop or thread to keep the display visible.

---

## putValue() and putFilledValue()
Set what text to show on the display.
- `putValue("42")` → pads with spaces → `"  42"`
- `putFilledValue("42")` → pads with zeros → `"0042"`
Both can align left or right.

---

## setCounter(), increment(), decrement()
Simple counter that shows on the display.
```python
display.setCounter(0)   # shows 0000
display.increment()     # shows 0001
display.increment()     # shows 0002
display.decrement()     # shows 0001
```
Every call updates the number and immediately refreshes the display text.
