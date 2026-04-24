import smbus
import time
import RPi.GPIO as GPIO

# ADC settings
ADC_ADDR = 0x48#adc address
X_CHANNEL = 5#joystick x channel
Y_CHANNEL = 6#joystick y channel

# RGB LED pins
RED_PIN = 5#red led pin
GREEN_PIN = 6#green led pin
BLUE_PIN = 13#blue led pin

bus = smbus.SMBus(1)#initialize the i2c bus


def setup():#setup the gpio pins and pwm
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

    return red_pwm, green_pwm, blue_pwm


def ads7830_command(channel):#create the command for the adc
    return 0x84 | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)#create the command for the adc


def read_adc(channel):#read the adc value
    bus.write_byte(ADC_ADDR, ads7830_command(channel))#send the command to the adc
    time.sleep(0.005)#wait a tiny bit
    return bus.read_byte(ADC_ADDR)#read the value from the adc


def convert_to_percentage(value):#convert the value to percentage
    return (value / 255) * 100


def set_rgb(red_pwm, green_pwm, blue_pwm, red, green, blue):#set the rgb led values
    red_pwm.ChangeDutyCycle(100 - red)#set the red led duty cycle
    green_pwm.ChangeDutyCycle(100 - green)#set the green led duty cycle
    blue_pwm.ChangeDutyCycle(100 - blue)#set the blue led duty cycle


def main():#run the main function
    red_pwm, green_pwm, blue_pwm = setup()#setup the pwm

    try:
        while True:
            x_value = read_adc(X_CHANNEL)#read the x-axis value
            y_value = read_adc(Y_CHANNEL)#read the y-axis value

            red = convert_to_percentage(x_value)#convert the x-axis value to percentage
            green = convert_to_percentage(y_value)#convert the y-axis value to percentage
            blue = (red + green) / 2#calculate the blue led value

            set_rgb(red_pwm, green_pwm, blue_pwm, red, green, blue)

            print(f"X={x_value} -> R={red:.1f}%")#print the x-axis value and red led value
            print(f"Y={y_value} -> G={green:.1f}%")#print the y-axis value and green led value
            print(f"AVG -> B={blue:.1f}%")#print the blue led value
            print()

            time.sleep(0.1)

    except KeyboardInterrupt:#if the user presses ctrl+c
        print("Exiting...")

    finally:#stop the pwm and cleanup the gpio pins
        red_pwm.stop()#stop the red led pwm
        green_pwm.stop()#stop the green led pwm
        blue_pwm.stop()#stop the blue led pwm
        GPIO.cleanup()#cleanup the gpio pins


if __name__ == "__main__":#this is the main part of the code that will run when the script is executed
    main()