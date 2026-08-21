# Glossary

Key terms used across this project, explained simply.

---

## Bit

The smallest unit of data in computing. It can only be one of two values:

- `0` — off / false / low
- `1` — on / true / high

Everything a computer does is built from bits.

---

## Nibble

Half a byte — exactly 4 bits.

Example byte split into two nibbles:

```
10101111
^^^^      upper nibble = 1010
    ^^^^  lower nibble = 1111
```

**Why it matters in this project:**
The I2C backpack only has 4 data pins wired to the LCD. You cannot send 8 bits at once, so every byte is split into two nibbles and sent one at a time.

---

## Byte

8 bits grouped together. The standard unit of data.

| Unit   | Bits | Example    |
|--------|------|------------|
| Bit    | 1    | `1`        |
| Nibble | 4    | `1010`     |
| Byte   | 8    | `10101111` |

A byte can represent 256 different values (0–255).

---

## Binary

A number system that uses only `0` and `1` (base 2), instead of the digits 0–9 we use normally (base 10).

In Python, binary numbers are written with the `0b` prefix:

```python
0b00000100  # binary for the number 4
0b00000001  # binary for the number 1
```

Binary is used in this project because it lets you see exactly which individual bit (pin) is being turned on or off.

---

## Hex (Hexadecimal)

A number system that uses 16 symbols: `0–9` then `A–F` (base 16). In Python, hex numbers start with `0x`.

One hex digit represents exactly 4 bits (one nibble), so one byte = two hex digits.

```
0x27  =  0010 0111  (I2C address of the LCD)
0x80  =  1000 0000  (start of LCD row 1)
0x01  =  0000 0001  (LCD clear command)
```

Hex is used for LCD commands and addresses because it is more compact than binary but still maps cleanly to bits.

---

## I2C (Inter-Integrated Circuit)

A communication protocol that lets the Raspberry Pi talk to devices like the LCD using only two wires:

- **SDA** — data line (sends the actual bytes)
- **SCL** — clock line (keeps both sides in sync)

Each device on the bus has a unique address (the LCD backpack in this project is at `0x27`). The Pi sends a message to that address and the correct device responds.

---

## I2C Backpack (PCF8574)

A small chip soldered onto the back of the LCD module. It converts the two-wire I2C signal from the Pi into the 8 parallel signals the LCD actually needs. Without it, you would need 8+ GPIO pins just for the display.

---

## GPIO (General Purpose Input/Output)

The physical pins on the Raspberry Pi that can be controlled by software. You can set them HIGH (3.3V) or LOW (0V) to control hardware.

---

## Register Select (RS)

A control pin on the LCD that tells it what type of data is coming next.

- `RS = 0` → command mode (instruction like "clear screen" or "move cursor")
- `RS = 1` → character mode (text to display like the letter 'A')

In code, RS is OR'd into every byte before sending so the LCD always knows what to expect:

```python
RS = 0b00000001
```

---

## Enable Pin (ENABLE)

A control pin that acts like a trigger. The LCD ignores data sitting on its pins until ENABLE is pulsed HIGH then LOW. It only reads on the **falling edge** (the moment it goes from HIGH to LOW).

```python
ENABLE = 0b00000100
```

This is why `lcd_toggle_enable()` exists — to ring that bell for every piece of data sent.

---

## Falling Edge

The moment a signal transitions from HIGH (1) to LOW (0). The HD44780 LCD reads data on the falling edge of the ENABLE pin — not while it is high, not while it is low, but at the exact moment it drops.

---

## 4-bit Mode

A way of operating the LCD where only 4 data pins are used instead of 8. Every byte must be split into two nibbles and sent separately. This is why the I2C backpack works — it only has 4 data lines to spare after using the other 4 for control pins (RS, ENABLE, backlight, read/write).

---

## ASCII

A standard that assigns a number to every printable character. For example:

```
'A' = 65
'H' = 72
' ' = 32
```

In Python, `ord('A')` gives `65`. The LCD expects ASCII numbers when in character mode, which is why `ord()` is called on each character before sending it.

---

## SMBus / smbus2

A Python library used to communicate over I2C. `smbus2` is the version used in this project. The key method is:

```python
bus.write_byte(address, data)
```

This sends one byte to the device at the given address.

---

## subprocess

A Python module that lets you run Linux shell commands from inside a Python script. In this project it runs `ip a` to get network information:

```python
subprocess.check_output("ip a", shell=True, text=True)
```

- `"ip a"` — the Linux command to run
- `shell=True` — run it through the shell
- `text=True` — return the output as a string (not bytes)

Without `text=True`, you get raw bytes (`b'...'`) and string methods like `.split()` will not work.

---

## threading.Event

A thread-safe signal used to communicate between threads. One thread can call `.set()` to raise the signal, and another thread checks `.is_set()` to know when to stop.

Used instead of a plain variable (`running = False`) because a plain variable has no guarantee that changes are visible to other threads immediately. `threading.Event` is specifically built for safe cross-thread signalling.

---

## State Machine

A pattern where a variable tracks the current "state" and decisions are made based on that state. In `get_ip_addresses()`, `current_adapter` is the state variable:

```python
if "wlan0:" in line:
    current_adapter = "wlan0"   # enter WiFi state
elif "eth0:" in line:
    current_adapter = "eth0"    # enter Ethernet state
elif line.startswith("inet "):
    # store IP under whichever state is active
```

The state tells the code which section of the `ip a` output it is currently reading.

---

## DDRAM (Display Data RAM)

The internal memory of the LCD. Characters you send are stored here and displayed on screen. Each memory address maps to a position on the display:

- `0x80` = start of row 1
- `0xC0` = start of row 2

Sending these addresses as a command moves the cursor to that row before writing text.
