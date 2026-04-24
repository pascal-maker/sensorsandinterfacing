### Assignment-specific explanation

This script reads the **X-axis of the joystick** through the **ADS7830 ADC** and shows it on the LCD as:

1. a bar graph on line 1
2. the raw ADC value on line 2

The LCD helper code is mostly boilerplate. The important parts are here:

```python
ADC_ADDR = 0x48
X_CHANNEL = 5
```

`ADC_ADDR` is the I2C address of the ADC.
`X_CHANNEL = 5` means the joystick X-axis is connected to analog channel 5.

```python
def ads7830_command(channel):
    return 0x84 | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)
```

This creates the command byte for the ADS7830. The Raspberry Pi cannot read analog values directly, so it tells the ADC which analog channel to read.

```python
def read_adc(channel):
    cmd = ads7830_command(channel)
    bus.write_byte(ADC_ADDR, cmd)
    time.sleep(0.01)
    return bus.read_byte(ADC_ADDR)
```

This sends the channel command to the ADC and then reads back an 8-bit value between `0` and `255`.

```python
def make_bar(value):
    blocks = int((value / 255) * 16)
    return "#" * blocks + "-" * (16 - blocks)
```

This converts the joystick value into a 16-character LCD bar.

Example:

```text
value = 0     → ----------------
value = 128   → ########--------
value = 255   → ################
```

In `run()`:

```python
x_val = read_adc(X_CHANNEL)
line1 = make_bar(x_val)
line2 = f"VRX=> {x_val}"
```

The program continuously reads the joystick X value, creates a bar graph, and displays the raw value on the second line.

### Oral explanation

> “This script reads the X-axis of the joystick using an ADS7830 analog-to-digital converter. The Raspberry Pi cannot read analog signals directly, so I send a command to the ADC telling it to read channel 5. The ADC returns a value between 0 and 255. I then convert that value into a 16-character bar graph for the first LCD line, and I show the raw value on the second LCD line.”

## 5 oral questions + answers

### 1. Why do you need an ADC?

Because the Raspberry Pi GPIO pins can only read digital HIGH or LOW signals. The joystick gives an analog voltage, so the ADC converts that voltage into a digital value between `0` and `255`.

### 2. What does `X_CHANNEL = 5` mean?

It means the X-axis of the joystick is connected to analog input channel 5 of the ADS7830.

### 3. What range does the ADC return?

The ADS7830 returns an 8-bit value, so the range is from `0` to `255`.

### 4. What does `make_bar()` do?

It maps the ADC value from `0–255` to `0–16` LCD blocks. Then it creates a fake bar graph using `#` for filled blocks and `-` for empty blocks.

### 5. What would happen when the joystick moves left or right?

The analog voltage changes, so the ADC value changes. A lower value creates a shorter bar, and a higher value creates a longer bar.
