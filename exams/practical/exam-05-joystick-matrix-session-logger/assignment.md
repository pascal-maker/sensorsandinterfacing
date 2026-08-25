# Practice Exam 5 — Joystick Matrix Session Logger

## Goal

Build a joystick-controlled 8×8 drawing application. A joystick moves a cursor,
its push button draws or erases pixels, a separate button starts/stops a logging
session, and every accepted action is written to CSV.

This is an unsolved practice exam. Do not copy the completed Week 09 assignment;
compose the reusable exam-kit classes and write the application logic yourself.

## Hardware

- ADS7830 address: `0x48`
- Joystick X channel: `6`
- Joystick Y channel: `5`
- Joystick click: GPIO `7`
- Session toggle button: GPIO `20`
- 74HC595 data/latch/clock: GPIO `22`, `27`, `17`
- 8×8 LED matrix connected through the two 74HC595 chips

## Required behaviour

1. Start the cursor at the centre of the matrix.
2. Moving the joystick beyond its thresholds moves one cell at a time.
3. Require the joystick to return to `CENTER` before accepting another move.
4. Clamp X and Y to `0..7`.
5. Joystick click toggles the selected pixel.
6. GPIO 20 toggles session logging on/off and prints the new state.
7. While logging is enabled, write a CSV row for every move or pixel toggle:
   `timestamp,event,x,y,pixel_state,joystick_x,joystick_y`.
8. The cursor must remain visible while saved pixels remain stored.
9. On Ctrl+C, stop the matrix thread, close CSV and I2C, blank the matrix, and
   clean up GPIO.

## Restrictions

- Do not use one long blocking delay for joystick repeat control.
- Do not write a CSV row continuously while the joystick is held.
- Keep hardware pin constants at the top of the program.
- Use at least four reusable classes from `exams/copy_paste_kit/`.

## Suggested build order

1. Make the matrix show a centre cursor.
2. Print joystick directions without moving anything.
3. Add one-move-per-centre-return logic.
4. Add draw/erase.
5. Add session toggle and CSV logging.
6. Verify cleanup by stopping and immediately restarting the program.

## Self-check

- [ ] All four directions reach every matrix edge.
- [ ] Holding the joystick does not race across the display.
- [ ] Drawing the same position twice turns it on and then off.
- [ ] Logging-disabled actions do not appear in the CSV.
- [ ] The CSV contains a header and flushes each row.
- [ ] Ctrl+C leaves the matrix dark.
