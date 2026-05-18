# CS:GO Bomb Simulator (`exam-retake.py`)

## Overview
This script implements a "CS:GO Bomb" simulator using a Raspberry Pi. It uses various hardware components to mimic the planting, defusing, and exploding mechanics of the bomb from the popular game Counter-Strike: Global Offensive. It features a ticking countdown timer, a 7-button defuse sequence, and an anti-tamper mechanism that triggers an immediate explosion if the device is moved.

## Hardware Components
- **Raspberry Pi**: The main controller running the Python script.
- **I2C LCD Display (16x2)**: Used to display the game state, instructions, countdown timer, and defuse progress.
- **MPU6050 Accelerometer & Gyroscope**: Acts as an anti-tamper sensor. It establishes a baseline position when the bomb is planted. Any significant movement afterwards will trigger an explosion.
- **4 Push Buttons**: 
  - Button 1 (`PLANT_BUTTON_PIN` - GPIO 20): Used to plant the bomb, reset the system, and as part of the defuse code.
  - Buttons 2, 3, 4 (GPIO 21, 16, 26): Used for entering the defuse code.
- **RGB LED**: Provides visual status indicators (Blue = Idle, Red = Armed/Exploded, Green = Defused).
- **Buzzer**: Provides audio feedback for button presses, the ticking countdown (which speeds up as time runs out), and the explosion/defuse sound effects.

## Software Architecture & Logic

### LCD Management
The script includes custom, low-level functions (`set_data_bits`, `send_instruction`, `send_character`, etc.) to interface with the 16x2 LCD over I2C without relying on a large external LCD library. It handles 4-bit mode initialization and custom character drawing (such as the visual progress bar).

### MPU6050 Class
A custom class interfaces with the MPU6050 sensor via I2C to read raw acceleration and gyroscope data, converting them to usable values to detect physical movement.

### The `CSGOBomb` Class
This is the core state machine of the game. It tracks:
- **State**: `STATE_IDLE`, `STATE_ARMED`, `STATE_DEFUSED`, or `STATE_EXPLODED`.
- **Timers**: 40-second countdown timer and dynamic beep intervals (beeps get faster as time runs out).
- **Defuse Logic**: A sequence of 7 button presses (`[20, 21, 16, 26, 20, 21, 16]`). It tracks the user's input, the number of incorrect attempts (max 3), and handles success or failure.

#### Game Flow:
1. **Idle**: The RGB LED is Blue. The LCD prompts the user to press a button to plant.
2. **Armed**: Pressing Button 1 plants the bomb. The MPU6050 records its current orientation. The LED turns Red, the timer starts, and the buzzer begins ticking. The LCD shows a visual progress bar.
3. **Defusing**: The user must input the 7-button sequence. Incorrect attempts are counted. If 3 wrong sequences are entered, the bomb explodes.
4. **Anti-Tamper**: In the `update` loop, it continuously checks the MPU6050. If the orientation changes beyond a specific threshold, it immediately triggers an explosion ("TAMPER DETECTED!").
5. **Exploded / Defused**: Depending on the outcome, the RGB LED will flash red or turn solid green, accompanied by appropriate buzzer sounds and LCD messages.

### Main Loop and Interrupts
- The script uses GPIO event detection (`GPIO.add_event_detect`) to handle button presses asynchronously. This allows the main `while True:` loop to run smoothly without blocking while waiting for input.
- Software debouncing logic is implemented in the callbacks using `time.time()` to prevent single physical button presses from registering multiple times.
- The `bomb.update()` method is called continuously in the main loop to handle the countdown, LED updates, buzzer ticking, and movement detection.
