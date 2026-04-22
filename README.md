# Sensors and Interfacing

Course lab work and assignments for a sensors & interfacing module on the Raspberry Pi.  
Each week introduces a new component, protocol, or concept through hands-on exercises, building toward a final multi-mode sensor station.

---

## Hardware Used

| Component | Details |
|-----------|---------|
| Raspberry Pi | Primary platform (BCM pin numbering) |
| MPU-6050 | 6-axis accelerometer + gyroscope — I2C @ 0x68 |
| ADS7830 | 8-channel 8-bit ADC — I2C @ 0x48 |
| I2C LCD (16×2) | Character display — I2C @ 0x27 |
| Joystick | Analog joystick (used in assignment) |
| Servo motor | Signal on GPIO 18 |
| DC motor | H-bridge on GPIO 14 & 15 |
| Stepper motor | 4-coil on GPIO 19, 13, 6, 5 |
| RGB LED | GPIO 5 (R), 6 (G), 13 (B) |
| Active buzzer | Week 8 |
| Shift register | Week 8 |
| Buttons & LEDs | Various GPIO pins throughout |

---

## Repository Structure

```
sensorsandinterfacing/
│
├── main.py              # Multi-mode sensor station (combines all weeks)
├── mpu6050.py           # Standalone MPU-6050 driver
├── temperature.py       # Temperature sensor module
├── test.py              # Quick test scripts
├── assignment2.py       # Standalone assignment 2
├── assignment3.py       # Standalone assignment 3
│
├── assignment/          # Graded assignment — multi-screen LCD app
│   ├── screen1.py       # Screen 1 of 5
│   ├── screen2.py
│   ├── screen3.py
│   ├── screen4.py
│   ├── screen5.py
│   ├── joystickofficial.py
│   └── lcdtest.py
│
├── week1/               # GPIO basics — LEDs, buttons, traffic light
├── week2/               # Button timing, debounce, pedestrian light, data logging
├── week3/               # Bit operations, ADC, BCD encoding
├── week4/               # PWM, ADS7830 ADC, I2C
├── week5/               # I2C scanning, SPI, servo motor, serial communication
├── week6/               # MPU-6050 accelerometer/gyroscope
├── week07/              # DC motor, stepper motor, servo, BLE Bluetooth
└── week08/              # Shift register, active buzzer
```

---

## Weekly Labs

| Week | Topic | Key Files |
|------|-------|-----------|
| 1 | GPIO basics — LEDs, buttons, traffic light | `gpio_basics.py`, `multibutton.py` |
| 2 | Button timing, debounce, pedestrian signals, CSV logging | `btn_timings.py`, `plotting.py`, `traflightpedestrian.py` |
| 3 | Bit operations, ADC, BCD encoding | `bit_operations.py`, `bounce.py` |
| 4 | PWM, ADS7830 ADC over I2C | `pwm_adc.py`, `exercisevolt.py` |
| 5 | I2C scanning, SPI, servo motor, serial comms | `scani2c_exercise.py`, `servomotor.py`, `communication.py` |
| 6 | MPU-6050 — 6-axis IMU readings | `mpu6050.py`, `assignment1.py` |
| 7 | DC motor, stepper motor, servo, BLE Bluetooth | `motors.py`, `steppermotor.py`, `ble_rpi/` |
| 8 | Shift register (74HC595), active buzzer | `shiftregisterexercise.py`, `active_buzzer.py` |

---

## Main Application — `main.py`

A multi-mode sensor station that ties all weeks together. Cycle through modes using the **MODE button (GPIO 20)**.

| Mode | LED Color | Behaviour |
|------|-----------|-----------|
| **0 — IMU** | Blue | MPU-6050 accel-X maps to servo angle; prints accel/gyro/temp every 0.5 s |
| **1 — Motor** | Green | ADS7830 potentiometer (ch2) controls DC motor speed; ACTION button (GPIO 26) cycles Stop → Forward → Reverse |
| **2 — BCD** | Red | 4 buttons read as a 4-bit BCD value; ACTION button blinks the LED that many times |

### Wiring summary

```
GPIO 20  → MODE button
GPIO 26  → ACTION button
GPIO 16, 21, 19, 13 → BCD buttons (b0–b3)
GPIO  5,  6, 13 → RGB LED (R, G, B)
GPIO 17  → single LED
GPIO 18  → servo signal
GPIO 14, 15 → DC motor (H-bridge)
I2C     → MPU-6050 @ 0x68
I2C     → ADS7830  @ 0x48
```

### Run

```bash
python main.py
```

---

## Assignment — Multi-Screen LCD App

A 5-screen interactive application displayed on a 16×2 I2C LCD, navigated with an analog joystick.

```bash
cd assignment
python screen1.py   # start from screen 1
```

---

## Setup

```bash
# Enable I2C on the Pi
sudo raspi-config
# → Interface Options → I2C → Enable

# Install dependencies
pip install smbus2 RPi.GPIO
```

---

## Author

**pascal-maker** — Raspberry Pi · Python · Embedded Systems
