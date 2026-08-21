# Joystick Exam Simulation

## Possible exam question

Read the joystick X and Y values from the ADC. Detect the direction as LEFT,
RIGHT, UP, DOWN, or CENTER. Save each reading to a CSV file with a timestamp.
Use the joystick button to toggle CSV logging on and off.

## Files copied

- `main.py`
- `adc_reader.py`
- `joystick.py`
- `button_toggle.py`
- `csv_logger.py`

## Run

```bash
cd "/home/kaanc/Desktop/sensors interfacing/exam_copy_paste_kit/exam_simulation_joystick"
python3 main.py
```

The CSV should appear in this same folder as:

```text
joystick_log.csv
```

## Pins/channels to check

- Joystick X channel: `6`
- Joystick Y channel: `5`
- Joystick button pin: GPIO `7`

If GPIO `7` does not work on Raspberry Pi 5, change `pin=7` in `main.py` to
`pin=20` and use the separate button.
