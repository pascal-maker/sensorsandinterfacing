Here’s what all those terms mean, in simple words.

# 1. Motor

A **motor** is a component that turns electrical energy into movement.

In your kit, you have 3 main types:

* **DC motor**
* **servo motor**
* **stepper motor**

They all move, but in different ways.

---

# 2. DC motor

A **DC motor** is the simplest motor.

It just spins when you give it power.

## What you can control

* direction
* speed

## Good for

* wheels
* fans
* spinning things

## Not good for

* exact angle control

Because a DC motor does not know:

* where it is
* how far it turned

It just spins.

---

# 3. Servo motor

A **servo motor** is a motor that can move to a specific angle.

Example:

* 0°
* 90°
* 180°

So instead of “just spin,” a servo is more like:

> “go to this position”

## Good for

* robot arms
* flaps
* steering
* things that need angle control

## Important

A servo usually has:

* power
* ground
* signal wire

And you control it with **PWM**.

---

# 4. Stepper motor

A **stepper motor** moves in many tiny steps.

Instead of spinning freely like a DC motor, it moves like:

* step
* step
* step
* step

So it is good for precise movement.

## Good for

* exact rotation
* positioning
* turning by specific amount

Example:

* turn 90°
* turn 180°
* turn half a turn

---

# 5. PWM

**PWM** = Pulse Width Modulation

This is a way to control power using very fast ON/OFF signals.

## For DC motor

PWM controls:

* speed

## For servo

PWM controls:

* angle / position

So PWM is very important in your exercises.

---

# 6. GPIO

**GPIO** = General Purpose Input/Output

These are the Raspberry Pi pins you use in code.

## Input

Used for things like:

* buttons
* sensors

## Output

Used for things like:

* LEDs
* motors
* buzzers

Example:

```python
GPIO.setup(20, GPIO.IN)
GPIO.setup(18, GPIO.OUT)
```

---

# 7. ADC

**ADC** = Analog to Digital Converter

The Raspberry Pi cannot directly read analog values.

So you need an ADC chip.

It converts things like:

* potentiometer position
* joystick movement

into digital numbers like:

* `0`
* `120`
* `255`

---

# 8. Potentiometer

A **potentiometer** is a knob you can turn.

It gives an analog value.

You used it for:

* speed control

Example:

* turn knob left → low value
* turn knob right → high value

---

# 9. Joystick

A **joystick** is like 2 potentiometers in one.

It has:

* X-axis
* Y-axis

So it gives analog values for left/right and up/down.

You used the X-axis to control the servo angle.

---

# 10. BLE

**BLE** = Bluetooth Low Energy

This is a lightweight Bluetooth system.

You use it to make your Raspberry Pi talk to:

* phone
* laptop
* other BLE devices

---

# 11. GATT

**GATT** = Generic Attribute Profile

This is the system BLE uses for communication.

It organizes data into:

* services
* characteristics

You do not need to remember every detail, but for your exercises it means:

> it is the BLE communication structure

---

# 12. UART

**UART** normally means serial communication.

In your Bluetooth exercise, “UART service” means:

> BLE is used like a text serial channel

So your phone sends text like:

```text
DC-left
```

and the Pi reads it.

---

# 13. Queue

A **queue** is like a waiting line for messages.

In your BLE code you have:

* `rx_q`
* `tx_q`

## RX queue

messages coming **into** the Pi

## TX queue

messages the Pi sends **out**

---

# 14. Interrupt / Event

This means the Pi does not need to constantly ask:

> “is the button pressed now?”

Instead, it gets notified automatically when something changes.

Example:

```python
GPIO.add_event_detect(...)
```

This is cleaner for button handling.

---

# 15. Duty cycle

This is the PWM percentage.

Example:

* `0%` = always OFF
* `50%` = half on, half off
* `100%` = always ON

## For DC motor

bigger duty cycle = faster

## For servo

duty cycle maps to angle

---

# 16. H-bridge

An **H-bridge** is the motor driver circuit that lets a DC motor spin both directions.

Because to change direction, you reverse polarity.

The H-bridge does that electronically.

---

# 17. ULN2003

This is a driver used for the **stepper motor**.

It takes weak Raspberry Pi signals and drives the stepper motor coils.

Without it, the Pi cannot drive the stepper directly.

---

# 18. L293D

This is the driver used for the **DC motor**.

It is a dual H-bridge chip.

You used it with:

* GPIO14
* GPIO15

---

# 19. `sweep`

In your servo exercise, **sweep** means:

> move from one side to the other side

So:

* `Sweep-left` = move servo to left
* `Sweep-right` = move servo to right

---

# 20. `step`

In the stepper exercise, **step** means:

> a small motor movement

And in the BLE command:

```text
Step 90
```

it means:

> rotate the stepper by 90 degrees

---

# 21. Angle

Angle is the position of something in degrees.

Examples:

* `0°`
* `90°`
* `180°`

You use angle mostly with:

* servo motor
* stepper motor commands

---

# 22. Frequency

Frequency means how often something repeats per second.

For PWM:

* servo often uses **50 Hz**
* DC motor may use **1000 Hz**

---

# 23. Thread

A **thread** is like another flow of execution running next to your main code.

In your BLE exercise:

* one thread runs the BLE loop
* main code runs separately

This helps keep Bluetooth alive without blocking the rest of your code.

---

# 24. Main loop

The **main loop** is the part of your program that keeps running again and again.

Example:

```python
while True:
    ...
```

That is where you keep checking sensor values or updating motors.

---

# Super short version

## DC motor

spins continuously, speed + direction

## Servo

moves to a chosen angle

## Stepper

moves in many tiny steps, good for exact rotation

## PWM

fast ON/OFF control signal

## GPIO

Raspberry Pi pins

## ADC

converts analog to digital

## BLE

Bluetooth Low Energy

## GATT/UART

how BLE text messages are sent

## Queue

message line between BLE and your code


