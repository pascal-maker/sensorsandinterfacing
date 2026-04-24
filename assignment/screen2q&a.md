Here it is in **clean question → answer format** (good for studying / exam 👇)

---

### LCD Data Transfer

**Q: How are bytes sent to the LCD in 4-bit mode?**
A:

1. Send upper nibble `(bits & 0xF0)` with mode + backlight, pulse EN
2. Send lower nibble `((bits << 4) & 0xF0)` with mode + backlight, pulse EN
   Each nibble needs an EN pulse because the LCD reads data on the rising edge of EN.

---

### Hardware / Logic

**Q: Why do buttons read LOW when pressed?**
A: Because of pull-up resistors. The pin is HIGH (3.3V) by default, and pressing the button connects it to GND → LOW.

**Q: What does `pull_up_down=GPIO.PUD_UP` do?**
A: It enables an internal pull-up resistor (~50kΩ) so the pin stays HIGH when not pressed and doesn’t float.

---

### Nibble Logic

**Q: What happens when no buttons are pressed?**
A:
`0 0 0 0 → 0b0000 → 0x0 → 0`

**Q: Only button_2 pressed?**
A:
`(0 << 3) | (1 << 2) | (0 << 1) | 0 = 4`
→ `0b0100 → 0x4 → 4`

**Q: Why use `if value != last_value`?**
A: To avoid unnecessary LCD updates → prevents flickering and reduces I2C traffic.

---

### I2C & LCD

**Q: Where does `0x27` come from?**
A: It’s the I2C address of the LCD backpack (PCF8574). Found with `i2cdetect -y 1`.

**Q: Why send `0x33` and `0x32` first?**
A: To force the LCD into 4-bit mode from an unknown startup state.

**Q: What does `0x28` do?**
A: Sets 4-bit mode, 2 lines, 5x8 font (final configuration).

**Q: What does `0x06` (entry mode) do?**
A: Moves cursor right after each character.

---

### Main Loop

**Q: Why use `stop_event`?**
A: Cleaner control, especially with threads (can stop from anywhere without exceptions).

**Q: Why `last_value = -1`?**
A: Forces the LCD to update at startup (since valid values are 0–15).

**Q: Why `time.sleep(0.1)`?**
A: Prevents flooding the LCD/I2C bus and avoids flickering.

---

### Behavior / Edge Cases

**Q: What if multiple buttons are pressed?**
A:

* 2 buttons → e.g. `0b0011 = 3`
* 3 buttons → `0b0111 = 7`
* 4 buttons → `0b1111 = 15`

**Q: Does removing `0x28` break things?**
A: Sometimes. Some LCDs still work, but safest is to include it.

---

### LCD Memory

**Q: What is DDRAM?**
A: Display RAM → what you see on the screen.

**Q: What is CGRAM?**
A: Custom character memory → lets you define your own symbols.

---

### Design Concept

**Q: Why does the LCD use 4-bit mode?**
A: To save GPIO pins. Older microcontrollers had limited pins, so 4-bit mode halves the required data lines.

Focus only on these 4 parts.

### 1. Button setup

```python
GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
```

Each button is an input with an internal pull-up resistor.

So:

```text
not pressed = HIGH = 0
pressed     = LOW  = 1
```

That is why your code reverses the logic here:

```python
b1 = 1 if GPIO.input(BUTTON_1) == GPIO.LOW else 0
```

### 2. Make 4 bits into a nibble

```python
value = (b1 << 3) | (b2 << 2) | (b3 << 1) | b4
```

This makes one 4-bit number.

Example:

```text
b1 b2 b3 b4 = 1 0 1 1

b1 << 3 = 1000
b2 << 2 = 0000
b3 << 1 = 0010
b4      = 0001

result  = 1011 = 11 decimal
```

So `b1` is the most significant bit, and `b4` is the least significant bit.

### 3. Format for LCD

```python
binary_text = f"0b{value:04b}"
hex_text = f"0x{value:01x}"
```

This creates:

```text
value = 15
binary_text = 0b1111
hex_text = 0xf
```

Then:

```python
line1 = binary_text + hex_text.rjust(16-len(binary_text))
line2 = str(value).rjust(16)
```

This aligns binary left, hex right, and decimal right.

### 4. Update only when value changes

```python
if value != last_value:
```

The LCD only updates when a new button combination is pressed. This avoids constantly clearing and rewriting the same screen.

Oral explanation:

> “This script reads four buttons as four bits. Because I use pull-up resistors, a pressed button reads LOW, so I convert LOW to 1 and HIGH to 0. Then I combine the four bits into one nibble using bit shifts. `b1` becomes the most significant bit and `b4` the least significant bit. After that I format the value as binary, hexadecimal, and decimal, and display it on the LCD. The screen only updates when the value changes.”

## 5 oral questions + answers

### 1. Why does a pressed button become `1` even though GPIO reads `LOW`?

Because the buttons use internal pull-up resistors. When the button is not pressed, the input is HIGH. When pressed, it connects to ground, so it becomes LOW. In the program, I convert LOW to `1` because logically that means “button pressed”.

### 2. What is a nibble?

A nibble is 4 bits. In this assignment, the four buttons together form one nibble, with values from `0000` to `1111`, so decimal `0` to `15`.

### 3. Explain this line:

```python
value = (b1 << 3) | (b2 << 2) | (b3 << 1) | b4
```

It places each button bit in the correct position. `b1` is shifted to bit position 3, `b2` to position 2, `b3` to position 1, and `b4` stays at position 0. The OR operator combines them into one 4-bit value.

### 4. What does `value:04b` mean?

It formats the number as binary with 4 digits. For example, decimal `3` becomes `0011`, so the LCD shows `0b0011`.

### 5. Why do you use `last_value`?

To update the LCD only when the button combination changes. Without `last_value`, the LCD would keep clearing and rewriting even when nothing changed.

