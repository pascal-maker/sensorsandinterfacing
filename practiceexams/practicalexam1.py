from RPi import GPIO # import GPIO library
import smbus # import smbus library for I2C communication
import time # import time library for delays
from datetime import datetime # import datetime library for date and time

# GPIO Setup
GPIO.setmode(GPIO.BCM)# set the GPIO mode to BCM

# LCD I2C Configuration
I2C_ADDR = 0x27 # LCD I2C address
LCD_WIDTH = 16 # LCD width
LCD_CHR = 1  # Sending data
LCD_CMD = 0  # Sending command
LCD_LINE_1 = 0x80 # LCD line 1
LCD_LINE_2 = 0xC0 # LCD line 2
LCD_BACKLIGHT = 0x08 # LCD backlight
ENABLE = 0x04 # LCD enable
E_PULSE = 0.0002 # LCD pulse
E_DELAY = 0.0002 # LCD delay

i2c = smbus.SMBus(1) # I2C bus

# Button pins
PLANT_BUTTON_PIN = 20  # Button 1
DEFUSE_BUTTON_PIN = 21  # Button 2
BUTTON_3_PIN = 16      # Button 3
BUTTON_4_PIN = 26      # Button 4

# RGB LED pins (PWM for colors)
RED_PIN = 5 # RGB LED red pin
GREEN_PIN = 6 # RGB LED green pin
BLUE_PIN = 13 # RGB LED blue pin

# Buzzer pin
BUZZER_PIN = 12 # Buzzer pin

# Setup GPIO pins
GPIO.setup(PLANT_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)# setup plant button as input with pull up
GPIO.setup(DEFUSE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)# setup defuse button as input with pull up
GPIO.setup(BUTTON_3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)# setup button 3 as input with pull up
GPIO.setup(BUTTON_4_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)# setup button 4 as input with pull up
GPIO.setup(RED_PIN, GPIO.OUT)# setup red led as output
GPIO.setup(GREEN_PIN, GPIO.OUT)# setup green led as output
GPIO.setup(BLUE_PIN, GPIO.OUT)# setup blue led as output
GPIO.setup(BUZZER_PIN, GPIO.OUT)# setup buzzer as output

# RGB LED Configuration (Common Anode)
RGB_COMMON_ANODE = True # RGB LED common anode

# Initialize PWM for RGB LED
pwm_red = GPIO.PWM(RED_PIN, 1000)# PWM for red led
pwm_green = GPIO.PWM(GREEN_PIN, 1000)# PWM for green led
pwm_blue = GPIO.PWM(BLUE_PIN, 1000)# PWM for blue led

if RGB_COMMON_ANODE:
    pwm_red.start(100)# start red led
    pwm_green.start(100)# start green led
    pwm_blue.start(100)# start blue led
else:
    pwm_red.start(0)# stop red led
    pwm_green.start(0)# stop green led
    pwm_blue.start(0)# stop blue led

# LCD Helper Functions
def set_data_bits(bits, mode):# send data bits to the lcd   
    """Send data to the LCD with enable toggling."""
    data_byte = bits | mode | LCD_BACKLIGHT # set data byte with mode and backlight
    i2c.write_byte(I2C_ADDR, data_byte)# write data byte to the lcd
    time.sleep(E_DELAY)# delay for e pulse
    data_byte |= ENABLE# set enable pin
    i2c.write_byte(I2C_ADDR, data_byte)# write data byte to the lcd
    time.sleep(E_PULSE)# delay for e pulse
    data_byte &= ~ENABLE# clear enable pin
    i2c.write_byte(I2C_ADDR, data_byte)# write data byte to the lcd
    time.sleep(E_DELAY)# delay for e pulse

def send_byte_with_e_toggle(byte, mode):# send byte with e toggle
    """Send a byte in two nibbles (4-bit mode)."""
    high_nibble = (byte & 0xF0)# high nibble of the byte
    low_nibble = ((byte << 4) & 0xF0)# low nibble of the byte
    set_data_bits(high_nibble, mode)# set data bits
    set_data_bits(low_nibble, mode)# set data bits

def send_instruction(value):# send instruction to the lcd
    """Send a command to the LCD."""
    send_byte_with_e_toggle(value, LCD_CMD)# send byte with e toggle

def send_character(value):# send character to the lcd
    """Send a single character to the LCD."""
    send_byte_with_e_toggle(value, LCD_CHR)# send byte with e toggle

def init_LCD():# initialize the lcd
    """Initialize the LCD in 4-bit mode."""
    set_data_bits(0x30, LCD_CMD)# set data bits
    time.sleep(0.005)# delay for e pulse
    set_data_bits(0x30, LCD_CMD)# set data bits
    time.sleep(0.005)# delay for e pulse
    set_data_bits(0x30, LCD_CMD)# set data bits
    time.sleep(0.005)# delay for e pulse
    set_data_bits(0x20, LCD_CMD)
    send_instruction(0x28)  # 4-bit, 2 lines, 5x8 font
    send_instruction(0x0C)  # Display on, cursor off
    send_instruction(0x01)  # Clear display
    time.sleep(0.002)# delay for e pulse

def send_string(message, line):# send string to the lcd
    """Send a string to the specified line on the LCD."""
    send_instruction(line)# send line to the lcd
    for i in range(LCD_WIDTH):# loop through the lcd width
        if i < len(message):# check if i is less than the length of the message
            send_character(ord(message[i]))# send character
        else:
            send_character(ord(' '))# send space

def draw_progress_bar(percent, line):# draw progress bar on the lcd
    """Draw a progress bar on the LCD (0-100%)"""
    # 16 characters wide progress bar
    # Use full blocks (255 = █) to show progress
    filled_blocks = int((percent / 100.0) * LCD_WIDTH)# calculate filled blocks
    
    send_instruction(line)# send line to the lcd
    for i in range(LCD_WIDTH):# loop through the lcd width
        if i < filled_blocks:# check if i is less than filled blocks
            send_character(255)  # Full block character
        else:
            send_character(ord(' '))  # Empty space

def clear_lcd():# clear the lcd
    """Clear the LCD display."""
    send_instruction(0x01)# send instruction to clear the lcd
    time.sleep(0.002)# delay for e pulse

# Initialize LCD
init_LCD()

# MPU6050 Class for movement detection
class MPU6050:
    def __init__(self, address=0x68):# initialize the mpu6050
        self.address = address# mpu6050 address
        self.i2c = smbus.SMBus(1)# i2c bus
        
        # Register addresses
        self.REG_SETUP = 0x6B# setup register
        self.REG_ACC_CONFIG = 0x1C# accelerometer configuration register
        self.REG_GYRO_CONFIG = 0x1B# gyroscope configuration register
        self.REG_ACC = 0x3B# accelerometer data register
        self.REG_TEMP = 0x41# temperature data register
        self.REG_GYRO = 0x43# gyroscope data register
        
        # Initialize sensor
        self.i2c.write_byte_data(self.address, self.REG_SETUP, 1)# setup sensor
        self.i2c.write_byte_data(self.address, self.REG_ACC_CONFIG, 0x00)# accelerometer configuration
        self.i2c.write_byte_data(self.address, self.REG_GYRO_CONFIG, 0x00)# gyroscope configuration
    
    def __combine_bytes(self, msb, lsb):# combine bytes
        return (msb << 8) | lsb# combine bytes
    
    def __to_signed(self, val):# convert to signed
        if val & 0x8000:# check if the value is negative
            val -= 65536# convert to negative
        return val# return the value
    
    def read_acceleration(self):# read acceleration
        data = self.i2c.read_i2c_block_data(self.address, self.REG_ACC, 6)# read acceleration data
        x = self.__to_signed(self.__combine_bytes(data[0], data[1])) / 16384# convert to signed
        y = self.__to_signed(self.__combine_bytes(data[2], data[3])) / 16384# convert to signed
        z = self.__to_signed(self.__combine_bytes(data[4], data[5])) / 16384# convert to signed
        return (x, y, z)# return the value
    
    def read_gyroscope(self):# read gyroscope
        data = self.i2c.read_i2c_block_data(self.address, self.REG_GYRO, 6)# read gyroscope data
        x = self.__to_signed(self.__combine_bytes(data[0], data[1])) / 131# convert to signed
        y = self.__to_signed(self.__combine_bytes(data[2], data[3])) / 131# convert to signed
        z = self.__to_signed(self.__combine_bytes(data[4], data[5])) / 131# convert to signed
        return (x, y, z)# return the value

# Initialize MPU6050
mpu = MPU6050()# initialize the mpu6050

# CS:GO Bomb States
STATE_IDLE = 0# idle state
STATE_ARMED = 1# armed state
STATE_DEFUSED = 2# defused state
STATE_EXPLODED = 3# exploded state

# Bomb configuration
BOMB_TIMER = 40  # 40 seconds like CS:GO
DEFUSE_TIME = 10  # 10 seconds to defuse
BEEP_INTERVAL_START = 1.0  # Initial beep interval (seconds)
BEEP_INTERVAL_FAST = 0.1   # Fast beep interval when time is running out

class CSGOBomb:
    def __init__(self):# initialize the bomb
        self.state = STATE_IDLE# set the state to idle
        self.time_remaining = BOMB_TIMER# set the time remaining
        self.defuse_progress = 0# set the defuse progress
        self.last_beep_time = 0# set the last beep time
        self.plant_time = 0# set the plant time
        self.last_button_press = 0# set the last button press
        self.baseline_accel = None# baseline acceleration
        self.baseline_gyro = None# baseline gyroscope
        self.movement_threshold_accel = 1.2  # Movement sensitivity for accelerometer
        self.movement_threshold_gyro = 50    # Movement sensitivity for gyroscope
        self.movement_grace_seconds = 1.5    # Ignore movement just after planting
        self.defuse_code = [20, 21, 16, 26, 20, 21, 16]  # 7-button sequence using all 4 buttons
        self.current_input = []  # Track button presses
        self.defuse_attempts = 0# number of defuse attempts
        self.max_attempts = 3# maximum number of defuse attempts
        
    def set_rgb(self, red, green, blue):# set rgb color
        """Set RGB LED color (0-100)"""
        if RGB_COMMON_ANODE:# check if the rgb is common anode
            pwm_red.ChangeDutyCycle(100 - red)# set rgb color
            pwm_green.ChangeDutyCycle(100 - green)# set rgb color
            pwm_blue.ChangeDutyCycle(100 - blue)# set rgb color
        else:
            pwm_red.ChangeDutyCycle(red)# set rgb color
            pwm_green.ChangeDutyCycle(green)# set rgb color
            pwm_blue.ChangeDutyCycle(blue)# set rgb color
    
    def beep(self, duration=0.05):# make a beep sound
        """Make a beep sound"""
        GPIO.output(BUZZER_PIN, GPIO.HIGH)# set buzzer to high
        time.sleep(duration)# delay for duration
        GPIO.output(BUZZER_PIN, GPIO.LOW)# set buzzer to low
    
    def plant_bomb(self):# plant the bomb
        """Plant the bomb and start countdown"""
        if self.state == STATE_IDLE:# check if the state is idle
            self.state = STATE_ARMED# set the state to armed
            self.time_remaining = BOMB_TIMER# set the time remaining
            self.plant_time = time.time()# set the plant time
            self.last_beep_time = time.time()# set the last beep time
            # Record baseline position when bomb is planted
            self.baseline_accel = mpu.read_acceleration()# read acceleration
            self.baseline_gyro = mpu.read_gyroscope()# read gyroscope
            self.current_input = []  # Reset code input
            self.defuse_attempts = 0# number of defuse attempts
            print("BOMB PLANTED!")# print bomb planted
            print("WARNING: DO NOT MOVE THE BOMB!")# print warning do not move the bomb
            print(f"DEFUSE CODE: Press buttons in sequence:")# print defuse code
            code_str = ", ".join([f"BTN{[20,21,16,26].index(x)+1}" for x in self.defuse_code])# format the defuse code
            print(f"  {code_str}")# print the defuse code
            self.beep(0.2)# make a beep sound
    
    def add_button_to_code(self, button_pin):# add button press to defuse code sequence
        """Add button press to defuse code sequence"""
        if self.state != STATE_ARMED:# check if the state is armed
            return
        
        self.current_input.append(button_pin)# add button press to code input
        print(f"Code input: {len(self.current_input)}/{len(self.defuse_code)}")# print code input
        
        # Check if we have enough inputs
        if len(self.current_input) >= len(self.defuse_code):# check if we have enough inputs
            if self.current_input == self.defuse_code:# check if the code input is correct
                # Correct code!
                self.defuse_bomb()#
            else:
                # Wrong code
                self.defuse_attempts += 1# increment the number of defuse attempts
                print(f"WRONG CODE! Attempts: {self.defuse_attempts}/{self.max_attempts}")# print wrong code
                if self.defuse_attempts >= self.max_attempts:# check if the number of defuse attempts is greater than or equal to the maximum number of defuse attempts
                    print("TOO MANY FAILED ATTEMPTS!")# print too many failed attempts
                    self.explode("ANTI-TAMPER TRIGGERED!")# explode the bomb
                else:
                    # Reset input and let them try again
                    self.current_input = []# reset the code input
                    self.beep(0.05)# make a beep sound
                    time.sleep(0.1)# delay for duration
                    self.beep(0.05)# make a beep sound
    
    def defuse_bomb(self):# defuse the bomb
        """Successfully defuse the bomb"""
        if self.state == STATE_ARMED:# check if the state is armed
            self.state = STATE_DEFUSED# set the state to defused
            print("BOMB DEFUSED!")# print bomb defused
            # Play success sound
            for _ in range(3):# loop 3 times
                self.beep(0.1)# make a beep sound
                time.sleep(0.1)# delay for duration
    
    def check_movement(self):# check if bomb has been moved
        """Check if bomb has been moved"""
        if self.state != STATE_ARMED or self.baseline_accel is None:#check if the state is armed or baseline acceleration is None
            return False# return false#ignore if not armed or baseline not set

        if time.time() - self.plant_time < self.movement_grace_seconds:# ignore sensor noise after planting
            return False# return false#ignore if time is less than movement grace seconds
        
        try:
            # Read current position
            current_accel = mpu.read_acceleration()# read acceleration
            current_gyro = mpu.read_gyroscope()# read gyroscope
            
            # Calculate differences from baseline
            accel_diff = sum(abs(current_accel[i] - self.baseline_accel[i]) for i in range(3))# calculate acceleration difference
            gyro_diff = sum(abs(current_gyro[i] - self.baseline_gyro[i]) for i in range(3))# calculate gyroscope difference
            
            # Check if movement exceeds threshold
            if accel_diff > self.movement_threshold_accel or gyro_diff > self.movement_threshold_gyro:# check if movement exceeds threshold
                print(f"MOVEMENT DETECTED! Accel: {accel_diff:.2f}, Gyro: {gyro_diff:.2f}")# print movement detected
                return True
        except:
            pass  # Ignore sensor errors
        
        return False
    
    def explode(self, reason="TERRORISTS WIN!"):# explode the bomb
        """Bomb explodes!"""
        self.state = STATE_EXPLODED# set the state to exploded
        print(f"BOMB EXPLODED! {reason}")# print bomb exploded
        # Play explosion sound
        for _ in range(10):# loop 10 times
            self.beep(0.05)# make a beep sound
            time.sleep(0.05)# delay for duration
    
    def reset(self):# reset the bomb
        """Reset the bomb"""
        self.state = STATE_IDLE# set the state to idle
        self.time_remaining = BOMB_TIMER# set the time remaining
        self.defuse_progress = 0# set the defuse progress
        clear_lcd()# clear the lcd
        self.set_rgb(0, 0, 0)# set rgb color
        print("BOMB RESET")# print bomb reset
    
    def update(self):# update the bomb
        """Main update loop"""
        current_time = time.time()# get the current time
        
        if self.state == STATE_IDLE:# check if the state is idle
            # Blue LED when idle
            self.set_rgb(0, 0, 100)# set rgb color
            send_string(" CS:GO BOMB SIM", LCD_LINE_1)# send string to lcd
            send_string("Press to PLANT!", LCD_LINE_2)# send string to lcd
            
        elif self.state == STATE_ARMED:# check if the state is armed
            # Check for movement - if moved, explode immediately!
            if self.check_movement():# check if bomb has been moved
                send_string("MOVEMENT DET!  ", LCD_LINE_1)# send string to lcd
                send_string("BOMB TRIGGERED!", LCD_LINE_2)# send string to lcd
                time.sleep(1)# delay for duration
                self.explode("TAMPER DETECTED!")# explode the bomb
                return
            
            # Calculate time remaining
            elapsed = current_time - self.plant_time# calculate time elapsed
            self.time_remaining = BOMB_TIMER - elapsed# calculate time remaining
            
            if self.time_remaining <= 0:# check if time remaining is less than or equal to 0
                self.explode()# explode the bomb
                return
            
            # Red LED when armed
            self.set_rgb(100, 0, 0)# set rgb color
            
            # Display countdown as progress bar on LCD
            percent_remaining = (self.time_remaining / BOMB_TIMER) * 100# calculate percentage remaining
            draw_progress_bar(percent_remaining, LCD_LINE_1)# draw progress bar on lcd
            
            # Show status or defuse progress
            if len(self.current_input) > 0:# check if we have any code input
                progress_str = f"Code:{len(self.current_input)}/{len(self.defuse_code)} Tries:{self.defuse_attempts}"
                send_string(progress_str, LCD_LINE_2)# send string to lcd
                # Show defuse progress with LED (green mixed with red)
                green_amount = int((len(self.current_input) / len(self.defuse_code)) * 100)# calculate green amount
                self.set_rgb(100 - green_amount, green_amount, 0)# set rgb color
            elif self.defuse_attempts > 0:# check if we have any defuse attempts
                attempts_str = f"Tries:{self.defuse_attempts}/{self.max_attempts}     "# format the attempts string
                send_string(attempts_str, LCD_LINE_2)# send string to lcd
            else:
                send_string("Enter Code!    ", LCD_LINE_2)# send string to lcd
            
            # Calculate beep interval (faster as time runs out)
            if self.time_remaining < 10:# check if time remaining is less than 10
                beep_interval = BEEP_INTERVAL_FAST# set beep interval to fast
            elif self.time_remaining < 20:# check if time remaining is less than 20
                beep_interval = 0.5# set beep interval to 0.5
            else:
                beep_interval = BEEP_INTERVAL_START# set beep interval to start
            
            # Beep at intervals
            if current_time - self.last_beep_time >= beep_interval:# check if current time minus last beep time is greater than or equal to beep interval
                self.beep()# make a beep sound
                self.last_beep_time = current_time# set last beep time to current time
            
        elif self.state == STATE_DEFUSED:
            # Green LED when defused
            self.set_rgb(0, 100, 0)# set rgb color
            send_string("BOMB DEFUSED!! ", LCD_LINE_1)# send string to lcd
            percent_remaining = (self.time_remaining / BOMB_TIMER) * 100# calculate percentage remaining
            seconds_left = int(self.time_remaining)# calculate seconds remaining
            bar_str = f"{seconds_left}s "# format the seconds string
            send_string(bar_str.center(LCD_WIDTH), LCD_LINE_2)# send string to lcd
            time.sleep(0.01)# delay for duration
            
        elif self.state == STATE_EXPLODED:
            # Flashing red LED when exploded
            flash = int(current_time * 5) % 2# calculate flash
            if flash:# check if flash is true
                self.set_rgb(100, 0, 0)# set rgb color
            else:
                self.set_rgb(0, 0, 0)# set rgb color
            send_string(" BOMB EXPLODED! ", LCD_LINE_1)# send string to lcd
            send_string("TERRORISTS WIN! ", LCD_LINE_2)# send string to lcd
            time.sleep(0.01)# delay for duration

# Create bomb instance
bomb = CSGOBomb() # create bomb instance

# Button debounce tracking
last_plant_press = 0 # track last plant button press time
last_defuse_press = 0 # track last defuse button press time
last_button3_press = 0 # track last button 3 press time
last_button4_press = 0 # track last button 4 press time

def plant_button_callback(channel):# handle plant button press  
    """Handle plant button press"""
    global last_plant_press# use global variable for last plant button press time
    current_time = time.time()
    if current_time - last_plant_press > 0.3:# check if current time minus last plant button press time is greater than or equal to 0.3
        last_plant_press = current_time# set last plant button press time to current time
        if bomb.state == STATE_IDLE:# check if the state is idle
            bomb.plant_bomb()# plant the bomb
        elif bomb.state == STATE_ARMED:# check if the state is armed
            bomb.add_button_to_code(channel)# add button to code
        elif bomb.state in [STATE_DEFUSED, STATE_EXPLODED]:# check if the state is defused or exploded
            bomb.reset()# reset the bomb

def defuse_button_callback(channel):  # handle defuse button press  
    """Handle defuse button press"""
    global last_defuse_press# use global variable for last defuse button press time
    current_time = time.time()
    if current_time - last_defuse_press > 0.3:# check if current time minus last defuse button press time is greater than or equal to 0.3
        last_defuse_press = current_time# set last defuse button press time to current time
        if bomb.state == STATE_ARMED:# check if the state is armed
            bomb.add_button_to_code(channel)# add button to code

def button3_callback(channel):  # handle button 3 press  
    """Handle button 3 press"""
    global last_button3_press# use global variable for last button 3 press time
    current_time = time.time()
    if current_time - last_button3_press > 0.3:# check if current time minus last button 3 press time is greater than or equal to 0.3
        last_button3_press = current_time# set last button 3 press time to current time
        if bomb.state == STATE_ARMED:# check if the state is armed
            bomb.add_button_to_code(channel)

def button4_callback(channel):  # handle button 4 press  
    """Handle button 4 press"""
    global last_button4_press# use global variable for last button 4 press time
    current_time = time.time()
    if current_time - last_button4_press > 0.3:# check if current time minus last button 4 press time is greater than or equal to 0.3
        last_button4_press = current_time# set last button 4 press time to current time
        if bomb.state == STATE_ARMED:# check if the state is armed
            bomb.add_button_to_code(channel)# add button to code

# Setup button interrupts#
GPIO.add_event_detect(PLANT_BUTTON_PIN, GPIO.FALLING, callback=plant_button_callback, bouncetime=300)# set plant button interrupt
GPIO.add_event_detect(DEFUSE_BUTTON_PIN, GPIO.FALLING, callback=defuse_button_callback, bouncetime=300)# set defuse button interrupt
GPIO.add_event_detect(BUTTON_3_PIN, GPIO.FALLING, callback=button3_callback, bouncetime=300)# set button 3 interrupt
GPIO.add_event_detect(BUTTON_4_PIN, GPIO.FALLING, callback=button4_callback, bouncetime=300)# set button 4 interrupt

print("=" * 50)# print separator line
print("CS:GO BOMB SIMULATOR WITH MOVEMENT DETECTION")# print the title of the program
print("=" * 50)# print separator line
print("Controls:")# print the controls section header
print(f"  GPIO {PLANT_BUTTON_PIN}: BTN1 - PLANT BOMB / RESET / CODE INPUT")# print plant button controls
print(f"  GPIO {DEFUSE_BUTTON_PIN}: BTN2 - CODE INPUT")# print defuse button controls
print(f"  GPIO {BUTTON_3_PIN}: BTN3 - CODE INPUT")# print button 3 controls
print(f"  GPIO {BUTTON_4_PIN}: BTN4 - CODE INPUT")# print button 4 controls
print("=" * 50)# print separator line
print("Defuse: Enter 7-button code sequence using all 4 buttons")# print defuse instructions
print("WARNING: Do not move the bomb once planted!")# print warning message
print("Movement will trigger immediate explosion!")# print warning message
print("Max 3 attempts to enter correct code!")# print warning message
print("=" * 50)# print separator line
print("Ready! Press PLANT button to begin...")# print ready message

try:
    while True:
        bomb.update()# update the bomb
        time.sleep(0.01)  # Small delay for smooth operation
        
except KeyboardInterrupt:# handle keyboard interrupt
    print("\n\nExiting...")# print exiting message
    
finally:# handle finally block
    clear_lcd()# clear the lcd
    bomb.set_rgb(0, 0, 0)# set rgb color to black
    GPIO.output(BUZZER_PIN, GPIO.LOW)# set buzzer to off
    pwm_red.stop()# stop red pwm
    pwm_green.stop()# stop green pwm
    pwm_blue.stop()# stop blue pwm
    i2c.close()# close the i2c connection
    GPIO.cleanup()# cleanup the gpio
    print("Cleanup complete.")# print cleanup complete message
