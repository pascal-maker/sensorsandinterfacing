import RPi.GPIO as GPIO
import smbus
import time

# ----------------------------
# GPIO + I2C setup
# ----------------------------
GPIO.setmode(GPIO.BCM)
#set the i2c bus
i2c = smbus.SMBus(1)
#set the ADC address
ADC_ADDRESS = 0x48

# RGB pins
RED_PIN = 18
GREEN_PIN = 24
BLUE_PIN = 23

# Button pin One button must control the system mode.
BUTTON_PIN = 17
#set the rgb pins as output
GPIO.setup(RED_PIN, GPIO.OUT)
GPIO.setup(GREEN_PIN, GPIO.OUT)
GPIO.setup(BLUE_PIN, GPIO.OUT)

# Choose pull-up or pull-down depending on your wiring One button must control the system mode.
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# PWM objects use PWM to control the brightness of the LED segments
pwm_red = GPIO.PWM(RED_PIN, 1000)
pwm_green = GPIO.PWM(GREEN_PIN, 1000)
pwm_blue = GPIO.PWM(BLUE_PIN, 1000)
#Use them to control the RGB LED segments
pwm_red.start(0)
pwm_green.start(0)
pwm_blue.start(0)

# ----------------------------
# ADC command dictionary
# ----------------------------
commands_per_channel = {
    2: 0b1001,   # A2
    3: 0b1101,   # A3
    4: 0b1011    # A4
}

# ----------------------------
# Global state
# ----------------------------
system_on = True #Turn the system on and off

# ----------------------------
# Helper: read ADC channel
# ----------------------------
def read_adc(channel):
    command = (commands_per_channel[channel] << 4) | 0x84#<< 4 = put it in the right position
    #| 0x84 = add required settings
    #write_byte(...) = send it to the ADC
    i2c.write_byte(ADC_ADDRESS, command)#write_byte(...) = send it to the ADC
    data = i2c.read_byte(ADC_ADDRESS)#read_byte(...) = read it from the ADC
    return data#return the data

# ----------------------------
# Helper: convert ADC to PWM
# ----------------------------
def adc_to_duty(adc_value):
    duty = adc_value * 100 / 255#convert the ADC value to PWM duty cycle
    return duty#return the duty cycle

# ----------------------------
# Button callback
# ----------------------------
def toggle_system(channel):
    global system_on
    system_on = not system_on #toggle the system on and off
    print("System on:", system_on)

# Add event detection
GPIO.add_event_detect(
    BUTTON_PIN,
    GPIO.FALLING,   # or GPIO.RISING depending on wiring
    callback=toggle_system,#Do not poll the button manually all the time. Use an event.
    bouncetime=200
)

# ----------------------------
# Main loop #
# ----------------------------
try:
    while True:
        # Read the values of the 3 potentiometers
        red_adc = read_adc(2)
        green_adc = read_adc(3)
        blue_adc = read_adc(4)

        # Use them to control the RGB LED segments
        red_duty = adc_to_duty(red_adc)
        green_duty = adc_to_duty(green_adc)
        blue_duty = adc_to_duty(blue_adc)

        if system_on:
            # Normal mode: potentiometers control RGB
            pwm_red.ChangeDutyCycle(red_duty)
            pwm_green.ChangeDutyCycle(green_duty)
            pwm_blue.ChangeDutyCycle(blue_duty)
        else:
            # "Off" mode: LED never fully off When the system is “off”, the RGB LED must still stay a little bit on.
            MIN_DUTY = 5
            pwm_red.ChangeDutyCycle(MIN_DUTY)
            pwm_green.ChangeDutyCycle(MIN_DUTY)
            pwm_blue.ChangeDutyCycle(MIN_DUTY)

        print(f"R={red_adc} G={green_adc} B={blue_adc}")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    pwm_red.stop()
    pwm_green.stop()
    pwm_blue.stop()
    GPIO.cleanup()
    i2c.close()

#This script starts by setting up the GPIO pins and the I2C bus. Then it defines a function to read the ADC channels and another function to convert the ADC values to PWM duty cycles. The button callback toggles the system on and off. The main loop reads the ADC values, converts them to duty cycles, and then updates the PWM duty cycles based on the system state. Finally, the script cleans up the GPIO pins and the I2C bus.