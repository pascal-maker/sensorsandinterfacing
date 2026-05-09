 Q: Why do you send data in two nibbles?                                       
  A: The LCD only has 4 data pins wired, so one byte (8 bits) must be split into
   two 4-bit chunks — high nibble first, then low nibble.                       
                                                                                
  ---                                                                           
  Q: Why do you pulse the enable pin for every byte?                          
  A: The LCD only reads data on the falling edge of the enable pin. Without that
   pulse it ignores everything sitting on the data pins entirely.
                                                                                
  ---
  Q: Why is 0x08 OR'd into every byte?                                          
  A: It keeps the backlight transistor on. Without it the display logic works 
  perfectly but the screen goes dark because no light shines through the
  characters.                                                                   
   
  ---                                                                           
  Q: Why are there time.sleep calls in lcd_toggle_enable?                     
  A: The LCD needs time to process signals. Without the delays it tries to latch
   data before you've finished sending it, producing garbage output.
                                                                                
  ---                                                                         
  Q: Why use a threading Event instead of a plain variable to stop the loop?    
  A: A plain variable has no thread-safety guarantee — the other thread might   
  not see the change immediately. A threading Event is specifically designed for
   reliable signaling between threads.                                          
                                                                              
  ---                                    
  Q: What happens if get_ip_addresses crashes?
  A: The script dies, the display freezes on whatever was last shown, and there 
  is no recovery or fallback.

  Good script. For the oral evaluation, don’t explain the LCD internals too much. Focus on this part:

```python
output = subprocess.check_output("ip a", shell=True, text=True)
```

This runs the Linux command `ip a` from Python and stores the full output as text.

Then this part filters the output:

```python
if "wlan0:" in line:
    current_adapter = "wlan0"
elif "eth0:" in line:
    current_adapter = "eth0"
elif line.startswith("inet"):
    ip_address = line.split()[1].split("/")[0]
```

Meaning:

* when the script sees `wlan0`, it knows the next IPv4 line belongs to WiFi
* when it sees `eth0`, it knows the next IPv4 line belongs to LAN
* when it sees a line starting with `inet`, it extracts only the IP address
* `.split()[1]` gets something like `192.168.1.42/24`
* `.split("/")[0]` removes `/24`, leaving only `192.168.1.42`

Then this decides where to store it:

```python
if current_adapter == "wlan0":
    wlan_ip = ip_address
elif current_adapter == "eth0":
    eth_ip = ip_address
```

Finally, `run()` shows them on the LCD:

```python
lcd_string("WiFi: ", LCD_LINE_1)
lcd_string(wlan_ip, LCD_LINE_2)
```

Then after 2 seconds:

```python
lcd_string("LAN: ", LCD_LINE_1)
lcd_string(eth_ip, LCD_LINE_2)
```

So your oral explanation can be:

> “This program runs the Linux command `ip a` using `subprocess.check_output`. Then it goes line by line through the output. When it sees `wlan0` or `eth0`, it remembers which adapter it is reading. When it finds an IPv4 line starting with `inet`, it extracts only the IP address by splitting away the subnet mask. Then it displays the WiFi IP and LAN IP on the LCD, alternating every two seconds.”

## 5 oral questions + answers

### 1. Why do you use `subprocess.check_output()`?

Because the assignment asks to run a system command from Python. `check_output("ip a")` executes the Linux command and returns the output, so I can process it inside Python.

### 2. Why do you use `text=True`?

Because otherwise the output would be bytes. With `text=True`, Python gives me a normal string, so I can use `.splitlines()`, `.strip()`, and `.split()`.

### 3. How do you know whether an IP belongs to WiFi or LAN?

I keep track of the current adapter with `current_adapter`. When I read a line containing `wlan0`, I set it to WiFi. When I read `eth0`, I set it to LAN. The next `inet` line then belongs to that adapter.

### 4. What does this line do?

```python
ip_address = line.split()[1].split("/")[0]
```

It extracts only the IPv4 address. For example, from:

```text
inet 192.168.1.20/24
```

`line.split()[1]` gives `192.168.1.20/24`, and `.split("/")[0]` gives `192.168.1.20`.

### 5. What happens if WiFi or LAN is not connected?

The variable stays `"Not Connected"`, because that is the default value before reading the command output. So the LCD will show `"Not Connected"` instead of an IP address.

---

## Exam practice questions

### Q1. Your script uses `subprocess.check_output("ip a", shell=True, text=True)`. What does each argument do, and why is `text=True` important?

`"ip a"` is the Linux command that shows network information. `shell=True` runs it through the shell. `text=True` returns the output as a normal Python string instead of bytes. Without `text=True` you get raw bytes (`b'...'`), and string methods like `.splitlines()`, `.strip()`, and `.split()` will not work on bytes.

---

### Q2. Why is the byte split into two nibbles in `lcd_send_byte()`, and what does `| 0x08` do?

The I2C backpack only has 4 data lines wired to the LCD, so a full 8-bit byte cannot be sent at once. It is split into an upper nibble (top 4 bits) and a lower nibble (bottom 4 bits), each sent separately with an ENABLE pulse in between. `| 0x08` sets the backlight bit on the PCF8574 chip — remove it and the display logic still works but the screen goes dark.

---

### Q3. In `get_ip_addresses()`, how does the script know whether an IP belongs to WiFi or LAN?

It uses a state machine. `current_adapter` tracks which section of the `ip a` output is being read. When a line contains `wlan0:`, the state is set to `"wlan0"`. When it contains `eth0:`, the state is set to `"eth0"`. When a line starts with `inet`, the IP address is extracted and stored under whichever adapter is currently active. The key term is **state machine** — the variable remembers which section you are in.

---

### Q4. What does `lcd_toggle_enable()` do, and why are `time.sleep()` calls needed?

It pulses the ENABLE pin HIGH then LOW. The LCD only reads data on the falling edge (HIGH→LOW) — without this pulse the LCD ignores everything on the data pins. The `time.sleep(0.0005)` delays are critical because the LCD is much slower than the Pi CPU. Without the delays the Pi moves on before the LCD has finished reading, producing garbage output.

---

### Q5. Why use `threading.Event` instead of a plain boolean to stop the loop?

A plain boolean has no thread-safety guarantee — when one thread writes `running = False`, the other thread may not see that change immediately due to CPU caching or instruction reordering. `threading.Event` is specifically designed so the signal is guaranteed to be visible across threads immediately.

