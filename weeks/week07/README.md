# Week 07 — Motors and BLE

Run the motor exercises from the repository root:

```bash
python weeks/week07/assignment_a_stepper_left.py
python weeks/week07/assignment_b_stepper_right.py
python weeks/week07/assignment_c_dc_motor.py
python weeks/week07/assignment_d_servo.py
python weeks/week07/assignment_abcd_combined.py
```

The scripts use BCM GPIO numbering. The shared implementations are
`hardware.StepperMotor`, `hardware.DCMotor`, `hardware.ServoMotor`, and
`hardware.ADS7830`.

## Pin and channel overview

| Function | BCM pin/channel |
|---|---:|
| Stepper-left button | GPIO 20 |
| Stepper-right button | GPIO 21 |
| DC mode button | GPIO 16 |
| Servo toggle button | GPIO 26 |
| Stepper ULN2003 inputs | GPIO 19, 13, 6, 5 |
| DC L293D inputs | GPIO 14, 15 |
| Servo signal | GPIO 18 |
| DC speed potentiometer | ADS7830 channel 0 combined; channel 3 standalone |
| Joystick X-axis | ADS7830 channel 6 |

The DC motor requires an external motor supply through the L293D driver. Never
power the motor directly from a GPIO pin. The programs print state, ADC, speed,
and servo information so their inputs can still be checked without motor power.

Stop any program with `Ctrl+C`; its `finally` block switches off PWM, releases
the stepper coils, closes I2C, and cleans up GPIO.

The complete Raspberry Pi BLE extension is:

```bash
python weeks/week07/ble_rpi/assignment.py
```
