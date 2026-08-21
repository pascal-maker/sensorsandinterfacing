from RPi import GPIO
import time

GPIO.setmode(GPIO.BCM)

# The 4 GPIO pins connected to BCD counter outputs (LSB to MSB order: bit0..bit3)
pins = [16, 20, 21, 26]

# Configure each pin as input with an internal pull-up resistor.
# Pull-up means the pin reads HIGH (1) by default; the counter pulls it LOW (0)
# to assert a '1' bit, so we invert every reading below.
for pin in pins:
    GPIO.setup(pin, GPIO.IN, GPIO.PUD_UP)

# Track the previous decoded value so we only print on change (EXTRA requirement)
last_value = None#guarantee that the first reading always prints, regardless of what the counter shows.

try:
    while True:
        value = 0  # Will accumulate the 4-bit nibble start the niblle as all zeros: 0000 each loop resets the nibble before oring in the 4 bits

        # Read and invert each pin, then shift it into the correct bit position
        for i, pin in enumerate(pins):# gives you both the index and the value from the list at the same time. i=0, pin =16 etc you need i to know which bit postion to shift into and pin to actually read the gpio.
            raw = GPIO.input(pin)   # 0 or 1 straight from the pin reads the pyschical voltage on the pn - returns either 0 low or 1 high

            # Invert: pull-up makes active-low logic, so a LOW pin means bit = 1
            bit = 1 - raw# pins are set to pull up, so they read as 1 unless the counter is pulling them low, so this inverts the reading to get the correct bit value low should be 1 here the logic is flipped: 0 pin stays high 1 pin goes low counter says bit = 1  →  pin goes LOW  →  raw = 0  →  1 - 0 = 1  ✓
  #Counter says bit = 0  →  pin stays HIGH → raw = 1  →  1 - 1 = 0  

            print(f"Bit {i} = {bit}", end="  ")  # Print each bit individually prints each bit on the same line as t's read . end =" "replaces the default new line with spaces so all 4 bits appear side by side 

            # Shift the bit into position i and OR it into the nibble.
            # i=0 → bit0 (units), i=1 → bit1 (twos), i=2 → bit2 (fours), i=3 → bit3 (eights)
            value |= bit << i# shifts each bit into position i and merges into a value. after all 4 iterations the niblle is fully built

        print(f"\n-> Combined nibble = {value:04b}  (decimal: {value})")# prints the final result once all 4 bits are combined
        

        # EXTRA: only report to console when the decoded value actually changes
        if value != last_value:#the extra requirement only reports to the console when the decoded value actually changes announces the new value to the console, Only fires on a change so you dont get flooded  with repeated identical lines.
            print(f"*** Value changed: {value} ***")#prints the new value
            last_value = value# updates the tracker so next iteration it compares against the value you just read, not an older one.

        time.sleep(0.1)  # Short poll interval keeps the reading responsive

except KeyboardInterrupt:
    GPIO.cleanup()