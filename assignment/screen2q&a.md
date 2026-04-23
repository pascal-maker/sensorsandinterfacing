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


