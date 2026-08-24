````md
# Screen 2 — Nibble explanation

## What the assignment wants

For screen 2, we have to:

- read the state of **4 buttons**
- combine those 4 button states into **1 nibble**
- show that value in:
  - **binary**
  - **hexadecimal**
  - **decimal**

The LCD should update whenever the button combination changes.

Example from the assignment:

```text
0b1111       0xf
             15
````

So:

* binary is shown on the **left** of line 1
* hex is shown on the **right** of line 1
* decimal is shown on the **right** of line 2

---

## What is a bit?

A **bit** is the smallest piece of binary information.

A bit can only be:

```text
0 or 1
```

For a button, that usually means something like:

* `0` = not pressed
* `1` = pressed

---

## What is a nibble?

A **nibble** is:

```text
4 bits
```

Examples of nibbles:

```text
0000
0101
1011
1111
```

Because this screen uses **4 buttons**, we can treat each button as **1 bit**.

That means the 4 buttons together make exactly **1 nibble**.

---

## Why 4 buttons = 1 nibble?

Suppose we have 4 buttons:

* Button 1
* Button 2
* Button 3
* Button 4

Each button can be either `0` or `1`.

So together they form:

```text
b1 b2 b3 b4
```

Example:

```text
1 0 1 1
```

That is already a nibble.

---

## What does “combine them into a nibble” mean?

It means:

Take the 4 separate button values and make **one binary value** from them.

Example:

```text
b1 = 1
b2 = 0
b3 = 1
b4 = 1
```

Together that becomes:

```text
1011
```

That is the nibble.

---

## Bit positions inside the nibble

Each button is placed in a certain position:

```text
b1 b2 b3 b4
8  4  2  1
```

These are the binary place values.

So:

* `b1` is the **8-place**
* `b2` is the **4-place**
* `b3` is the **2-place**
* `b4` is the **1-place**

Example:

```text
b1 = 1
b2 = 0
b3 = 1
b4 = 1
```

means:

```text
1×8 + 0×4 + 1×2 + 1×1
= 8 + 0 + 2 + 1
= 11
```

So:

```text
1011 = 11
```

---

## Why do we shift the bits?

To put each button in the correct bit position, we use **left shift**.

The code is:

```python
value = (b1 << 3) | (b2 << 2) | (b3 << 1) | b4
```

This looks difficult at first, but it is just placing each button in the correct position.

---

## What does `<<` mean?

`<<` means:

```text
shift left
```

It moves a bit to the left.

Examples:

```text
1      = 0001
1 << 1 = 0010
1 << 2 = 0100
1 << 3 = 1000
```

So shifting is just a way to move the bit into the correct place.

---

## Example with real values

Suppose:

```python
b1 = 1
b2 = 0
b3 = 1
b4 = 1
```

### `b1 << 3`

`b1` must go into the first position:

```text
1 _ _ _
```

That is:

```text
1000
```

So:

```text
1 << 3 = 1000
```

---

### `b2 << 2`

`b2` must go into the second position:

```text
_ 0 _ _
```

That is:

```text
0000
```

because `b2 = 0`.

So:

```text
0 << 2 = 0000
```

---

### `b3 << 1`

`b3` must go into the third position:

```text
_ _ 1 _
```

That is:

```text
0010
```

So:

```text
1 << 1 = 0010
```

---

### `b4`

`b4` already belongs in the last position:

```text
_ _ _ 1
```

That is already:

```text
0001
```

So no shift is needed.

---

## Combine them

Now we have:

```text
b1 << 3 = 1000
b2 << 2 = 0000
b3 << 1 = 0010
b4      = 0001
```

Combine them:

```text
1000
0000
0010
0001
----
1011
```

So the final nibble is:

```text
1011
```

---

## What does `|` mean?

`|` is the **bitwise OR** operator.

It combines bits.

Rules:

```text
0 | 0 = 0
0 | 1 = 1
1 | 0 = 1
1 | 1 = 1
```

So OR is used to merge the shifted button bits into one final nibble.

That is why the code uses:

```python
(b1 << 3) | (b2 << 2) | (b3 << 1) | b4
```

Each button is placed correctly, then OR combines them all.

---

## Binary, decimal, and hexadecimal

The same nibble can be written in different ways.

Example nibble:

```text
1011
```

### Binary

```text
0b1011
```

### Decimal

```text
11
```

### Hexadecimal

```text
0xb
```

All 3 represent the same value.

---

## Why hex only goes from 0 to F

A nibble has 4 bits.

4 bits can represent values from:

```text
0000 to 1111
```

That means decimal:

```text
0 to 15
```

In hex, that becomes:

```text
0 1 2 3 4 5 6 7 8 9 A B C D E F
```

So:

```text
1111 = 15 = F
1011 = 11 = B
```

---

## How the LCD display should look

If the nibble is:

```text
1111
```

then the LCD should show:

```text
0b1111       0xf
             15
```
The 0b just means:

this number is binary

If the nibble is:

```text
1011
```

then the LCD should show:

```text
0b1011       0xb
             11
```

---

## What “aligned left” and “aligned right” mean

### Line 1

* binary should be at the **left**
* hex should be at the **right**

Example:

```text
0b1011       0xb
```

### Line 2

* decimal should be at the **right**

Example:

```text
              11
```

This means you have to format the text carefully before sending it to the LCD.

---

## Important GPIO detail

If the buttons are set up with:

```python
GPIO.PUD_UP
```

then the pin values are usually:

* not pressed = `1`
* pressed = `0`

But for the nibble, we usually want:

* pressed = `1`
* not pressed = `0`

So we invert the input.

Example:

```python
b1 = 1 if GPIO.input(BUTTON_1) == GPIO.LOW else 0
```

This makes the logic easier:

* button pressed → bit becomes `1`
* button not pressed → bit becomes `0`

---

## Summary

Screen 2 is about turning 4 button states into 1 nibble.

### Steps:

1. Read the 4 buttons
2. Convert each button to a bit (`0` or `1`)
3. Put each bit in the correct place with shifting
4. Combine them with OR
5. Display the result in:

   * binary
   * hex  The 0x just means:this number is hexadecimla
   * decimal

### Core formula:

```python
value = (b1 << 3) | (b2 << 2) | (b3 << 1) | b4
```

### Meaning:

* `b1` goes to the 8-place
* `b2` goes to the 4-place
* `b3` goes to the 2-place
* `b4` stays in the 1-place

The result is a nibble, which can then be shown in different number systems.

```
```
