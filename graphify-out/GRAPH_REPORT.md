# Graph Report - sensorsandinterfacing  (2026-08-28)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1371 nodes · 2026 edges · 142 communities (104 shown, 38 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 67 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a0fdb2ed`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- assignment/ble/bluetooth_uart_server.py
- practicalexam1.py
- BcdSevenSegmentApp
- datavisualization/main.py
- FourDigit7Segment
- assignment/assignment.py
- Joystick
- practicalexam2.py
- ShiftRegister
- ShiftRegister
- LCDService
- main
- assignment/ble/utils_gatt_server.py
- LedMatrix8x8
- ble_rpi/ble/utils_gatt_server.py
- LCDService
- ShiftRegister
- DCMotor
- CharacteristicUserDescriptionDescriptor
- Descriptor
- Descriptor
- ButtonService
- firstdemo.py
- ble_rpi/ble/bluetooth_uart_server.py
- HeartRateMeasurementChrc
- buzzer.py
- LCD
- LCD
- ButtonToggle
- Advertisement
- CharacteristicUserDescriptionDescriptor
- MPU6050
- screen5.py
- TxCharacteristic
- ShiftRegister
- LCD
- temporarysolution.py
- MPU6050
- MPU6050
- ADCReader
- MPU6050
- Service
- TestCharacteristic
- screen2.py
- screen4.py
- ButtonService
- Service
- Characteristic
- TestCharacteristic
- PassiveBuzzerService
- ActiveBuzzerService
- AutoOffTimer
- ble_rpi/ble/utils_advertisement.py
- Button
- Characteristic
- ShiftRegister
- main.py
- ble_rpi/assignment.py
- ble_win_mac/assignment.py
- week08/assignment.py
- ShiftRegister
- Keypad4x4
- pwm_adc.py
- ServoMotor
- MPU6050
- BatteryLevelCharacteristic
- CSVLogger
- BatteryLevelCharacteristic
- HeartRateMeasurementChrc
- projectone/main.py
- LED
- ADS7830
- week5/assignment.py
- communication.py
- SerialTransmitter
- BCDInput
- btn_timings.py
- Application
- firstexercise.py
- RGBLed
- send_byte
- uart_client.py
- steppermotorleft.py
- stppermotortight.py
- _handle
- pontentiometers.py
- exercisedsolution.py
- ShiftRegister
- angle_to_duty_cycle
- TestEncryptDescriptor
- TestSecureDescriptor
- week08/demo.py
- week08/testscript.py
- 3leds.py
- pedestrian.py
- joystick_monitor.py
- demoserial.py
- setup_sudoers.sh
- multibutton.py
- toggleassignement.py
- TestEncryptDescriptor
- TestSecureDescriptor

## God Nodes (most connected - your core abstractions)
1. `Characteristic` - 26 edges
2. `Characteristic` - 22 edges
3. `ADCReader` - 21 edges
4. `CSVLogger` - 21 edges
5. `ButtonToggle` - 18 edges
6. `ShiftRegister` - 18 edges
7. `ShiftRegister` - 17 edges
8. `Advertisement` - 16 edges
9. `BcdSevenSegmentApp` - 16 edges
10. `SevenSegmentDisplay` - 16 edges

## Surprising Connections (you probably didn't know these)
- `UartAdvertisement` --uses--> `Advertisement`  [INFERRED]
  week07/ble_rpi/ble/bluetooth_uart_server.py → assignment/ble/utils_advertisement.py
- `_get()` --uses--> `LCDService`  [INFERRED]
  week08/projectone/interface/pages/lcd.py → week011/basic_lcd.py
- `RxCharacteristic` --uses--> `Characteristic`  [INFERRED]
  week07/ble_rpi/ble/bluetooth_uart_server.py → assignment/ble/utils_gatt_server.py
- `TxCharacteristic` --uses--> `Characteristic`  [INFERRED]
  week07/ble_rpi/ble/bluetooth_uart_server.py → assignment/ble/utils_gatt_server.py
- `UartService` --uses--> `Service`  [INFERRED]
  week07/ble_rpi/ble/bluetooth_uart_server.py → assignment/ble/utils_gatt_server.py

## Import Cycles
- None detected.

## Communities (142 total, 38 thin omitted)

### Community 0 - "assignment/ble/bluetooth_uart_server.py"
Cohesion: 0.05
Nodes (36): Application, ble_gatt_uart_loop(), find_adapter(), Advertisement, Characteristic, method, Service, Best-effort de-registration from BlueZ before exit. (+28 more)

### Community 1 - "practicalexam1.py"
Cohesion: 0.07
Nodes (31): button3_callback(), button4_callback(), clear_lcd(), CSGOBomb, defuse_button_callback(), draw_progress_bar(), init_LCD(), MPU6050 (+23 more)

### Community 2 - "BcdSevenSegmentApp"
Cohesion: 0.08
Nodes (11): AdcConfig, AutoOffControl, BcdConfig, BcdInput, BcdSevenSegmentApp, ButtonConfig, CsvLogger, FourDigitDisplay (+3 more)

### Community 3 - "datavisualization/main.py"
Cohesion: 0.07
Nodes (22): ActiveBuzzerService, PassiveBuzzerService, Passive buzzer — needs PWM to generate sound. Controls frequency and duty cycle., LCDService, HD44780 16x2 LCD via PCF8574 I2C backpack., Write up to 16 characters on each line., active_bz_beep(), active_bz_off() (+14 more)

### Community 4 - "FourDigit7Segment"
Cohesion: 0.08
Nodes (7): main(), pressed(), setup_buttons(), DisplayThread, FourDigit7Segment, LedMatrix8x8, ShiftRegister

### Community 5 - "assignment/assignment.py"
Cohesion: 0.13
Nodes (27): ads7830_command(), convert_to_percentage(), joystick_pressed(), main(), read_adc(), set_rgb(), setup_gpio(), start_screen() (+19 more)

### Community 6 - "Joystick"
Cohesion: 0.09
Nodes (7): ADCReader, Potentiometer, ADS7830 ADC helper used on the Freenove Projects Board., ButtonToggle, CSVLogger, Joystick, main()

### Community 7 - "practicalexam2.py"
Cohesion: 0.09
Nodes (26): add_value_to_matrix(), button_callback(), cleanup(), clear_matrix(), draw_matrix(), log_value(), potentiometer_to_column(), Turn all matrix LEDs off. (+18 more)

### Community 8 - "ShiftRegister"
Cohesion: 0.14
Nodes (6): main(), main(), Multiplexed common-anode 7-segment display through two 74HC595 chips., SevenSegmentDisplay, 74HC595 helper for Freenove display examples., ShiftRegister

### Community 9 - "ShiftRegister"
Cohesion: 0.13
Nodes (8): count_fingers(), gesture_loop(), get_gesture(), main(), MatrixDisplay, stream_feed(), LEDMatrix8x8, ShiftRegister

### Community 10 - "LCDService"
Cohesion: 0.13
Nodes (15): LCDService, HD44780 16x2 LCD via PCF8574 I2C backpack., Toggle the Enable pin to latch one nibble into the HD44780., Send a full byte as two 4-bit nibbles (high nibble first)., Write up to 16 characters on each line. Pads with spaces to clear old text., Clear the display and return cursor to home position., Turn the backlight on or off without changing display content., Clear the display, turn off backlight, and close the I2C bus. (+7 more)

### Community 11 - "main"
Cohesion: 0.12
Nodes (6): ADCReader, Potentiometer, ADS7830 ADC helper used on the Freenove Projects Board., ButtonToggle, CSVLogger, main()

### Community 12 - "assignment/ble/utils_gatt_server.py"
Cohesion: 0.13
Nodes (12): Application, BodySensorLocationChrc, FailedException, find_adapter(), HeartRateControlPointChrc, HeartRateService, InvalidValueLengthException, main() (+4 more)

### Community 13 - "LedMatrix8x8"
Cohesion: 0.14
Nodes (5): main(), main(), Joystick, LedMatrix8x8, 8x8 matrix helper. Column select is high; row LEDs are active-low.

### Community 14 - "ble_rpi/ble/utils_gatt_server.py"
Cohesion: 0.13
Nodes (12): Application, BodySensorLocationChrc, FailedException, find_adapter(), HeartRateControlPointChrc, HeartRateService, InvalidValueLengthException, main() (+4 more)

### Community 15 - "LCDService"
Cohesion: 0.13
Nodes (8): LCDService, HD44780 16x2 LCD via PCF8574 I2C backpack., Toggle the Enable pin to latch one nibble into the HD44780., Send a full byte as two 4-bit nibbles (high nibble first)., Write up to 16 characters on each line. Pads with spaces to clear old text., Clear the display and return cursor to home position., Turn the backlight on or off without changing display content., Clear the display, turn off backlight, and close the I2C bus.

### Community 16 - "ShiftRegister"
Cohesion: 0.18
Nodes (6): clear_matrix(), read_values(), clear(), clear_matrix(), test_matrix(), ShiftRegister

### Community 17 - "DCMotor"
Cohesion: 0.13
Nodes (7): DCMotor, Week 7 — Motors Classes: DCMotor, StepperMotor, Controls a DC motor via two PWM pins (H-bridge style). pin1 driven → forward;…, Spin forward at speed % (0–100)., Spin in reverse at speed % (0–100)., Controls a 28BYJ-48 style stepper motor using 4 GPIO pins (half-step mode)., StepperMotor

### Community 18 - "CharacteristicUserDescriptionDescriptor"
Cohesion: 0.16
Nodes (5): CharacteristicUserDescriptionDescriptor, NotPermittedException, Dummy test descriptor. Returns a static value., Writable CUD descriptor., TestDescriptor

### Community 19 - "Descriptor"
Cohesion: 0.21
Nodes (5): Descriptor, InvalidArgsException, NotSupportedException, method, org.bluez.GattDescriptor1 interface implementation

### Community 20 - "Descriptor"
Cohesion: 0.21
Nodes (5): Descriptor, InvalidArgsException, NotSupportedException, method, org.bluez.GattDescriptor1 interface implementation

### Community 21 - "ButtonService"
Cohesion: 0.16
Nodes (11): ButtonService, Return the debounced button state. Safe to call from any thread., Release the GPIO pin. Call this on shutdown., Blocking loop that fires callbacks on press and release. Cleans up on exit., create(), _get(), Blocks, ButtonService (+3 more)

### Community 22 - "firstdemo.py"
Cohesion: 0.12
Nodes (4): ADS7830, PWMLed, Week 4 — PWM & ADC Classes: - PWMLed - ADS7830 - RGBLed, RGBLed

### Community 23 - "ble_rpi/ble/bluetooth_uart_server.py"
Cohesion: 0.19
Nodes (12): ble_gatt_uart_loop(), find_adapter(), Advertisement, Best-effort de-registration from BlueZ before exit., Request BLE shutdown from any thread., shutdown_ble(), stop_ble_gatt_uart_loop(), UartAdvertisement (+4 more)

### Community 25 - "buzzer.py"
Cohesion: 0.23
Nodes (14): _active_beep(), _active_off(), _active_on(), create(), _get_active(), _get_passive(), _passive_play(), _passive_stop() (+6 more)

### Community 28 - "ButtonToggle"
Cohesion: 0.19
Nodes (4): ButtonToggle, main(), LedBarGraph, LED bar graph through a 74HC595 chain.

### Community 30 - "CharacteristicUserDescriptionDescriptor"
Cohesion: 0.16
Nodes (5): CharacteristicUserDescriptionDescriptor, NotPermittedException, Dummy test descriptor. Returns a static value., Writable CUD descriptor., TestDescriptor

### Community 32 - "screen5.py"
Cohesion: 0.32
Nodes (12): calculate_combined_g(), lcd_clear(), lcd_init(), lcd_send_byte(), lcd_string(), lcd_toggle_enable(), make_lines(), mpu_init() (+4 more)

### Community 33 - "TxCharacteristic"
Cohesion: 0.18
Nodes (5): Characteristic, Service, RxCharacteristic, TxCharacteristic, UartService

### Community 36 - "temporarysolution.py"
Cohesion: 0.18
Nodes (12): angle_to_duty_cycle(), map_value_to_angle(), Move servo to the requested angle., Temporary output function. Because the LCD is not detected yet, this version…, Button interrupt callback. Toggles the system on or off., Read one analog value from the ADC. This version uses the command pattern that…, Convert ADC value (0..255) to servo angle (0..180)., Convert servo angle (0..180) to PWM duty cycle. Servo expects: - 50 Hz PWM - 20… (+4 more)

### Community 39 - "ADCReader"
Cohesion: 0.23
Nodes (4): ADCReader, Potentiometer, ADS7830 ADC helper used on the Freenove Projects Board., main()

### Community 41 - "Service"
Cohesion: 0.22
Nodes (4): BatteryService, Fake Battery service that emulates a draining battery., org.bluez.GattService1 interface implementation, Service

### Community 42 - "TestCharacteristic"
Cohesion: 0.18
Nodes (6): Dummy test service that provides characteristics and descriptors that exercise…, Dummy test characteristic. Allows writing arbitrary bytes to its value, and…, Dummy test characteristic requiring encryption., TestCharacteristic, TestEncryptCharacteristic, TestService

### Community 43 - "screen2.py"
Cohesion: 0.38
Nodes (10): format_screen(), lcd_clear(), lcd_init(), lcd_send_byte(), lcd_string(), lcd_toggle_enable(), make_nibble(), read_buttons_bits() (+2 more)

### Community 44 - "screen4.py"
Cohesion: 0.38
Nodes (10): ads7830_command(), lcd_clear(), lcd_init(), lcd_send_byte(), lcd_string(), lcd_toggle_enable(), make_bar(), read_adc() (+2 more)

### Community 45 - "ButtonService"
Cohesion: 0.27
Nodes (5): get_button_service(), ButtonService, read_button_state(), ButtonService, main()

### Community 46 - "Service"
Cohesion: 0.22
Nodes (4): BatteryService, Fake Battery service that emulates a draining battery., org.bluez.GattService1 interface implementation, Service

### Community 47 - "Characteristic"
Cohesion: 0.20
Nodes (4): Characteristic, org.bluez.GattCharacteristic1 interface implementation, Dummy test characteristic requiring secure connection., TestSecureCharacteristic

### Community 48 - "TestCharacteristic"
Cohesion: 0.18
Nodes (6): Dummy test service that provides characteristics and descriptors that exercise…, Dummy test characteristic. Allows writing arbitrary bytes to its value, and…, Dummy test characteristic requiring encryption., TestCharacteristic, TestEncryptCharacteristic, TestService

### Community 49 - "PassiveBuzzerService"
Cohesion: 0.18
Nodes (5): PassiveBuzzerService, Passive buzzer — needs PWM to generate sound. Controls frequency and duty cycle., Play a tone for `duration` seconds. frequency -- pitch in Hz (set to 0 or…, Immediately silence the buzzer without releasing the pin., Silence, stop PWM, and release the GPIO pin.

### Community 50 - "ActiveBuzzerService"
Cohesion: 0.22
Nodes (6): ActiveBuzzerService, Active buzzer — digital ON/OFF only. Has its own internal oscillator., Switch the buzzer on continuously., Switch the buzzer off., Emit a single beep of the given duration (seconds)., Silence and release the GPIO pin.

### Community 52 - "ble_rpi/ble/utils_advertisement.py"
Cohesion: 0.27
Nodes (9): FailedException, find_adapter(), InvalidArgsException, InvalidValueLengthException, main(), NotPermittedException, NotSupportedException, shutdown() (+1 more)

### Community 53 - "Button"
Cohesion: 0.20
Nodes (5): Button, Return True while button is held down (active-LOW)., Return True on the falling edge (button just pressed)., Return True on the rising edge (button just released)., Call once per loop to keep edge detection state fresh.

### Community 54 - "Characteristic"
Cohesion: 0.20
Nodes (4): Characteristic, org.bluez.GattCharacteristic1 interface implementation, Dummy test characteristic requiring secure connection., TestSecureCharacteristic

### Community 56 - "main.py"
Cohesion: 0.36
Nodes (8): blink_led(), main(), main.py — Multi-mode sensor station ====================================…, Blink the single LED `times` times (blocking, run in thread)., run_bcd_mode(), run_imu_mode(), run_motor_mode(), set_mode()

### Community 57 - "ble_rpi/assignment.py"
Cohesion: 0.28
Nodes (3): stepper_half_turn(), stepper_turn_steps(), stop_stepper()

### Community 58 - "ble_win_mac/assignment.py"
Cohesion: 0.28
Nodes (3): stepper_half_turn(), stepper_turn_steps(), stop_stepper()

### Community 59 - "week08/assignment.py"
Cohesion: 0.36
Nodes (6): clear_register(), copy_to_storage_register(), set_bar_graph(), shift_out_16bit(), write_byte(), write_one_bit()

### Community 62 - "pwm_adc.py"
Cohesion: 0.22
Nodes (4): PWMLed, Week 4 — PWM & ADC Classes: PWMLed, ADS7830, RGBLed, Single LED controlled via PWM (0–100 % brightness)., Set brightness 0–100 %.

### Community 63 - "ServoMotor"
Cohesion: 0.28
Nodes (4): Controls a hobby servo via PWM (50 Hz). Angle range: 0–180 degrees., Move servo to angle (degrees), hold for hold_ms, then release., Sweep from start to end angle in steps., ServoMotor

### Community 69 - "projectone/main.py"
Cohesion: 0.29
Nodes (5): create(), Blocks, Open a short-lived connection to the daemon, send command, return the response., Add the System tab to the shared Blocks app., _send()

### Community 71 - "ADS7830"
Cohesion: 0.29
Nodes (4): ADS7830, Driver for the ADS7830 8-channel, 8-bit ADC over I2C. Default I2C address:…, Return raw ADC value (0–255) for the given channel., Return voltage in volts for the given channel.

### Community 72 - "week5/assignment.py"
Cohesion: 0.36
Nodes (4): lcd_display_string(), lcd_init(), lcd_send_byte(), lcd_toggle_enable()

### Community 73 - "communication.py"
Cohesion: 0.25
Nodes (4): I2CScanner, Week 5 — Serial & I2C Communication Classes: SerialTransmitter, I2CScanner,…, Scans the I2C bus for connected devices., Return a list of hex address strings for found devices.

### Community 74 - "SerialTransmitter"
Cohesion: 0.29
Nodes (4): Transmits bytes bit-by-bit over a single GPIO pin (MSB first). LED_TX flashes…, Send one byte (integer 0–255) MSB first., Send each character of a string as its ASCII byte., SerialTransmitter

### Community 79 - "firstexercise.py"
Cohesion: 0.48
Nodes (5): copy_to_storage_register(), reset_storage_register(), write_one_bit(), write_one_byte(), write_two_bytes()

### Community 80 - "RGBLed"
Cohesion: 0.29
Nodes (3): Common-anode RGB LED driven by three PWM channels. Because it's common-anode,…, Set color using 0–255 values per channel. Inverts to duty cycle for common-…, RGBLed

### Community 81 - "send_byte"
Cohesion: 0.38
Nodes (6): Send a single bit. 1 = HIGH 0 = LOW, Send a byte using: - 1 start bit - 8 data bits - 1 stop bit UART style…, Send all characters in a string., send_bit(), send_byte(), send_string()

### Community 82 - "uart_client.py"
Cohesion: 0.40
Nodes (5): UART Service ------------- An example showing how to write a simple program…, Slices *data* into chunks of size *n*. The last slice may be smaller than *n*., This is a simple "terminal" program that uses the Nordic Semiconductor (nRF)…, sliced(), uart_terminal()

### Community 83 - "steppermotorleft.py"
Cohesion: 0.47
Nodes (3): apply_step(), stepper_worker(), stop_stepper()

### Community 84 - "stppermotortight.py"
Cohesion: 0.47
Nodes (3): apply_step(), stepper_worker(), stop_stepper()

### Community 85 - "_handle"
Cohesion: 0.47
Nodes (5): _handle(), main(), Run a shell command in a completely detached child process. The delay gives the…, Dispatch a command string and return the response to send back., _run_detached()

### Community 86 - "pontentiometers.py"
Cohesion: 0.70
Nodes (4): map_adc_to_percent(), read_adc(), toggle_dc(), update_dc_motor()

### Community 89 - "angle_to_duty_cycle"
Cohesion: 0.50
Nodes (4): angle_to_duty_cycle(), Convert an angle (0 to 180 degrees) to the matching duty cycle for the servo.…, Move servo to the given angle., set_angle()

## Knowledge Gaps
- **9 isolated node(s):** `FailedException`, `InvalidValueLengthException`, `NotPermittedException`, `NotSupportedException`, `FailedException` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Characteristic` connect `Characteristic` to `assignment/ble/bluetooth_uart_server.py`, `BatteryLevelCharacteristic`, `TxCharacteristic`, `TestCharacteristic`, `assignment/ble/utils_gatt_server.py`, `CharacteristicUserDescriptionDescriptor`, `Descriptor`, `HeartRateMeasurementChrc`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `Characteristic` connect `Characteristic` to `BatteryLevelCharacteristic`, `HeartRateMeasurementChrc`, `ble_rpi/ble/utils_gatt_server.py`, `TestCharacteristic`, `Descriptor`, `ble_rpi/ble/bluetooth_uart_server.py`, `CharacteristicUserDescriptionDescriptor`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `ble_gatt_uart_loop()` connect `assignment/ble/bluetooth_uart_server.py` to `assignment/ble/utils_gatt_server.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Characteristic` (e.g. with `RxCharacteristic` and `TxCharacteristic`) actually correct?**
  _`Characteristic` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ADCReader` (e.g. with `main()` and `main()`) actually correct?**
  _`ADCReader` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `CSVLogger` (e.g. with `main()` and `main()`) actually correct?**
  _`CSVLogger` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ButtonToggle` (e.g. with `main()` and `main()`) actually correct?**
  _`ButtonToggle` has 2 INFERRED edges - model-reasoned connections that need verification._