# Practice Exam 6 — Keypad Servo Lock With Alarm and Lockout

## Goal

Build a four-digit keypad lock. A correct code unlocks a servo temporarily.
Three wrong attempts trigger an alarm and a timed lockout. Record every completed
attempt to CSV without storing the secret code in the log.

This is an unsolved practice exam.

## Hardware

- 4×4 keypad rows: GPIO `16`, `20`, `21`, `26`
- 4×4 keypad columns: GPIO `19`, `13`, `6`, `5`
- Servo signal: GPIO `18`
- Active buzzer: GPIO `23`
- Secret code for testing: `2580`

## Key meanings

- Digits `0..9`: append a digit, maximum four digits.
- `*`: clear the current entry.
- `#`: submit the entry.
- Ignore A–D.

## Required behaviour

1. Servo starts locked at 0°.
2. A correct code moves it to 90° for five seconds, then relocks it.
3. A wrong code gives two short beeps and increments the failure count.
4. After three consecutive failures, sound a one-second alarm and enter a
   15-second lockout.
5. During lockout, ignore keypad input and print the remaining whole seconds no
   more than once per second.
6. A successful unlock resets the failure count.
7. Log each submitted attempt as:
   `timestamp,result,digits_entered,failed_attempts`.
8. Never store the actual entered code or secret in the CSV.
9. On Ctrl+C, lock and release the servo, silence the buzzer, close CSV, return
   keypad columns HIGH, and clean GPIO.

## Design requirements

- Use a state variable or enum for `LOCKED`, `UNLOCKED`, and `LOCKOUT`.
- Use `time.monotonic()` deadlines; do not block for the five- or 15-second
  periods with a single `sleep()`.
- Put code validation in a separate function.
- Use `Keypad4x4`, `ServoMotor`, `ActiveBuzzer`, and `CSVLogger`.

## Self-check

- [ ] Holding a key enters it only once.
- [ ] `*` reliably clears partial input.
- [ ] A correct code unlocks and automatically relocks.
- [ ] Exactly three wrong submissions start lockout.
- [ ] Key presses during lockout have no effect.
- [ ] The CSV reveals only result and digit count, never entered digits.
- [ ] Ctrl+C always returns the lock to a safe state.
