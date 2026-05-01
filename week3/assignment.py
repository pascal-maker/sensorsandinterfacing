from RPi import GPIO
import time

# -----------------------
# CONFIG
# -----------------------
pins = [16, 20, 21, 26]   # BCD inputs (LSB → MSB) position in the list defines the bit value and binary weight 4 buttons pin[0]= 16 -> bit 0 -> worth 1 etc pin[1]= 20 -> bit 1 -> worth 2 etc  pins[2]=21-> bit 2 -> worth 4 etc pins[3] = 26 -> bit 3 -> worth 8 etc
led = 17#pin for LED

GPIO.setmode(GPIO.BCM)

# Setup inputs
for pin in pins:# Setup inputs in pull up mode 
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setup  pins

# Setup LED
GPIO.setup(led, GPIO.OUT)

# Shared variable
bcd_value = 0#stores the value of the bcd code when its pressed 0 is the starting value meaning all buttons are unpressed and the LED will stay on for 1 second and repeat every second aslo it willhold the decimal number (0-15) from whichever bcd buttons are pressed


# -----------------------
# CALLBACK FUNCTION
# -----------------------
def bcd_changed(channel):#when a button is pressed this function is called
    global bcd_value#gives us acess to change the global variable

    btn_num = pins.index(channel) + 1  # which button (1-4) triggered the event chanel is the gpio pin number that triggered the event searches the list and returns rhe position fo that list
    action = "PRESSED" if GPIO.input(channel) == GPIO.LOW else "RELEASED"# checks the state of the pin that triggered the event if it is LOW its pressed since we are using pull up mode if its HIGH its released
    print(f"\nButton {btn_num} (GPIO {channel}) {action}")#prints which button was pressed and what it did

    value = 0#sets initial value to 0 fresh calculation each time reads all 4 pins from scrach rather than modfying the old value

    for i, pin in enumerate(pins):#loops through the pins gives you both the index i and pin number at the same time
        bit = 1 - GPIO.input(pin)   #returns 1 if not pressed and 0 if pressed subtracting 1 from the input value flips it so if its HIGH its 0 and if its LOW its 1 
        print(f"  Button {i+1} (GPIO {pin}): {'PRESSED' if bit else 'released'} -> bit {i} -> contributes {bit * (2**i)}")# prints the state of the button its index and what it contributes to the bcd code 
        value |= (bit << i)# updates the value of the bcd code based on the bits read from the buttons shifts the bit left into is correct position  the OR assignment operater |=  adds the bit to the value

    bcd_value = value#updates the global variable with the new value rest of program can use it
    print(f"  => BCD value: {bcd_value} (binary: {bcd_value:04b})")#prints the final value of the bcd code in binary


# -----------------------
# ADD EVENTS
# -----------------------
for pin in pins:# uses the pins list 
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=bcd_changed, bouncetime=50)# adds an event dectetor to each pin so that the bcd_changed function is called when a button is pressed or released


# -----------------------
# MAIN LOOP
# -----------------------
try:
    while True:
        if bcd_value == 0:#if the bcd value is 0 then turn on the LED for 1 second and then turn it off IF ALL BUTTONS ARE UNPRESSED VALUE = 0 LED TURNS ON AND STAYS ON FOR 1 SECOND. THEN THE LOOP REPEATS AND KEEPS IT ON AGAIN SO EFFIECLERY THE LED JUST STAYS ON WHILE NOTHING IS PRESSED.
            GPIO.output(led, GPIO.HIGH)#turns led on
            time.sleep(1)#waits for 1 second
        else:
            interval = 1 / (bcd_value * 2)#sets the interval between flashes based on the bcd value CALCULATES THE TIME BETWEEN EACH TOGGLE FOR EXAMPLE IF bcd value = 1 it will flash 2 times the interval will be 1/(1*2) = 0.5 seconds so it will turn on for 0.5 seconds and then off for 0.5 seconds and repeat until the total time for this bcd value has passed so if interval is 0.5 and it flashes 2 times total time = 0.5*2 =1 second THE HIGHER THE NUMBER , THE FASTER IT BLINKS

            for _ in range(bcd_value * 2):#the number of flashes is equal to the bcd value loops   BECAUSE ONE FULL BLINK 2 TOGGLES ON AND OFF
                GPIO.output(led, not GPIO.input(led))#flips the state of the LED READS THE CURRENT PIN STATE AND NOT FLIPS IT THEN WRITES IT BACK SO EACH ITERATION TOGGLES THE LED. THEN WAITS INTERVAL SECONDS BEFORE THE NEXT TOGGLE
                time.sleep(interval)#waits for the interval to pass before flipping the state of the LED again

except KeyboardInterrupt:
    GPIO.cleanup()