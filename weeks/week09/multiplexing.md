# Multiplexing & 7-Segment Display

## What is multiplexing?

Multiplexing means: **control many outputs using fewer pins**.

A 4-digit 7-segment display does not control every digit separately at once. Instead, it cycles through them extremely fast:

1. Turn on digit 1
2. Turn on digit 2
3. Turn on digit 3
4. Turn on digit 4

Then repeat — so fast that your eyes perceive all digits as **on simultaneously**.

---

## What is a 7-segment display?

Each digit has **7 LED segments** labeled:

```
A   B   C   D   E   F   G
```

Plus the decimal point (DP):

```
8 LEDs = 1 byte = 8 bits
```

---

## Shift register connection

The kit maps each segment to one shift register output:

| Output Bit | Segment |
|------------|---------|
| Q0         | A       |
| Q1         | B       |
| Q2         | C       |
| Q3         | D       |
| Q4         | E       |
| Q5         | F       |
| Q6         | G       |
| Q7         | DP      |

One byte = one digit.

---

## Common Cathode vs Common Anode

A 7-segment display has two types. The difference is how the LEDs are wired internally, which determines whether a `0` or `1` turns a segment ON.

### How it works

- **Common cathode**: All LED negative ends share one pin connected to ground. To turn a segment on, you send a **high signal (1)** to its control pin.
  - `1` = segment ON
  - `0` = segment OFF

- **Common anode**: All LED positive ends share one pin connected to VCC. To turn a segment on, you must pull the control pin **low**.
  - `0` = segment ON
  - `1` = segment OFF

### Side-by-side: number 2

| Segment | Common cathode | Common anode |
|---------|---------------|--------------|
| A       | 1             | 0            |
| B       | 1             | 0            |
| C       | 0             | 1            |
| D       | 1             | 0            |
| E       | 1             | 0            |
| F       | 0             | 1            |
| G       | 1             | 0            |
| **Byte** | `0x5B`      | `0xA4`     |

### Exam trick

The two values are always **bitwise inverses** of each other:

```
Common cathode (2):   0b0101_1011 = 0x5B
                        ↓ flip all bits
Common anode (2):    0b1010_0100 = 0xA4
```

Your kit uses common **anode** — so `0` turns segments ON.

---

## Latch Pin (ST_CP / Storage Register Clock)

The latch pin controls **when the shift register outputs update**. This is critical for displaying stable values without flicker.

### How 74HC595 works internally

The chip has two registers:
1. **Shift register** — where data enters bit-by-bit (Q0-Q7 are NOT visible yet)
2. **Storage register** — where the final value lives and outputs appear

The latch pin moves data from shift → storage, making it visible on Q0-Q7 at once.

### The 3-step cycle for each digit

```
1. Shift out byte (MSB first, bit by bit)
   └─ bits are now in the shift register (not yet visible)

2. Pulse LATCH HIGH → LOW
   └─ all 8 bits appear on Q0-Q7 at once
   
3. Select digit to show
```

### Why latch matters for multiplexing

Without a proper latch, you would see **bit flicker** — segments changing mid-digit as each bit streams in one by one. The latch ensures the full byte appears **simultaneously**.

### Pin signals summary (74HC595)

| Signal | Purpose |
|--------|---------|
| DS     | Data input (serial data, 1 bit at a time) |
| SH_CP  | Shift register clock — advances bits on each pulse |
| ST_CP  | Storage register clock (latch) — copies shift → output |

### Exam tip

The latch is what makes multiplexing **look smooth**. Without it:
- Digits would flicker or show partial numbers
- You'd see the bit-by-bit streaming visually

---

## Example: Display number 1

To show `1`, only segments **B** and **C** need to be ON.

### Common cathode (1 = ON)

```
A=0, B=1, C=1, D=0, E=0, F=0, G=0, DP=0

Bits: Q7  Q6  Q5  Q4  Q3  Q2  Q1  Q0
      DP  G   F   E   D   C   B   A
            0   0   0   0   1   1   0

Value: 0b0000_0110 = 0x06
```

### Common anode (0 = ON) — your kit

Logic is **inverted**: `0` turns a segment ON, `1` turns it OFF.

For number 1:

```
B=0, C=0 → all others 1

Bits: Q7  Q6  Q5  Q4  Q3  Q2  Q1  Q0
      DP  G   F   E   D   C   B   A
      1   1   1   1   1   0   0   1

Value: 0b1111_1001 = 0xF9
```

---

## Exam tip

**Common cathode:** `1` = ON
**Common anode:** `0` = ON (your kit)

The common anode value is simply the **bitwise inverse** of the common cathode value.

> If you know one, just flip all bits to get the other.
