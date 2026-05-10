# Beginner Guide to Bit Operations — Structured Exam Notes

## Core Mental Model

```text
Bit operations are mostly:
- moving bits
- keeping bits
- combining bits
```

Most beginner exercises are just combinations of:

| Operation | Meaning          |                  |
| --------- | ---------------- | ---------------- |
| `&`       | keep/filter bits |                  |
| `         | `                | combine/set bits |
| `^`       | toggle/flip bits |                  |
| `<<`      | move bits left   |                  |
| `>>`      | move bits right  |                  |

---

# 1. What is a Bit?

A bit is the smallest unit in a computer.

A bit can only be:

| Bit | Meaning |
| --- | ------- |
| 0   | OFF     |
| 1   | ON      |

Example:

```text
1
```

means ON.

```text
0
```

means OFF.

---

# 2. What is a Byte?

A byte contains:

```text
8 bits
```

Example:

```text
01001011
```

---

# 3. Bit Positions

Bits are counted from RIGHT to LEFT.

```text
B7 B6 B5 B4 B3 B2 B1 B0
```

Example:

```text
0  1  0  0  1  0  1  1
```

---

# 4. Bit Values

| Bit | Value |
| --- | ----- |
| B7  | 128   |
| B6  | 64    |
| B5  | 32    |
| B4  | 16    |
| B3  | 8     |
| B2  | 4     |
| B1  | 2     |
| B0  | 1     |

---

# 5. Convert Binary to Decimal

Example:

```text
01001011
```

Find the ON bits:

| Bit | Value |
| --- | ----- |
| B6  | 64    |
| B3  | 8     |
| B1  | 2     |
| B0  | 1     |

Add them:

```text
64 + 8 + 2 + 1 = 75
```

So:

```text
01001011 = 75
```

---

# 6. Nibbles

A nibble = 4 bits.

A byte has:

| Name         | Bits         |
| ------------ | ------------ |
| upper nibble | left 4 bits  |
| lower nibble | right 4 bits |

Example:

```text
1011 0110
```

| Part         | Value |
| ------------ | ----- |
| upper nibble | 1011  |
| lower nibble | 0110  |

---

# 7. Shift Left `<<`

Means:

```text
move bits LEFT
```

Example:

```python
1 << 3
```

Start:

```text
00000001
```

Move left 3 times:

```text
00001000
```

---

# 8. Shift Right `>>`

Means:

```text
move bits RIGHT
```

Example:

```python
16 >> 2
```

Binary:

```text
00010000
```

Move right twice:

```text
00000100
```

Result:

```text
4
```

---

# 9. AND Operator `&`

`&` means:

```text
keep only matching 1s
```

Example:

```text
10101100
00001111
--------
00001100
```

Only lower nibble survives.

---

# 10. OR Operator `|`

`|` means:

```text
combine bits
```

Example:

```text
10100000
00000111
--------
10100111
```

---

# 11. XOR Operator `^`

`^` means:

```text
toggle/flip bits
```

XOR rules:

| Original | XOR 1 | Result |
| -------- | ----- | ------ |
| 0        | 1     | 1      |
| 1        | 1     | 0      |

Example:

```text
01100101
01000000
--------
00100101
```

Bit 6 flipped.

---

# 12. Important Masks

| Mask | Binary   | Purpose      |
| ---- | -------- | ------------ |
| 0x01 | 00000001 | bit 0        |
| 0x02 | 00000010 | bit 1        |
| 0x04 | 00000100 | bit 2        |
| 0x08 | 00001000 | bit 3        |
| 0x10 | 00010000 | bit 4        |
| 0x20 | 00100000 | bit 5        |
| 0x40 | 01000000 | bit 6        |
| 0x80 | 10000000 | bit 7        |
| 0x0F | 00001111 | lower nibble |
| 0xF0 | 11110000 | upper nibble |

---

# 13. Check if a Bit is ON

## Exercise 1 — Check bit 3

Suppose:

```text
value = 00101101
```

Check bit 3.

Mask:

```text
00001000
```

which is:

```python
0x08
```

AND operation:

```text
00101101
00001000
--------
00001000
```

Result is NOT zero.

So:

```text
bit 3 is ON
```

Formula:

```python
value & 0x08
```

---

# 14. Turn ON a Bit

## Exercise 2 — Turn ON bit 5

Suppose:

```text
value = 00000101
```

Bit 5 mask:

```text
00100000
```

Use OR:

```text
00000101
00100000
--------
00100101
```

Formula:

```python
value | 0x20
```

---

# 15. Turn OFF a Bit

## Exercise 3 — Turn OFF bit 2

Suppose:

```text
value = 00101111
```

Bit 2 mask:

```text
00000100
```

Invert mask:

```text
11111011
```

AND:

```text
00101111
11111011
--------
00101011
```

Formula:

```python
value & ~0x04
```

---

# 16. Toggle a Bit

## Exercise 4 — Toggle bit 6

Suppose:

```text
value = 01100101
```

Bit 6 mask:

```text
01000000
```

Use XOR:

```text
01100101
01000000
--------
00100101
```

Bit 6 flipped from 1 → 0.

Formula:

```python
value ^ 0x40
```

---

# 17. Extract Lower Nibble

## Exercise 5

Suppose:

```text
10110110
```

Mask:

```text
00001111
```

AND:

```text
10110110
00001111
--------
00000110
```

Result:

```text
0110
```

Formula:

```python
value & 0x0F
```

---

# 18. Extract Upper Nibble

## Exercise 6

Suppose:

```text
10110110
```

Keep upper nibble:

```text
11110000
```

AND:

```text
10110110
11110000
--------
10110000
```

Shift right 4:

```text
10110000 >> 4
=
00001011
```

Result:

```text
1011
```

Formula:

```python
(value & 0xF0) >> 4
```

---

# 19. Move a Nibble

## Exercise 7

Suppose:

```text
00001011
```

Move into upper nibble:

```text
00001011 << 4
=
10110000
```

Formula:

```python
value << 4
```

---

# 20. Rebuild a Byte

## Exercise 8

Suppose:

```text
upper = 1010
lower = 0111
```

Move upper nibble:

```text
1010 << 4
=
10100000
```

Combine lower nibble:

```text
10100000
00000111
--------
10100111
```

Formula:

```python
(upper << 4) | lower
```

---

# 21. BCD (Binary Coded Decimal)

BCD stores each decimal digit in 4 bits.

Example:

```text
72
```

becomes:

```text
0111 0010
```

because:

| Digit | Binary |
| ----- | ------ |
| 7     | 0111   |
| 2     | 0010   |

---

# 22. Decode BCD

## Exercise 9 — Decode 0x72

BCD:

```text
01110010
```

Upper digit:

```text
01110010 >> 4
=
00000111
```

= 7

Lower digit:

```text
01110010
00001111
--------
00000010
```

= 2

Final decimal:

```text
72
```

Formula:

```python
(BCD >> 4) * 10 + (BCD & 0x0F)
```

---

# 23. Create BCD

## Exercise 10 — Create BCD for 45

Need:

```text
4 in upper nibble
5 in lower nibble
```

Shift 4 left:

```text
4 << 4
=
01000000
```

OR with 5:

```text
01000000
00000101
--------
01000101
```

Formula:

```python
(4 << 4) | 5
```

---

# 24. Hard Example — Rebuild A and B

Given:

```text
X1 : B7 B6 B5 B4 A7 A6 A5 A4
X2 : B3 B2 B1 B0 A3 A2 A1 A0
```

Need:

```text
A = A7 A6 A5 A4 A3 A2 A1 A0
B = B7 B6 B5 B4 B3 B2 B1 B0
```

---

## Build A

From X1:

```text
A7 A6 A5 A4
```

are already lower nibble.

Keep them:

```python
X1 & 0x0F
```

Move left:

```python
(X1 & 0x0F) << 4
```

Get lower half from X2:

```python
X2 & 0x0F
```

Combine:

```python
A = ((X1 & 0x0F) << 4) | (X2 & 0x0F)
```

---

## Build B

From X1:

```python
X1 & 0xF0
```

keeps:

```text
B7 B6 B5 B4
```

From X2:

```python
(X2 & 0xF0) >> 4
```

gets:

```text
B3 B2 B1 B0
```

Combine:

```python
B = (X1 & 0xF0) | ((X2 & 0xF0) >> 4)
```

---

# 25. BIG Exam Pattern

Almost ALL beginner bit exercises reduce to this:

| Goal         | Operation |   |
| ------------ | --------- | - |
| keep bits    | `&`       |   |
| combine bits | `         | ` |
| toggle bits  | `^`       |   |
| move left    | `<<`      |   |
| move right   | `>>`      |   |

That’s honestly about 90% of beginner bit manipulation.
