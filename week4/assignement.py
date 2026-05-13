import RPi.GPIO as GPIO #import GPIO library
import smbus #import smbus library
import time #import time library

# --- Hardware config ---
R_PIN      = 5 #red led pin
G_PIN      = 6#green led pin
B_PIN      = 13#blue led pin
BUTTON_PIN = 20#button pin

ADC_ADDR = 0x48   # ADS7830 I2C address of the ADS7830 chip on the bus 
CMD_R    = 0x94   # AIN2 (red pot) bit 7 = 1 means single-ended.   this is the command to read the red pot from the ADC
CMD_G    = 0xD4   # AIN3 (green pot) bit 7 = 1 means single-ended.   this is the command to read the green pot from the ADC
CMD_B    = 0xA4   # AIN4 (blue pot) bit 7 = 1 means single-ended.   this is the command to read the blue pot from the ADC
VREF     = 3.3# reference voltage (5V). Used to convert the raw ADC value (0–255) back into a real voltage: voltage = value * 5.0 / 255
#Bits 6-4 = which channel (AIN0-AIN7) 3-2 = power mode (keep ADC on between reads)       
# CMD_r,CMD_G CMD_B are not adresses of the pots themselves,they are instructions to send to the ADC chip saying please read the voltage on the pin where that pot is connected.                                                
# --- GPIO setup ---
GPIO.setwarnings(False)#set warnings to false
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)#set mode to BCM

GPIO.setup(R_PIN,      GPIO.OUT)#set red led pin to output
GPIO.setup(G_PIN,      GPIO.OUT)#set green led pin to output
GPIO.setup(B_PIN,      GPIO.OUT)#set blue led pin to output
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)#set button pin to input with pull-up resistor

# --- PWM (1000 Hz, start fully off for common anode) ---
pwm_r = GPIO.PWM(R_PIN, 1000)#set red led pwm 
# Pulse width modulation — a way to fake analog brightness using a digital pin. A digital pin can only be fully ON (3.3V) or fully OFF (0V). PWM rapidly switches the pin on and off many times per second. The ratio of on-time to off-time controls how bright the LED appears:
#
# 100% duty cycle: |‾‾‾‾‾‾‾‾‾‾| fully on
#  50% duty cycle: |‾‾‾‾‾_____| half on, half off
#   0% duty cycle: |__________| fully off
pwm_g = GPIO.PWM(G_PIN, 1000)#set green led pwm
pwm_b = GPIO.PWM(B_PIN, 1000)#set blue led pwm
pwm_r.start(100)#start red led pwm
pwm_g.start(100)#start green led pwm
pwm_b.start(100)#start blue led pwm

# --- I2C / ADC ---
bus = smbus.SMBus(1)#set i2c bus

def read_adc(command):
    bus.write_byte(ADC_ADDR, command)#write command to i2c bus send the command to the ADC chip on the I2C bus to start a conversion
    bus.read_byte(ADC_ADDR)          # discard stale conversion The first read after a write returns the result of the *previous* conversion, not the one you just triggered.
    value   = bus.read_byte(ADC_ADDR)#read adc value This is the 8-bit measurement from the ADC, ranging from 0 to 255. When you turn the potentiometer:  • fully counter-clockwise: ~0 (0V)  • half way: ~128 (2.5V)  • fully clockwise: ~255 (5V)
    voltage = value * VREF / 255#convert adc value to voltage Converts the raw 0–255 number back into real volts (0.00V to 5.00V):

   # 0V   = 0 * 5.0 / 255 = 0.00V  (pot at minimum)
   # 2.5V = 128 * 5.0 / 255 = 2.51V (pot halfway)
   # 5V   = 255 * 5.0 / 255 = 5.00V (pot at maximum)
    return value, voltage#return adc value and voltage

# Common anode: invert duty cycle so higher pot = brighter
def to_duty(adc_value):#convert adc value to duty cycle
    return 100 - (adc_value * 100 / 255)#invert duty cycle so higher pot = brighter convert the raw adc value (0–255) into a percentage (0–100)  • pot at minimum → 0 * 100 / 255 = 0%  • pot at half → 128 * 100 / 255 = 50%  • pot at maximum → 255 * 100 / 255 = 100% nverts it because your LED is common anode (lower duty cycle = brighter):┌──────────────┬───────────┬───────────────────┬────────────────┬─────────────────┐ │ Pot position │ ADC value │ Without inversion │ With inversion │   LED result    │ ├──────────────┼───────────┼───────────────────┼────────────────┼─────────────────┤ │ Minimum      │ 0         │ 0%                │ 100%           │ Off             │ ├──────────────┼───────────┼───────────────────┼────────────────┼─────────────────┤ │ Half         │ 128       │ 50%               │ 50%            │ Half bright     │ ├──────────────┼───────────┼───────────────────┼────────────────┼─────────────────┤ │ Maximum      │ 255       │ 100%              │ 0%             │ Full brightness │ └──────────────┴───────────┴───────────────────┴────────────────┴─────────────────┘   

# --- System state ---
system_on = True#set system state

def toggle_system(channel):#toggle system
    global system_on#global variable    
    system_on = not system_on#toggle system state
    print("System:", "ON" if system_on else "OFF")#print system state

GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=toggle_system, bouncetime=200)#detect button press   make button work without polling instead of checkign hr button very sae evry loop, you register it once and the i calls toogle system automatically when it detects a button press.

# --- Main loop ---
try:
    while True:
        if system_on:#if system is on
            r, vr = read_adc(CMD_R)#read adc value for red led   This returns two things:  • r — the raw 8-bit value (0–255)  • vr — the voltage (0.00V – 5.00V)
            g, vg = read_adc(CMD_G)#read adc value for green led  This returns two things:  • g — the raw 8-bit value (0–255)  • vg — the voltage (0.00V – 5.00V)
            b, vb = read_adc(CMD_B)#read adc value for blue led   This returns two things:  • b — the raw 8-bit value (0–255)  • vb — the voltage (0.00V – 5.00V)

            pwm_r.ChangeDutyCycle(to_duty(r))#update the red led duty cycle  Converts the raw 0–255 number back into real volts (0.00V to 5.00V): 0V   = 0 * 5.0 / 255 = 0.00V  (pot at minimum) 2.5V = 128 * 5.0 / 255 = 2.51V (pot halfway) 5V   = 255 * 5.0 / 255 = 5.00V (pot at maximum)   
            pwm_g.ChangeDutyCycle(to_duty(g))#update the green led duty cycle  Converts the raw 0–255 number back into real volts (0.00V to 5.00V): 0V   = 0 * 5.0 / 255 = 0.00V  (pot at minimum) 2.5V = 128 * 5.0 / 255 = 2.51V (pot halfway) 5V   = 255 * 5.0 / 255 = 5.00V (pot at maximum)   
            pwm_b.ChangeDutyCycle(to_duty(b))#update the blue led duty cycle  Converts the raw 0–255 number back into real volts (0.00V to 5.00V): 0V   = 0 * 5.0 / 255 = 0.00V  (pot at minimum) 2.5V = 128 * 5.0 / 255 = 2.51V (pot halfway) 5V   = 255 * 5.0 / 255 = 5.00V (pot at maximum)   

            print(f"R: {r:3d} ({vr:.2f}V)  G: {g:3d} ({vg:.2f}V)  B: {b:3d} ({vb:.2f}V)")#print adc values and voltages
        else:
            # Never fully off — dim white glow at 95% (common anode)
            pwm_r.ChangeDutyCycle(95)#change red led duty cycle all three channels are set to 95% duty cycle
            pwm_g.ChangeDutyCycle(95)#change green led duty cycle very dim white glow
            pwm_b.ChangeDutyCycle(95)#change blue led duty cycle all three channels are set to 95% duty cycle

        time.sleep(0.1)#wait for 0.1 seconds

except KeyboardInterrupt:
    print("Exiting...")#print exiting message
    pwm_r.stop()#stop red led pwm
    pwm_g.stop()#stop green led pwm
    pwm_b.stop()#stop blue led pwm
    bus.close()#close i2c bus
    GPIO.cleanup()#cleanup gpio pins
