
X1 : B7 B6 B5 B4 A7 A6 A5 A4

A byte has 8 positions:

bit7 bit6 bit5 bit4 bit3 bit2 bit1 bit0

The LEFT side is the upper nibble.
The RIGHT side is the lower nibble.

Visualize the byte positions
bit7 bit6 bit5 bit4 bit3 bit2 bit1 bit0
 B7   B6   B5   B4   A7   A6   A5   A4

Notice:

Bits	Contents
bit7–bit4	B7 B6 B5 B4
bit3–bit0	A7 A6 A5 A4
Lower nibble means
last 4 bits

which are:

bit3 bit2 bit1 bit0

And in X1 those positions contain:

A7 A6 A5 A4

So A’s first half is already sitting in the lower nibble.

Why do we use & 0x0F?

Because:

0x0F = 00001111

This keeps ONLY the lower nibble.

Example:

Suppose:

X1 = 10100110

Then:

10100110
00001111
--------
00000110

Upper nibble disappears.

Only lower nibble stays.

So the logic is:

We look at:

X1 : B7 B6 B5 B4 A7 A6 A5 A4

and immediately see:

A bits are on the RIGHT side

Right side = lower nibble.

That’s why we say:

“A7 A6 A5 A4 are already in the lower nibble.”

give me 10 of this erxerices witha fullly exlaine solution so i an duenrtand
Exercise 1 — Check if bit 3 is ON

Suppose:

value = 00101101

Check whether bit 3 is 1.

Step 1 — What mask do we need?

Bit positions:

B7 B6 B5 B4 B3 B2 B1 B0

Bit 3 mask:

00001000

which is:

0x08
Step 2 — AND operation
00101101
00001000
--------
00001000

Result is NOT zero.

So:

bit 3 = 1
Final answer
value & 0x08

If result ≠ 0 → bit 3 is ON.

Exercise 2 — Extract lower nibble

Suppose:

value = 10110110

Extract lower nibble.

Use lower nibble mask
0x0F = 00001111
AND operation
10110110
00001111
--------
00000110

Result:

0110

(decimal 6)

Final formula
value & 0x0F
Exercise 3 — Extract upper nibble

Suppose:

value = 10110110

Extract upper nibble.

Keep upper nibble
11110000
AND
10110110
11110000
--------
10110000
Shift right 4
10110000 >> 4
=
00001011

Result:

1011

(decimal 11)

Final formula

(value&0xF0)>>4

Exercise 4 — Create BCD for 45

Need:

4 in upper nibble
5 in lower nibble
Shift 4 left
4 << 4

Result:

01000000
OR with 5
01000000
00000101
--------
01000101
Final formula

(4<<4)∣5

Exercise 5 — Decode BCD 0x72
01110010
Tens digit

Shift right:

01110010 >> 4
=
00000111

= 7

Ones digit
01110010
00001111
--------
00000010

= 2

Decimal number
72
Formula

(BCD>>4)×10+(BCD&0x0F)

Exercise 6 — Turn ON bit 5

Suppose:

value = 00000101

Turn ON bit 5.

Bit 5 mask
00100000
OR operation
00000101
00100000
--------
00100101
Final formula
value | 0x20
Exercise 7 — Turn OFF bit 2

Suppose:

value = 00101111

Turn OFF bit 2.

Bit 2 mask
00000100

Invert it:

11111011
AND
00101111
11111011
--------
00101011

Bit 2 becomes 0.

Final formula
value & ~0x04
Exercise 8 — Move nibble

Suppose:

00001011

Move it into upper nibble.

Shift left 4
00001011 << 4
=
10110000
Final formula
value << 4
Exercise 9 — Rebuild byte

Suppose:

upper = 1010
lower = 0111

Create:

10100111
Shift upper nibble
1010 << 4
=
10100000
OR lower nibble
10100000
00000111
--------
10100111
Formula

(upper<<4)∣lower

Exercise 10 — Separate A and B

Given:

X1 : B7 B6 B5 B4 A7 A6 A5 A4
X2 : B3 B2 B1 B0 A3 A2 A1 A0

Build A and B.

Build A

Lower nibble of X1 contains:

A7 A6 A5 A4

Keep it:

X1 & 0x0F

Move left:

(X1 & 0x0F) << 4

Lower nibble of X2 contains:

A3 A2 A1 A0

Keep it:

X2 & 0x0F

Combine:

A=((X1&0x0F)<<4)∣(X2&0x0F)

Build B

Upper nibble of X1 already contains:

B7 B6 B5 B4

Keep it:

X1 & 0xF0

Upper nibble of X2 contains:

B3 B2 B1 B0

Move down:

(X2 & 0xF0) >> 4

Combine:

B=(X1&0xF0)∣((X2&0xF0)>>4)

Most important beginner realization

Almost ALL exam questions reduce to:

Goal	Operation
keep bits	&
combine bits	`
move bits left	<<
move bits right	>>

That’s honestly 90% of beginner bit manipulation
