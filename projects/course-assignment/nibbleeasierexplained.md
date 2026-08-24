Yes — much simpler.

# One value, three ways to write it

Take this nibble:

```text
1011
```

That is just **one value**.

You can write that same value in 3 number systems:

## 1. Binary

Binary uses only:

```text
0 and 1
```

So the value is written as:

```text
0b1011
```

The `0b` just means:

> this number is binary

---

## 2. Decimal

Decimal is the normal number system we use every day:

```text
0 1 2 3 4 5 6 7 8 9
```

The same value becomes:

```text
11
```

Why?

Because:

```text
1011 = 1×8 + 0×4 + 1×2 + 1×1
     = 8 + 0 + 2 + 1
     = 11
```

So:

```text
1011 in binary = 11 in decimal
```

---

## 3. Hexadecimal

Hex uses:

```text
0 1 2 3 4 5 6 7 8 9 A B C D E F
```

So after 9, it continues with letters:

* A = 10
* B = 11
* C = 12
* D = 13
* E = 14
* F = 15

So the same value `11` becomes:

```text
0xb
```

because:

```text
B = 11
```

The `0x` just means:

> this number is hexadecimal

---

# Why does hex only go from 0 to F here?

Because a nibble has **4 bits**.

And 4 bits can only make values from:

```text
0000 to 1111
```

That means:

## Smallest

```text
0000 = 0
```

## Largest

```text
1111 = 15
```

So a nibble can only store:

```text
0 to 15
```

In hex, that range is:

```text
0 to F
```

because:

* 10 = A
* 11 = B
* 12 = C
* 13 = D
* 14 = E
* 15 = F

---

# Example table

| Binary | Decimal | Hex |
| ------ | ------: | --: |
| 0000   |       0 |   0 |
| 0001   |       1 |   1 |
| 0010   |       2 |   2 |
| 0011   |       3 |   3 |
| 0100   |       4 |   4 |
| 0101   |       5 |   5 |
| 0110   |       6 |   6 |
| 0111   |       7 |   7 |
| 1000   |       8 |   8 |
| 1001   |       9 |   9 |
| 1010   |      10 |   A |
| 1011   |      11 |   B |
| 1100   |      12 |   C |
| 1101   |      13 |   D |
| 1110   |      14 |   E |
| 1111   |      15 |   F |

---

# What the LCD should show

The assignment wants the **same nibble** shown in 3 ways.

Suppose the nibble is:

```text
1011
```

Then:

* binary = `0b1011`
* hex = `0xb`
* decimal = `11`

So LCD should show:

## Line 1

```text
0b1011       0xb
```

## Line 2

```text
              11
```

---

# What “aligned left” means

If something is aligned left, it starts at the beginning of the line.

Example:

```text
0b1011
```

starts on the left side.

So line 1 starts like:

```text
0b1011...
```

---

# What “aligned right” means

If something is aligned right, it ends at the far right side of the line.

So on line 1:

* binary is on the left
* hex is on the right

Example on a 16-char LCD:

```text
0b1011       0xb
```

Binary starts at the left.
Hex ends at the right.

And on line 2:

* decimal ends at the right

Example:

```text
              11
```

That means the `11` is pushed all the way to the right side.

---

# Super short version

Take one nibble:

```text
1011
```

That same value can be written as:

```text
binary  = 0b1011
decimal = 11
hex     = 0xb
```

The LCD should show:

* binary left
* hex right
* decimal right

So screen 2 is really just:

> read 4 buttons → make 1 nibble → show it in 3 number systems

If you want, next I’ll show you exactly how to make the LCD line strings like:

```python
line1 = "0b1011       0xb"
line2 = "              11"
```

