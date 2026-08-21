# Joystick Exam Simulation

## Possible exam question

Read the joystick X and Y values from the ADC. Detect the direction as LEFT,
RIGHT, UP, DOWN, or CENTER. Save each reading to a CSV file with a timestamp.
Use the joystick button to toggle CSV logging on and off.

## Files used

- `joystick_csv_toggle.py`
- `../adc_reader.py`
- `../joystick.py`
- `../button_toggle.py`
- `../csv_logger.py`

## Run

```bash
python3 -m exams.copy_paste_kit.examples.joystick_csv_toggle
```

The CSV appears in the current working directory as:

```text
joystick_log.csv
```

## Pins/channels to check

- Joystick X channel: `6`
- Joystick Y channel: `5`
- Joystick button pin: GPIO `7`

If GPIO `7` does not work on Raspberry Pi 5, change `pin=7` in `main.py` to
`pin=20` and use the separate button.
