Here is a **tiny glossary** with the main terms from your course, in short student style.

# Tiny glossary

## DC motor

A simple motor that just spins.
You control:

* speed
* direction

It does **not** know its position.

---

## Servo motor

A motor that moves to a **specific angle**.
Example:

* 0°
* 90°
* 180°

Good for precise position.

---

## Stepper motor

A motor that moves in **small steps**.
Good for rotating by exact amounts.

Example:

* turn 90°
* turn 180°

---

## GPIO

The Raspberry Pi pins you control in Python.

* input = button/sensor
* output = LED/motor/buzzer

---

## PWM

Pulse Width Modulation.
Fast ON/OFF signal used to control:

* DC motor speed
* servo position

---

## Duty cycle

The PWM percentage.

* 0% = always off
* 50% = half on
* 100% = always on

---

## ADC

Analog to Digital Converter.
Used because Raspberry Pi cannot read analog values directly.

Used for:

* potentiometer
* joystick

---

## Potentiometer

A knob that gives an analog value when you turn it.
Used for speed control.

---

## Joystick

Like 2 potentiometers together:

* X-axis
* Y-axis

Used to control position.

---

## H-bridge

Circuit that lets a DC motor turn:

* left
* right

Because it can reverse polarity.

---

## L293D

Motor driver chip for the DC motor.
It is the H-bridge driver you use.

---

## ULN2003

Driver for the stepper motor.
It lets weak GPIO signals control the stepper coils.

---

## I²C

A communication bus used to talk to devices with just a few wires.

Used for:

* ADC
* MPU6050
* LCD

---

## SMBus

A stricter version of I²C.
Python uses this to communicate with I²C devices on the Pi.

---

## IMU

Inertial Measurement Unit.
A sensor that measures movement/orientation.

---

## MPU6050

A 6-DOF IMU with:

* accelerometer
* gyroscope
* temperature sensor

---

## Accelerometer

Measures acceleration in:

* X
* Y
* Z

Also measures gravity.

---

## Gyroscope

Measures rotation speed in:

* X
* Y
* Z

Unit = degrees per second

---

## Temperature sensor

Inside the MPU6050.
Gives temperature in °C after conversion.

---

## Big-endian

High byte comes first, low byte second.

Used when combining sensor bytes.

---

## Two’s complement

System used to store negative numbers in binary.

Needed for MPU6050 readings.

---

## BLE

Bluetooth Low Energy.
Used to connect Pi to phone/laptop wirelessly.

---

## GATT

Bluetooth structure for communication.

Uses:

* services
* characteristics

---

## UART service

A BLE service that acts like a text/serial connection.

Used to send messages like:

```text
DC-left
Step 90
```

---

## Service

A group/container in GATT.

---

## Characteristic

A specific data channel inside a service.

---

## RX

Receive.
Data coming **into** the Pi.

---

## TX

Transmit.
Data going **out from** the Pi.

---

## Queue

A waiting line for messages.

Used in BLE:

* `rx_q`
* `tx_q`

---

## Thread

A second flow of code running in parallel.

Used so BLE can run in the background.

---

## Interrupt / event

A way for the Pi to react when a button changes state, without constantly checking it in a loop.

Example:

```python
GPIO.add_event_detect(...)
```

---

## Main loop

The loop that keeps your program running:

```python
while True:
```

---

## Sweep

Move servo from one side to the other.

Example:

* `Sweep-left`
* `Sweep-right`

---

## Step

Can mean:

* one little stepper motor step
* or a command like `Step 90`

---

## Angle

Position in degrees.

Example:

* 0°
* 90°
* 180°

---

## Frequency

How many times something repeats per second.

Example:

* servo PWM = 50 Hz
* DC motor PWM = 1000 Hz

---

# Ultra short memory list

* **DC motor** = spin
* **servo** = angle
* **stepper** = exact steps
* **PWM** = control signal
* **ADC** = read analog
* **BLE** = wireless phone control
* **MPU6050** = movement sensor
* **GPIO** = Raspberry Pi pins

