### Assignment-specific explanation

Screen 6 creates a **BLE GATT UART server** on the Raspberry Pi.
The LCD first shows:

```text
Send a message
via BLE UART
```

Then, when a message arrives through BLE, the message is displayed on the LCD.

The important parts are:

```python
rx_q = queue.Queue()
tx_q = queue.Queue()
device_name = "pj-pi-gatt-uart"
```

`rx_q` stores incoming BLE messages.
`tx_q` would be used for outgoing BLE messages.
`device_name` is the Bluetooth name shown to other devices.

```python
threading.Thread(
    target=ble_gatt_uart_loop,
    args=(rx_q, tx_q, device_name),
    daemon=True
).start()
```

This starts the BLE UART server in a separate thread.

That is important because the BLE server must keep running while the main program also updates the LCD.

```python
incoming = rx_q.get(timeout=0.1)
```

This checks if a new BLE message arrived.
The timeout prevents the program from getting stuck forever while waiting.

```python
if isinstance(incoming, (bytes, bytearray)):
    incoming = incoming.decode("utf-8", errors="ignore").strip()
```

BLE data can arrive as bytes, so the program converts it into a normal string.

```python
line1 = incoming[:16]
line2 = incoming[16:32]
```

The LCD only has 16 characters per line, so the message is split over two lines.

### Oral explanation

> “This script starts a BLE GATT UART service on the Raspberry Pi. At the beginning, the LCD tells the user to send a message via BLE UART. The BLE server runs in a separate thread, because the main loop still needs to keep checking for incoming messages and update the LCD. Incoming messages are put in a receive queue. When the main loop gets a message from that queue, it decodes it if needed, splits it into two 16-character lines, and displays it on the LCD.”

## 5 oral questions + answers

### 1. Why do you use a queue?

Because the BLE server and the LCD loop run separately. The BLE thread puts incoming messages into `rx_q`, and the main program reads them safely from that queue.

### 2. Why does the BLE server run in a separate thread?

Because the BLE UART loop needs to keep running continuously. If it ran in the main loop, it could block the LCD update logic.

### 3. What is `rx_q` used for?

`rx_q` is the receive queue. It stores messages that arrive from BLE until the main program reads and displays them.

### 4. Why do you decode the incoming data?

Because BLE messages may arrive as bytes. The LCD needs normal text, so bytes are decoded to a UTF-8 string.

### 5. Why do you split the message with `incoming[:16]` and `incoming[16:32]`?

Because the LCD is 16 by 2. The first 16 characters go on line 1, and the next 16 characters go on line 2.

---

## Exam practice questions

### Q1. Why does the BLE server run in a separate thread instead of the main loop?

The BLE UART loop must run continuously. If it ran in the main loop it would block — the main loop would be stuck inside the BLE function and never reach the LCD code, causing the screen to freeze.

---

### Q2. Why is a `queue.Queue()` used instead of a plain variable to pass messages between threads?

Thread safety. Two threads reading and writing the same plain variable at the same time can corrupt the data. `queue.Queue()` is specifically designed to be safe for multiple threads to use simultaneously — one thread puts messages in, the other takes them out, without clashing.

---

### Q3. What does `timeout=0.1` do in `rx_q.get(timeout=0.1)`, and what happens if no message arrives?

It prevents the program from blocking forever while waiting for a BLE message. If no message arrives within 0.1 seconds, `queue.Empty` is raised. The code catches that with `except queue.Empty: pass` and does nothing, then loops again. Without the timeout the program would block there indefinitely and never check the stop event.

---

### Q4. Why might BLE data arrive as bytes, and what does `errors="ignore"` protect against?

BLE transmits raw bytes over the air. The program must decode them into a Python string before the LCD can display them. `errors="ignore"` protects against bytes that are not valid UTF-8 characters — without it Python would crash with a `UnicodeDecodeError`. Ignoring them silently drops the bad bytes and displays the rest of the message normally.

---

### Q5. What does `daemon=True` mean and why is it important?

A daemon thread automatically closes when the main thread exits. Without `daemon=True` the BLE thread would keep running even after Ctrl+C is pressed and the program would never fully exit — you would have to force-kill it.
