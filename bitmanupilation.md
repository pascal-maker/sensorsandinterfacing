# Beginner Guide to Bit Operations

This is the mental model you should keep during the exam:

```text
Bit operations are mostly:
- moving bits
- keeping bits
- combining bits
```

That’s honestly most of it.

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

A byte is:

```text
8 bits
```

Example byte:

```text
01001011
```

---

# 3. Bit Positions

Bits are numbered from RIGHT to LEFT.

```text
B7 B6 B5 B4 B3 B2 B1 B0
```

Example:

```text
0  1  0  0  1  0  1  1
```

---

# 4. Bit Values

Each position has a value.

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

# 5. Example — Convert Binary to Decimal

Example:

```text
01001011
```

Check which bits are ON:

| Bit | Value | ON/OFF |
| --- | ----- | ------ |
| B6  | 64    | ON     |
| B3  | 8     | ON     |
| B1  | 2     | ON     |
| B0  | 1     | ON     |

Add them:

64 + 8 + 2 + 1 = 75

So:

```text
01001011 = 75
```

---

# 6. Nibbles

A nibble is:

```text
4 bits
```

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
1 << 1
```

Start:

```text
00000001
```

Move left once:

```text
00000010
```

---

Another example:

```python
1 << 3
```

Result:

```text
00001000
```

---

# Easy memory trick

| Operator | Meaning    |
| -------- | ---------- |
| `<<`     | move left  |
| `>>`     | move right |

---

# 8. Shift Right `>>`

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

---

Example:

```text
10101100
00001111
--------
00001100
```

Only the bottom 4 bits survive.

---

# Think of & as a Filter

| Bit | Meaning       |
| --- | ------------- |
| 0   | block         |
| 1   | allow through |

---

# 10. OR Operator `|`

`|` means:

```text
combine bits
```

---

Example:

```text
10100000
00000111
--------
10100111
```

Bits from both numbers are combined.

---

# 11. Very Important Masks

## Lower nibble mask

```text
0x0F
=
00001111
```

Keeps ONLY lower nibble.

---

## Upper nibble mask

```text
0xF0
=
11110000
```

Keeps ONLY upper nibble.

---

# 12. BCD (Binary Coded Decimal)

BCD means:

```text
each decimal digit gets its own 4 bits
```

---

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

# 13. Decode BCD

Suppose:

```text
01110010
```

---

## Get upper digit

Shift right 4:

```python
value >> 4
```

Result:

```text
00000111
```

which equals:

```text
7
```

---

## Get lower digit

Use:

```python
value & 0x0F
```

---

Binary:

```text
01110010
00001111
--------
00000010
```

which equals:

```text
2
```

---

# Final Decimal Formula

\text{decimal} = (BCD >> 4) \times 10 + (BCD & 0x0F)

---

# 14. Create BCD

Example:

Create BCD for:

```text
72
```

---

## Step 1 — Move 7 into upper nibble

```python
7 << 4
```

Result:

```text
01110000
```

---

## Step 2 — Add the 2

```python
(7 << 4) | 2
```

---

Binary:

```text
01110000
00000010
--------
01110010
```

Done.

---

# 15. Check if a Bit is ON

Example:

Check if bit 6 is ON.

Bit 6 mask:

```text
01000000
```

which is:

```python
0x40
```

---

Use:

```python
value & 0x40
```

---

Example:

```text
01100101
01000000
--------
01000000
```

Result is NOT zero.

So:

```text
bit 6 is ON
```

---

# 16. Turn ON a Bit

Example:

Turn ON bit 5.

Bit 5 mask:

```text
00100000
```

Use OR:

```python
value | 0x20
```

---

Example:

```text
00000101
00100000
--------
00100101
```

---

# 17. Turn OFF a Bit

Example:

Turn OFF bit 2.

Bit 2 mask:

```text
00000100
```

Invert it:

```text
11111011
```

Use:

```python
value & ~0x04
```

---

Example:

```text
00101111
11111011
--------
00101011
```

---

# 18. Extract Lower Nibble

Example:

```text
10110110
```

Use:

```python
value & 0x0F
```

---

Result:

```text
00000110
```

---

# 19. Extract Upper Nibble

Example:

```text
10110110
```

Keep upper nibble:

```text
11110000
```

---

AND:

```text
10110110
11110000
--------
10110000
```

---

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

---

# Formula

(value & 0xF0) >> 4

---

# 20. Rebuild a Byte

Suppose:

```text
upper = 1010
lower = 0111
```

Create:

```text
10100111
```

---

## Step 1 — Move upper nibble left

```python
upper << 4
```

Result:

```text
10100000
```

---

## Step 2 — Combine lower nibble

```python
(upper << 4) | lower
```

---

Binary:

```text
10100000
00000111
--------
10100111
```

---

# 21. Hard Example — Rebuild A and B

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

# Build A

From X1:

```text
A7 A6 A5 A4
```

are already lower nibble.

Keep them:

```python
X1 & 0x0F
```

Move them left:

```python
(X1 & 0x0F) << 4
```

---

From X2:

```python
X2 & 0x0F
```

gets:

```text
A3 A2 A1 A0
```

---

Combine:

A = ((X1 & 0x0F) << 4) ;|; (X2 & 0x0F)

---

# Build B

From X1:

```python
X1 & 0xF0
```

keeps:

```text
B7 B6 B5 B4
```

---

From X2:

```python
(X2 & 0xF0) >> 4
```

gets:

```text
B3 B2 B1 B0
```

---

Combine:

B = (X1 & 0xF0) ;|; ((X2 & 0xF0) >> 4)

---

# 22. The BIG Exam Pattern

Most bit questions reduce to:

| Goal            | Operation |   |
| --------------- | --------- | - |
| keep bits       | `&`       |   |
| combine bits    | `         | ` |
| move bits left  | `<<`      |   |
| move bits right | `>>`      |   |

That’s honestly about 90% of beginner bit manipulation.
