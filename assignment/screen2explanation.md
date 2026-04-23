The assignment says:

read the 4 buttons
treat each button as 1 bit
combine those 4 bits into 1 nibble
show that nibble in:
binary
hexadecimal
decimal
update the LCD whenever the button combination changes

What is a nibble?

A nibble is:

4 bits

Since you have 4 buttons, each button becomes one bit:

b1 b2 b3 b4

Example:

1 0 1 1

That becomes one nibble:

1011 in binary

in decimal that is 11

in hexadecimal that is b
What must be shown on the LCD?
Line 1
binary on the left
hex on the right

Example:

0b1011       0xb
Line 2
decimal on the right

Example:

              11
Why does it only update when buttons change?

Because the assignment says:

When a new combination of buttons is pressed, the LCD will update

So if the value stays the same, there is no need to redraw the LCD.

That is why your code uses:

last_value = -1

and checks:

if value != last_value:
2. What your code does

Assignment explanation

Screen 2 reads 4 buttons. Each button becomes 1 bit:

button pressed     = 1
button not pressed = 0

Together, the 4 bits form a nibble:

b1 b2 b3 b4

Example:

1 0 1 1 = 0b1011 = 0xb = 11

The LCD must show:

0b1011       0xb
              11

So:

line 1: binary left, hex right
line 2: decimal right
update only when the button combination changes
Your code has these big parts:

okay lets start with explaining screen 2: we import lcd library which is used to control the lcd screen and time library for delays and RPi.GPIO for controlling the GPIO pins. we set the 4 buttons    

then we continue with setup the buttons we continue by setting the button pins as inputs and enabling the pull up resistors we toggle and send bits to the lcd to display the text we want. we then startwith reading butotn bits def read_buttons_bits(): which reads the button states and returns them as a tuple of 4 bits
we then make a nibble def make_nibble(b1,b2,b3,b4): which takes the 4 bits and makes a nibble from them
we then format the value to be displayed on the lcd def format_screen(value): which takes the nibble and formats it to be displayed on the lcd
we then start the run function which takes the stop event as an argument and keeps running until the stop event is set
 
