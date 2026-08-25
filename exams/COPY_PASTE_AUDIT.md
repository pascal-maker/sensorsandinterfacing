# Exam Copy-Paste Readiness Audit

Use this page as the index during revision. Prefer the small maintained classes
in `exams/copy_paste_kit/`; use weekly classes when the kit intentionally does
not duplicate a larger device driver.

## Coverage by week

| Week | Main topic | Reusable source | Readiness |
|---|---|---|---|
| 1 | GPIO LEDs and buttons | `weeks/week01/gpio_basics.py` (`LED`, `Button`) | Ready |
| 2 | Edges, timing, CSV and plots | `button_toggle.py`, `csv_logger.py`; Week 2 plotting examples | Ready |
| 3 | Four-bit BCD | `bcd_input.py` | Ready |
| 4 | ADS7830, PWM, RGB, joystick | `adc_reader.py`, `joystick.py`; `weeks/week04/pwm_adc.py` | Ready |
| 5 | LCD and servo | `servo_motor.py`; `weeks/week05/ledexercise.py` (`LCD`) | Ready |
| 6 | Byte combining and movement | `shift_register.py`; Week 6 exercises | Ready |
| 7 | DC motor, stepper and servo | `weeks/week07/example/motors.py`; `servo_motor.py` | Ready |
| 8 | Buzzer, shift register and LED bar | `active_buzzer.py`, `shift_register.py`, `led_bar_graph.py` | Ready |
| 9 | Keypad, matrix and seven-segment | `keypad_4x4.py`, `led_matrix_8x8.py`, `seven_segment_display.py` | Ready |
| 11 | Camera, RFID and threaded display | Week 11 assignments/classes | Reference ready; hardware-specific |

## Fast selection guide

| Requirement in an exam | Copy first |
|---|---|
| Read a potentiometer | `ADCReader` + `Potentiometer` |
| Read joystick direction | `ADCReader` + `Joystick` |
| Read a BCD switch | `BCDInput` |
| Toggle state with a button | `ButtonToggle` |
| Scan a keypad | `Keypad4x4` |
| Save timestamped measurements | `CSVLogger` |
| Drive a 74HC595 | `ShiftRegister` |
| Display a number | `SevenSegmentDisplay` |
| Show a level | `LedBarGraph` |
| Draw a cursor/graph | `LedMatrix8x8` |
| Move a servo | `ServoMotor` |
| Sound an alarm | `ActiveBuzzer` |

## Important limitations

- Do not run the seven-segment display and LED matrix from the same shift-register
  chain at the same time unless the exam wiring explicitly supports it.
- GPIO 16, 20, 21 and 26 are reused by the BCD input and keypad rows.
- GPIO 7 may conflict with SPI CE1 on Raspberry Pi 5.
- Initialise `GPIO.setmode(GPIO.BCM)` before constructing kit objects.
- Stop display threads, close CSV/I2C resources, and then call `GPIO.cleanup()`.
- Camera, RFID and Bluetooth examples need their external packages and hardware;
  keep their Week 7/11 implementations as references rather than blind copies.

## Audit conclusion

The repository has enough reusable class coverage for the taught GPIO, ADC,
input, actuator, logging and display combinations. The remaining exam skill is
composition: selecting compatible pins, coordinating timing, and guaranteeing
cleanup. Practice Exams 5 and 6 target those integration skills.
