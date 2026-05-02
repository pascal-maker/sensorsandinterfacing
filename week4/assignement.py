from RPi import GPIO#importing GPIO module 
import smbus#importing smbus module for i2c communication
import time #importing time module for delays

#RGB pins
RED = 17#red led pin
GREEN = 27#green led pin
BLUE = 22#blue led pin

#BUTTON
BUTTON_PIN = 20#button pin
#I2C address
bus = smbus.SMBus(1)#set the i2c bus
address = 0x48#set the address the 7-bit i2c address of the target device default adress of common adc chips like ADS1115 or each device on the i2d bus has a unique address 
#state
system_on = True#system state wheteher the system is currently running likely to allow shutdown 
 

GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)#set the mode

for pin in [RED,GREEN,BLUE]:#
    GPIO.setup(pin, GPIO.OUT)#set the pins as output

#button input (pull_up)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)#set the button pin as input with pull up resistor
#PWM setup a digital pin can only be fully on or off pwm fakes analog brightness by rapidly toggling the pin the longer it stays on per cycle the brighter the LED appears
pwm_r = GPIO.PWM(RED, 100)#set the pwm for red led
pwm_g = GPIO.PWM(GREEN, 100)#set the pwm for green led
pwm_b = GPIO.PWM(BLUE, 100)#set the pwm for blue led
pwm_r.start(0)#start the pwm for red led
pwm_g.start(0)#start the pwm for green led
pwm_b.start(0)#start the pwm for blue led

#ADC reading functions
def read_adc(channel):#function to read the adc channel takes one argument channel which is the channel number of the ADC to read usually 0-3
    command = 0x84 | ((channel & 0x07) << 4)#set the command for the adc (0x84) | ((channel & 0x07) << 4) constructs a command byte: 0x84 sets the single-ended input mode and start bit for the PCF8591 ADC; (channel & 0x07) masks the channel to 3 bits (valid channels 0-3); << 4 shifts the channel bits into the correct position in the command byte; | combines them into one byte to send
    bus.write_byte(address, command)#write the command to the bus  sends the command byte to the ADC over the I2C bus telling it which channel to read
    value = bus.read_byte(address)#read the value from the bus reads the 8-bit result back (0-255), representing the analog voltage on that channel
    return value#return the value

def toggle_system(channel):#function to toggle the system takes one argument channel which is the channel number of the button that triggered the interrupt usually the pin number of the button
    global system_on#set the system state not a local copy
    system_on = not system_on#toggle the system state flips the state - if it was true it becomes false and vice versa
    print("System:","ON"if system_on else "OFF")#print the system state if true print "ON" else print "OFF"

GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=toggle_system, bouncetime=200)#set the event detect for the button detects a falling edge (transition from high to low) on the button pin calls the toggle_system function when detected with a debounce time of 200 milliseconds

try:
    while True:
        if system_on:#active mode
            #read potentiometers
            r_val = read_adc(2)#read the red channel read the potentiometers from adc channels 2,3,4 each returns a value 0-255 representing the wiper position of the pot 0v 0 3.3v 255
            g_val = read_adc(3)#read the green channel read the potentiometers from adc channels 2,3,4 each returns a value 0-255 representing the wiper position of the pot 0v 0 3.3v 255
            b_val = read_adc(4)#read the blue channel read the potentiometers from adc channels 2,3,4 each returns a value 0-255 representing the wiper position of the pot 0v 0 3.3v 255

            #convert to pwm duty cycle 0-100
            r_pwm = (r_val/255)*100#convert to pwm converts the 0-255 adc range to a 0-100 pwm duty cycle percentage adc reads 0 pwm 0 fully off adc reads 128 pwm ~50 half brightness adc reads 255 pwm 100 fully bright
            g_pwm = (g_val/255)*100#convert to pwm converts the 0-255 adc range to a 0-100 pwm duty cycle percentage adc reads 0 pwm 0 fully off adc reads 128 pwm ~50 half brightness adc reads 255 pwm 100 fully bright
            b_pwm = (b_val/255)*100#convert to pwm converts the 0-255 adc range to a 0-100 pwm duty cycle percentage adc reads 0 pwm 0 fully off adc reads 128 pwm ~50 half brightness adc reads 255 pwm 100 fully bright
        else:#standby mode
            r_pwm = 5#set the pwm for red led forces all three channels to 5% duty cycle a very dim white glow this acts as a visual indicator that the system is off but still powered rather than going completely dark
            g_pwm = 5#set the pwm for green led forces all three channels to 5% duty cycle a very dim white glow this acts as a visual indicator that the system is off but still powered rather than going completely dark
            b_pwm = 5#set the pwm for blue led forces all three channels to 5% duty cycle a very dim white glow this acts as a visual indicator that the system is off but still powered rather than going completely dark

        #apply
        pwm_r.ChangeDutyCycle(r_pwm)#apply the pwm for red led sets the red led brightness to r_pwm percent updates the live pwm signal  on each pin with the enwly calcualed duty cycle. actualy chanegs the eld brightness without this step 
        pwm_g.ChangeDutyCycle(g_pwm)#apply the pwm for green led sets the green led brightness to g_pwm percent hold values between 0-100 percent  ( 0-255)
        pwm_b.ChangeDutyCycle(b_pwm)#apply the pwm for blue led sets the blue led brightness to b_pwm percent    hold values between 0-100 percent (0-255) 
        #the led pyschically changes color/brightness  the moment is caled
        time.sleep(0.5)#wait for 0.5 seconds 
     
except KeyboardInterrupt:
    print("Cleaning up and exiting")#print that the system is cleaning up and exiting
    pwm_r.stop()#stop the pwm for red led stops the pwm signal on each led pin this halts the rapid on/off switching of the red led  which effectively turns it off 
    pwm_g.stop()#stop the pwm for green led stops the pwm signal on each led pin this halts the rapid on/off switching of the green led  which effectively turns it off
    pwm_b.stop()#stop the pwm for blue led stops the pwm signal on each led pin this halts the rapid on/off switching of the blue led  which effectively turns it off
    GPIO.cleanup()#cleanup the GPIO pins releases control of all GPIO pins used in the script back to the operating system to prevent issues with future scripts or unexpected behavior

