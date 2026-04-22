okay lets start with explaining screen 2: we import lcd library which is used to control the lcd screen and time library for delays and RPi.GPIO for controlling the GPIO pins. we set the 4 buttons    

then we continue with setup the buttons we continue by setting the button pins as inputs and enabling the pull up resistors we toggle and send bits to the lcd to display the text we want. we then startwith reading butotn bits def read_buttons_bits(): which reads the button states and returns them as a tuple of 4 bits
we then make a nibble def make_nibble(b1,b2,b3,b4): which takes the 4 bits and makes a nibble from them
we then format the value to be displayed on the lcd def format_screen(value): which takes the nibble and formats it to be displayed on the lcd
we then start the run function which takes the stop event as an argument and keeps running until the stop event is set
 
