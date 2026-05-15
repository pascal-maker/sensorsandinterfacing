# Summary — Week08 Shift Register

This chapter teaches how to use the **74HC595 shift register** to control many LEDs/devices using only a few Raspberry Pi GPIO pins.

---

# 1. Main idea

A Raspberry Pi has limited GPIO pins.

Example:

* 4 seven-segment displays would need many outputs
* LED matrices may need 64 outputs

Solution:

```text
Use shift registers
```

A shift register converts:

```text
Serial data → Parallel outputs
```

Meaning:

* Raspberry Pi sends bits one by one
* Shift register stores them
* Outputs appear simultaneously on many pins

---

# 2. 74HC595 shift register

The kit uses:

```text
74HC595
```

Features:

* 8-bit serial-in parallel-out
* Can cascade multiple registers
* Has storage register
* Has output enable
* Has master reset

---

# 3. Important pins

| Pin   | Meaning                          |
| ----- | -------------------------------- |
| DS    | serial data input                |
| SHCP  | shift clock                      |
| STCP  | storage/latch clock              |
| OE    | output enable                    |
| MR    | master reset                     |
| Q0–Q7 | outputs                          |
| Q7’   | overflow output to next register |

---

# 4. How shifting works

For every clock pulse on:

```text
SHCP
```

the bit on DS is:

* read
* inserted
* previous bits shift right

Like a conveyor belt.

---

# 5. Storage register concept

The chip has:

1. shift register (temporary)
2. storage register (visible outputs)

This means:

* you can load bits internally
* LEDs stay unchanged
* only after STCP pulse do outputs update

This prevents flickering.

---

# 6. Important hardware limitation

On your project board:

| Pin | Fixed state |
| --- | ----------- |
| OE  | LOW         |
| MR  | HIGH        |

Meaning:

* outputs always enabled
* no software reset possible

So clearing LEDs must be done by:

```text
shifting zeros into the registers
```

---

# 7. Cascading registers

Registers can be chained together.

Q7’ of first register connects to DS of second register.

So:

* 2 registers = 16 outputs
* 4 registers = 32 outputs

Your LED bar uses:

```text
2 cascaded shift registers
```

because:

* LED bar has 10 LEDs
* one register only provides 8 outputs

---

# 8. Communication protocol

To send data:

## Step 1

Put bit on DS

## Step 2

Pulse SHCP

```text
LOW → HIGH → LOW
```

This shifts the bit in.

## Step 3

After all bits are loaded:
pulse STCP

This copies internal bits to outputs.

---

# 9. Required methods

The course asks you to implement:

| Method                     | Purpose         |
| -------------------------- | --------------- |
| setup()                    | initialize GPIO |
| write_one_bit(bit)         | send one bit    |
| write_one_byte(byte)       | send 8 bits     |
| copy_to_storage_register() | pulse STCP      |
| reset_storage_register()   | clear LEDs      |
| shift_out_16bit(value)     | send 2 bytes    |

---

# 10. Bit operations

Instead of manually sending:

```python
write_one_bit(True)
write_one_bit(False)
...
```

you should use:

* masks
* shifts
* bitwise operations

Example:

```python
mask = 0b10000000
```

Then:

* check each bit
* send it
* shift mask right

---

# 11. 16-bit shifting

Since you have 2 registers:

* total = 16 bits

So software should work with:

```text
16-bit values
```

Example:

```python
0b0000001111000000
```

This controls all LEDs at once.

Only:

* lowest 10 bits matter
  for your LED bar.

---

# 12. LED bar graph

The LED bar contains:

* 10 LEDs
* controlled through shift registers

The assignment asks you to:

* light one LED
* light multiple LEDs
* create fill mode
* display joystick position
* display button states

---

# 13. Fill mode

Without fill:

```text
0000010000
```

single LED.

With fill:

```text
0001111111
```

all previous LEDs also on.

---

# 14. Object-oriented design

The course eventually builds:

## `ShiftRegister`

Handles:

* GPIO
* clocks
* serial communication

## `LedBarGraph`

Handles:

* LED patterns
* animations
* joystick visualization

This separates:

* hardware logic
  from
* application logic

Very good embedded-system design practice.

---

# 15. Joystick exercise

The joystick assignment:

* reads ADC values
* maps them to LED patterns

Example:

* center → middle LEDs
* move left → more LEDs left
* move right → more LEDs right

Which is exactly what your current script does.

---

# 16. Overall takeaway

This week teaches:

```text
Bit-level hardware communication
```

using:

* GPIO
* clocks
* serial shifting
* bitwise operations
* cascaded registers

You essentially build your own mini display driver from scratch.

# 16. How your code implements this

