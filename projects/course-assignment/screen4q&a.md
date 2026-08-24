### Assignment-specific explanation

Screen 4 is the same logic as Screen 3, but it reads the **Y-axis** of the joystick instead of the X-axis.

Important parts:

```python
Y_CHANNEL = 4
```

This means the joystick Y-axis is connected to ADC channel 4.

```python
y_val = read_adc(Y_CHANNEL)
```

This reads the analog Y-axis value through the ADC. The Raspberry Pi cannot read analog values directly, so the ADS7830 converts it to a digital value between `0` and `255`.

```python
line1 = make_bar(y_val)
line2 = f"VRY=> {y_val}"
```

The first line shows a bar graph.
The second line shows the raw Y value with label `VRY`.

```python
def make_bar(value):
    blocks = int((value / 255) * 16)
    return "#" * blocks + "-" * (16 - blocks)
```

This maps the ADC value from `0–255` to `0–16` LCD characters.

### Oral explanation

> “This script reads the Y-axis of the joystick using the ADS7830 ADC. The Y-axis is connected to channel 4. The ADC returns a value between 0 and 255. I convert that value into a 16-character bar graph on the first LCD line, and I show the raw value as `VRY` on the second line. It updates every 0.1 seconds.”

## 5 oral questions + answers

### 1. What is the difference between Screen 3 and Screen 4?

Screen 3 reads the X-axis and prints `VRX`. Screen 4 reads the Y-axis and prints `VRY`.

### 2. Why do you use `Y_CHANNEL = 4`?

Because the joystick Y-axis is connected to analog input channel 4 of the ADS7830 ADC.

### 3. What does the ADC return?

It returns an 8-bit digital value between `0` and `255`, representing the analog joystick voltage.

### 4. What does `make_bar(y_val)` do?

It converts the Y value into a simple LCD bar graph. A low value gives a short bar, and a high value gives a longer bar.

### 5. Why does the script update every `0.1` seconds?

So the LCD reacts smoothly when the joystick moves, but it does not update too fast. Updating too fast can cause flickering or unnecessary I2C communication.
