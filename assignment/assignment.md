

This is the **main controller script**. It imports all six screen scripts and switches between them when the joystick button is pressed.

Important part:

```python
screens = [
    screen1.run,
    screen2.run,
    screen3.run,
    screen4.run,
    screen5.run,
    screen6.run,
]
```

This stores all screen `run()` functions in a list.

```python
screen_thread = threading.Thread(
    target=screens[index],
    args=(stop_event,),
    daemon=True
)
```

Each screen runs in its own thread.
The `stop_event` is passed to the screen so the screen knows when it must stop.

```python
stop_event.set()
```

This tells the current screen to stop before starting the next screen.

```python
current_screen = (current_screen + 1) % len(screens)
```

This goes to the next screen.
The `% len(screens)` makes it loop back from screen 6 to screen 1.

```python
GPIO.add_event_detect(
    JOY_BUTTON,
    GPIO.FALLING,
    callback=joystick_pressed,
    bouncetime=200
)
```

This detects when the joystick button is pressed.
Because the button uses pull-up, pressing it makes the signal go from HIGH to LOW, so we use `GPIO.FALLING`.

## Oral explanation

> “This main script controls the six screens. Each screen has a `run(stop_event)` function. I store those functions in a list and start the current screen in a separate thread. When the joystick button is pressed, the callback stops the current screen using `stop_event`, waits shortly for the thread to finish, increments the screen index, and starts the next screen. The modulo operator makes it loop back to screen 1 after screen 6.”

## 5 oral questions + answers

### 1. Why do you use threads?

Because every screen has its own loop. If a screen runs in the main thread, the program cannot listen properly for screen switching. A separate thread lets the current screen run while the main program handles button presses.

### 2. What is `stop_event` used for?

`stop_event` is used to tell the current screen to stop safely. Each screen checks:

```python
while not stop_event.is_set():
```

When the main script sets the event, the screen exits its loop.

### 3. Why do you use `% len(screens)`?

To loop through the screens. After screen 6, it goes back to screen 1 instead of going out of range.

### 4. Why do you use `GPIO.FALLING`?

Because the joystick button uses a pull-up resistor. Not pressed is HIGH, pressed is LOW. So a button press creates a falling edge.

### 5. Why do you use `switch_lock`?

To avoid two screen switches happening at the same time. It prevents race conditions if the button callback fires too quickly.
