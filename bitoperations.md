These look hard at first because bit operations feel abstract, but honestly most of these reduce to just 3 ideas:

& → isolate/check bits
<< → move bits left
>> → move bits right

Once you recognize which of those 3 actions you need, the exercises become mechanical.

CORE CHEAT SHEET
Operation	Meaning
&	keep/isolate bits
`	`
<< n	move left n places
>> n	move right n places
Ex 1 — Convert 2-digit BCD to decimal

Suppose byte contains:

0111 0010

BCD means:

0111 = 7
0010 = 2

So value is:

72
How to extract digits

Upper digit:

tens = bcd >> 4

Why?

Because shifting right 4 places removes lower nibble.

Example:

01110010 >> 4
=
00000111

which is:

7

Lower digit:

ones = bcd & 0x0F

Why?

0x0F = 00001111

AND keeps only lower 4 bits.

01110010
00001111
--------
00000010

which is:

2

Final decimal:

decimal=(BCD>>4)×10+(BCD&0x0F)

Ex 2 — Check if bit 6 is 0 or 1

Bits are numbered:

B7 B6 B5 B4 B3 B2 B1 B0

To check bit 6:

value & 0x40

Why?

0x40 = 01000000

Only bit 6 is ON.

Example

Suppose:

value = 01100101

AND:

01100101
01000000
--------
01000000

Result is nonzero → bit 6 = 1.

If result is:

00000000

then bit 6 = 0.

Exam answer
if(value & 0x40):

bit 6 is 1.

Else bit 6 is 0.

Ex 3 — Write 72 into BCD

Need:

7 in upper nibble
2 in lower nibble
Step 1 — shift 7 left
7 << 4

Result:

01110000
Step 2 — combine with 2
(7 << 4) | 2
Binary
01110000
00000010
--------
01110010

BCD for 72.

Final answer

BCD=(7<<4)∣2

Ex 4 — Rebuild A and B

You are given:

X1 : B7 B6 B5 B4 A7 A6 A5 A4
X2 : B3 B2 B1 B0 A3 A2 A1 A0

Need to reconstruct:

A = A7 A6 A5 A4 A3 A2 A1 A0
B = B7 B6 B5 B4 B3 B2 B1 B0
Solve A

From X1:

A7 A6 A5 A4

are already lower nibble.

So isolate:

X1 & 0x0F

Need these as upper nibble of A:

(X1 & 0x0F) << 4

Now take lower nibble from X2:

X2 & 0x0F

Combine:

A=((X1&0x0F)<<4)∣(X2&0x0F)

Solve B

Upper nibble already in X1:

X1 & 0xF0

Lower nibble in upper half of X2:

B3 B2 B1 B0

Need to shift right:

(X2 & 0xF0) >> 4

Combine:

B=(X1&0xF0)∣((X2&0xF0)>>4)

BIG EXAM STRATEGY

Most bit questions become:

Question Type	Operation
“check a bit”	& mask
“move nibble”	<< or >>
“combine values”	`
“extract nibble”	& 0x0F or & 0xF0
Most important masks to memorize
Mask	Binary	Purpose
0x0F	00001111	lower nibble
0xF0	11110000	upper nibble
0x01	00000001	bit 0
0x02	00000010	bit 1
0x04	00000100	bit 2
0x08	00001000	bit 3
0x10	00010000	bit 4
0x20	00100000	bit 5
0x40	01000000	bit 6
0x80	10000000	bit 7

These questions look intimidating because of notation, but the actual operations are repetitive once you recognize the pattern.
