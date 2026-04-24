Here is the cleaned working version:

```python
import smbus
import time
import RPi.GPIO as GPIO

# ADC settings
ADC_ADDR = 0x48
X_CHANNEL = 5
Y_CHANNEL = 6

# RGB LED pins
RED_PIN = 5
GREEN_PIN = 6
BLUE_PIN = 13

bus = smbus.SMBus(1)


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(RED_PIN, GPIO.OUT)
    GPIO.setup(GREEN_PIN, GPIO.OUT)
    GPIO.setup(BLUE_PIN, GPIO.OUT)

    red_pwm = GPIO.PWM(RED_PIN, 1000)
    green_pwm = GPIO.PWM(GREEN_PIN, 1000)
    blue_pwm = GPIO.PWM(BLUE_PIN, 1000)

    red_pwm.start(0)
    green_pwm.start(0)
    blue_pwm.start(0)

    return red_pwm, green_pwm, blue_pwm


def ads7830_command(channel):
    return 0x84 | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)


def read_adc(channel):
    bus.write_byte(ADC_ADDR, ads7830_command(channel))
    time.sleep(0.005)
    return bus.read_byte(ADC_ADDR)


def convert_to_percentage(value):
    return (value / 255) * 100


def set_rgb(red_pwm, green_pwm, blue_pwm, red, green, blue):
    red_pwm.ChangeDutyCycle(100 - red)
    green_pwm.ChangeDutyCycle(100 - green)
    blue_pwm.ChangeDutyCycle(100 - blue)


def main():
    red_pwm, green_pwm, blue_pwm = setup()

    try:
        while True:
            x_value = read_adc(X_CHANNEL)
            y_value = read_adc(Y_CHANNEL)

            red = convert_to_percentage(x_value)
            green = convert_to_percentage(y_value)
            blue = (red + green) / 2

            set_rgb(red_pwm, green_pwm, blue_pwm, red, green, blue)

            print(f"X={x_value} -> R={red:.1f}%")
            print(f"Y={y_value} -> G={green:.1f}%")
            print(f"AVG -> B={blue:.1f}%")
            print()

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        red_pwm.stop()
        green_pwm.stop()
        blue_pwm.stop()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
```

## Assignment-specific explanation

This script reads the joystick X and Y values using the ADC, then uses those values to control an RGB LED with PWM.

Important parts:

```python
X_CHANNEL = 5
Y_CHANNEL = 6
```

These are the ADC channels for the joystick X-axis and Y-axis.

```python
x_value = read_adc(X_CHANNEL)
y_value = read_adc(Y_CHANNEL)
```

The Raspberry Pi cannot read analog values directly, so the ADC converts the joystick voltage to a value between `0` and `255`.

```python
red = convert_to_percentage(x_value)
green = convert_to_percentage(y_value)
blue = (red + green) / 2
```

The X-axis controls red.
The Y-axis controls green.
Blue is calculated as the average of red and green.

```python
red_pwm.ChangeDutyCycle(100 - red)
```

PWM controls brightness by changing the duty cycle.
`100 - red` is used because your RGB LED is likely active-low/common-anode: lower duty can mean brighter, so the value is inverted.

## Oral explanation

> “This script reads the joystick X and Y positions through the ADC. The ADC returns values from 0 to 255. I convert those values to percentages from 0 to 100. The X-axis controls the red LED brightness, the Y-axis controls the green LED brightness, and the blue brightness is the average of red and green. Then I use PWM duty cycle to control the RGB LED brightness.”

## 5 oral questions + answers

### 1. Why do you need the ADC?

Because the joystick outputs analog voltages, but the Raspberry Pi GPIO pins only read digital HIGH or LOW. The ADC converts the analog voltage into a digital value from `0` to `255`.

### 2. Why do you convert the ADC value to a percentage?

Because PWM duty cycle expects a value from `0` to `100`. The ADC gives `0` to `255`, so I map it to `0–100%`.

### 3. What does PWM do here?

PWM changes the brightness of each LED color by quickly switching the pin on and off. A higher duty cycle means the LED is on for a larger part of the time.

### 4. Why is blue calculated as an average?

Blue is not directly controlled by one joystick axis. It is calculated from both red and green:

```python
blue = (red + green) / 2
```

So blue changes based on the combined joystick position.

### 5. Why do you use `100 - red` in `ChangeDutyCycle()`?

Because the RGB LED is probably active-low/common-anode. That means the brightness logic is inverted: a lower duty cycle can make the LED brighter, so I subtract from `100`.
