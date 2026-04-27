

## The thing you're building

You've got an **8x8 LED matrix** — that's a little board with 64 LEDs arranged in a grid, 8 rows by 8 columns. You also have **4 buttons** and a **joystick** that can be clicked.

The goal: make a tiny drawing app, like an Etch-a-Sketch.

- A single LED **blinks** somewhere on the grid. That blinking LED is your "cursor" — it's where you currently are.
- You press the 4 buttons to **move the cursor** around (up, down, left, right).
- When you press the joystick, the LED at your current spot turns **solid** (it stays on, even when you move away). That's "drawing a dot."
- Press the joystick on a dot that's already drawn → it turns off again. That's "erasing."

That's it. That's the whole assignment. You can draw smiley faces or letters by walking the cursor around and clicking.

## Why the code is split into 3 files

Because there are 3 layers of "stuff" happening, and mixing them would be a mess.

**Layer 1 — `shift_register.py` — the "talking to the chip" layer**

The Pi only has so many GPIO pins. An 8x8 matrix needs 16 wires (8 rows + 8 columns). That's a lot of pins. So the kit uses a chip called a **74HC595 shift register** — basically a chip that lets you control 8 outputs using only 3 pins (data, clock, latch).

You send it bits one at a time over the data pin, pulse the clock to "push them in," then pulse the latch to say "ok, now actually output them." This file is just the boring plumbing that does that.

You don't really need to think about this file — it just works.

**Layer 2 — `led_matrix.py` — the "matrix abstraction" layer**

This file pretends the matrix is just an 8x8 grid of pixels you can turn on/off with `set_pixel(x, y)`, `clear_pixel(x, y)`, etc. It hides the messy reality.

The messy reality is: you can't actually light up arbitrary LEDs at the same time. The matrix is wired so that at any one moment, only **one row** can be lit. So to make it *look* like a full picture, you light row 0 for 1 ms, then row 1 for 1 ms, then row 2... and so on, super fast. Your eye blends them into a steady image. This trick is called **multiplexing**.

That's what `refresh_once()` does — it scans through all 8 rows once. You call it over and over in a loop, forever.

The "state" of the drawing lives in `self.row_data`, an array of 8 bytes. Each byte = one row. Each bit in the byte = one LED in that row. So `row_data[3] = 0b00010000` means "in row 3, column 4 is on."

**Layer 3 — `main.py` — the "game logic" layer**

This is the only file that's actually about your assignment. Everything else is plumbing.

What it does, in plain English, in a loop forever:

```
1. Check the time. If 0.3 seconds have passed, flip cursor_visible (blink).
2. Check if any direction button is pressed. If yes, move cursor_x or cursor_y.
3. Check if joystick was clicked. If yes, toggle the LED at the cursor.
4. Tell the matrix to draw one frame (one full row scan).
5. Go back to step 1.
```

That's the entire program.

## The two "tricky" ideas

**1. Debouncing.** If you press a button, you might hold it down for, like, 100 ms. The loop runs *thousands* of times per second. Without protection, one press would register as 50 presses and your cursor would shoot across the screen. So we save the time of the last accepted press (`last_move_time`) and ignore new presses until 0.18 seconds have passed.

**2. The blinking cursor.** The cursor isn't a real "drawn" pixel — it's faked. Every time we draw a frame, if `cursor_visible` is True, we XOR the cursor pixel into the row data *just for that frame*. Then a timer flips `cursor_visible` every 0.3 seconds, so it appears to blink. The actual `row_data` never has the cursor in it — only the drawn dots.

## How to think about it when reading the code

When you look at `main.py`, ask yourself: "what state is changing over time?" Three things:

- `cursor_x`, `cursor_y` → where the cursor is
- `cursor_visible` → is it currently in its "on" half of the blink?
- `matrix.row_data` → what's actually drawn

Buttons mutate the first one. The blink timer flips the second. The joystick click mutates the third. The display constantly reads all three and draws them.

Once you see it as "three pieces of state, three things that change them, one loop that draws them" — the code stops looking scary. It's just bookkeeping.

