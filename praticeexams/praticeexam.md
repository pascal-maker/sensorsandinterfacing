# VIP.py Script Explanation

`vip.py` is a Raspberry Pi bomb-defusal simulator. It uses buttons, an I2C LCD, an RGB LED, a buzzer, and an MPU6050 motion sensor to create an interactive game.

## Hardware Used

| Component | Purpose |
|---|---|
| Raspberry Pi GPIO | Controls buttons, RGB LED, and buzzer |
| 16x2 I2C LCD | Displays game status and countdown |
| MPU6050 | Detects movement using accelerometer and gyroscope data |
| RGB LED | Shows bomb state using colors |
| Buzzer | Gives audio feedback and countdown beeps |
| 4 Push buttons | Plant, reset, and enter the defuse code |

## Pin Setup

| GPIO Pin | Component |
|---|---|
| GPIO 20 | Button 1: plant/reset/code input |
| GPIO 21 | Button 2: code input |
| GPIO 16 | Button 3: code input |
| GPIO 26 | Button 4: code input |
| GPIO 5 | RGB LED red |
| GPIO 6 | RGB LED green |
| GPIO 13 | RGB LED blue |
| GPIO 12 | Buzzer |

The LCD uses I2C address `0x27`.

The MPU6050 uses I2C address `0x68`.

## Main Idea

The script creates a game where the user can plant a bomb, then try to defuse it before the timer reaches zero. The bomb can also explode if it is moved after being planted.

The program has four states:

```python
STATE_IDLE = 0
STATE_ARMED = 1
STATE_DEFUSED = 2
STATE_EXPLODED = 3
```

## State 1: Idle

When the program starts, the bomb is idle.

The LCD shows:

```text
CS:GO BOMB SIM
Press to PLANT!
```

The RGB LED is blue.

Pressing button 1 plants the bomb.

## State 2: Armed

When the bomb is planted:

- the state changes to `STATE_ARMED`
- a 40 second countdown starts
- the current MPU6050 position is stored as the baseline
- the RGB LED turns red
- the buzzer starts beeping
- the LCD shows a countdown progress bar

The defuse code is:

```python
[20, 21, 16, 26, 20, 21, 16]
```

This means the user must press:

```text
BTN1, BTN2, BTN3, BTN4, BTN1, BTN2, BTN3
```

The buzzer changes speed depending on the time left:

| Time Left | Buzzer Speed |
|---|---|
| More than 20 seconds | Slow |
| Less than 20 seconds | Faster |
| Less than 10 seconds | Very fast |

## State 3: Defused

If the correct code is entered, the bomb is defused.

The RGB LED turns green.

The LCD shows:

```text
BOMB DEFUSED!!
```

The buzzer plays a short success sound.

## State 4: Exploded

The bomb explodes if:

- the timer reaches zero
- the wrong code is entered 3 times
- the MPU6050 detects movement after the bomb is planted

When the bomb explodes:

- the RGB LED flashes red
- the buzzer makes a fast explosion sound
- the LCD shows:

```text
BOMB EXPLODED!
TERRORISTS WIN!
```

## MPU6050 Movement Detection

When the bomb is planted, the script stores the current accelerometer and gyroscope values:

```python
self.baseline_accel = mpu.read_acceleration()
self.baseline_gyro = mpu.read_gyroscope()
```

During the armed state, the script keeps reading the MPU6050.

It compares the current values with the baseline values.

If the difference is larger than the threshold, movement is detected and the bomb explodes.

```python
self.movement_threshold_accel = 0.3
self.movement_threshold_gyro = 50
```

## Button Interrupts

The script uses GPIO interrupts to detect button presses:

```python
GPIO.add_event_detect(PLANT_BUTTON_PIN, GPIO.FALLING, callback=plant_button_callback, bouncetime=300)
```

The buttons use pull-up resistors, so they are normally `HIGH`. When pressed, they become `LOW`. That is why the script uses `GPIO.FALLING`.

The `bouncetime=300` helps prevent one physical press from being counted multiple times.

## Main Loop

The main loop keeps the game running:

```python
while True:
    bomb.update()
    time.sleep(0.01)
```

The `update()` method checks the current state and updates the LCD, RGB LED, buzzer, timer, movement detection, and game result.

## Cleanup

When the user stops the program with `CTRL+C`, the script:

- clears the LCD
- turns off the RGB LED
- turns off the buzzer
- stops PWM
- closes I2C
- cleans up GPIO

This prevents GPIO pins from staying active after the program exits.

# Recreated Original Assignment

## Title

Raspberry Pi Bomb Defusal Simulator With Motion Detection

## Assignment Description

Create an interactive Raspberry Pi bomb-defusal simulator using GPIO buttons, an I2C LCD, an RGB LED, a buzzer, and an MPU6050 accelerometer/gyroscope.

The system should simulate a planted bomb with a countdown timer. The user must enter the correct button sequence before the timer reaches zero. The bomb should also detect movement using the MPU6050 sensor. If the bomb is moved after being planted, it should explode immediately.

## Requirements

1. Use a Raspberry Pi as the main controller.
2. Use a 16x2 I2C LCD to display the game state.
3. Use four push buttons for planting, resetting, and entering the defuse code.
4. Use an RGB LED to show the current bomb state.
5. Use a buzzer for sound feedback.
6. Use an MPU6050 sensor to detect movement.
7. The bomb must start in an idle state.
8. Pressing button 1 must plant the bomb.
9. When planted, the bomb must start a 40 second countdown.
10. The LCD must show a countdown or progress bar while the bomb is armed.
11. The buzzer must beep while the bomb is armed.
12. The buzzer must beep faster as the timer gets closer to zero.
13. The RGB LED must be blue when idle.
14. The RGB LED must be red when armed.
15. The RGB LED must be green when defused.
16. The RGB LED must flash red when exploded.
17. The user must enter a 7-button defuse sequence.
18. If the correct code is entered, the bomb must be defused.
19. If the wrong code is entered 3 times, the bomb must explode.
20. If the countdown reaches zero, the bomb must explode.
21. When the bomb is planted, the current MPU6050 position must be saved.
22. If the MPU6050 detects movement above a threshold, the bomb must explode.
23. After the bomb is defused or exploded, the system must allow a reset.
24. The program must clean up GPIO and I2C safely when it exits.

## Expected Behaviour

When the program starts, the LCD should show that the bomb simulator is ready.

The user presses the plant button to arm the bomb.

The LCD shows the countdown. The buzzer starts beeping. The RGB LED turns red.

The user must enter the correct defuse code before time runs out.

If the code is correct, the LCD shows that the bomb is defused and the RGB LED turns green.

If the user enters the wrong code 3 times, moves the bomb, or lets the timer reach zero, the bomb explodes.

## Learning Goals

This assignment tests the ability to:

- use GPIO inputs and outputs
- use pull-up buttons
- use GPIO interrupts
- control an RGB LED with PWM
- control a buzzer
- communicate with I2C devices
- write to a 16x2 LCD
- read accelerometer and gyroscope data
- use classes to organize program logic
- create a state machine
- safely clean up hardware resources
