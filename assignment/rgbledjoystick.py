import smbus#for i2c communication
import time
import RPi.GPIO as GPIO#for gpio pins


#ADC settings&joystick channels
ADC_ADDR = 0x48#address of the adc
X_CHANNEL = 5#channel for x axis
Y_CHANNEL = 6#channel for y axis



#RGB LED PINS
RED_PIN = 5#pin for red led
GREEN_PIN = 6#pin for green led
BLUE_PIN = 13#pin for blue led

#setup GPIO and PWM
GPIO.setmode(GPIO.BCM)#set the mode to bcm
GPIO.setwarnings(False)#disable warnings

GPIO.setup(RED_PIN, GPIO.OUT)#set the red led pin as output
GPIO.setup(GREEN_PIN, GPIO.OUT)#set the green led pin as output
GPIO.setup(BLUE_PIN, GPIO.OUT)#set the blue led pin as output

red_pwm = GPIO.PWM(RED_PIN, 1000)#set the red led pwm
green_pwm = GPIO.PWM(GREEN_PIN, 1000)#set the green led pwm
blue_pwm = GPIO.PWM(BLUE_PIN, 1000)#set the blue led pwm

red_pwm.start(0)#start the red led pwm
green_pwm.start(0)#start the green led pwm
blue_pwm.start(0)#start the blue led pwm


bus = smbus.SMBus(1)#initialize the i2c bus

def ads7830_command(channel):#create the command for the adc
    return 0x84 | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)#

def read_adc(channel):#read the adc
    bus.write_byte(ADC_ADDR, ads7830_command(channel))
    time.sleep(0.005)#wait a tiny bit
    data = bus.read_byte(ADC_ADDR)#read the data from the adc
    return data

def convert_to_percentage(value):#convert the value to percentage
    return (value / 255) * 100

def set_rgb(red, green, blue):
    red_pwm.ChangeDutyCycle(100 - red)  #set the red led duty cycle
    green_pwm.ChangeDutyCycle(100 - green)#set the green led duty cycle
    blue_pwm.ChangeDutyCycle(100 - blue)#set the blue led duty cycle
try:
    while True:
        x_value = read_adc(X_CHANNEL)#read the x axis value
        y_value = read_adc(Y_CHANNEL)#read the y axis value

        red = convert_to_percentage(x_value)#convert the x axis value to percentage
        green = convert_to_percentage(y_value)#convert the y axis value to percentage
        blue = (red + green) / 2#calculate the blue led duty cycle
        set_rgb(red, green, blue)#set the led color

        print(f"X={x_value} -> R={red:.1f}%")#print the x axis value and the red led duty cycle
        print(f"Y={y_value} -> G={green:.1f}%")#print the y axis value and the green led duty cycle
        print(f"AVG -> B={blue:.1f}%")#print the blue led duty cycle

        time.sleep(0.1)#wait a tiny bit

except KeyboardInterrupt:
    print("Exiting...")#print the exit message
    red_pwm.stop()#stop the red led pwm
    green_pwm.stop()#stop the green led pwm
    blue_pwm.stop()#stop the blue led pwm
    GPIO.cleanup()#cleanup the gpio pins

    time.sleep(0.1)
    