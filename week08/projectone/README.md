# Week 8 Project 1 — GPIO Data Visualization Dashboard

A browser-based dashboard built with **Gradio** that monitors and controls three GPIO components on a Raspberry Pi in real time. Runs locally or inside Docker and is reachable from any device on the same network.

---

## Hardware Components

| Component | GPIO Pin | Protocol |
|-----------|----------|----------|
| Push Button | GPIO 26 | Digital IN (pull-up) |
| Active Buzzer | GPIO 12 | Digital OUT |
| Passive Buzzer | GPIO 14 | PWM OUT |
| 16x2 LCD Display | SDA / SCL | I2C (address `0x27`) |

**Wiring notes:**
- Button uses a pull-up resistor — pressing pulls the line LOW.
- Active buzzer has its own oscillator; just switch it HIGH/LOW.
- Passive buzzer needs PWM to generate a tone — frequency and duty cycle control pitch and volume.
- LCD uses an HD44780 controller behind a PCF8574 I2C backpack (standard Freenove kit LCD).

---

## Project Structure

```
projectone/
├── main.py                        # Gradio entry point — composes all tabs
│
├── interface/                     # Gradio UI layer
│   └── pages/
│       ├── button.py              # Live button state tab (100 ms polling)
│       ├── buzzer.py              # Active + Passive buzzer control tabs
│       ├── lcd.py                 # LCD text input tab
│       └── system.py             # System control tab (reboot/shutdown via daemon)
│
├── hardware/                      # GPIO driver layer
│   ├── basic_button.py            # ButtonService — debounced digital input
│   ├── basic_buzzer.py            # ActiveBuzzerService + PassiveBuzzerService
│   ├── basic_lcd.py               # LCDService — HD44780 over I2C
│   └── gpio_compat.py             # RPi.GPIO / rpi-lgpio compatibility shim
│
├── daemon/                        # Host-side control daemon
│   ├── freenove_control_daemon.py # Unix socket server — executes systemctl commands
│   └── setup_sudoers.sh           # One-time sudoers setup for the daemon
│
├── deploy/                        # Systemd service units
│   ├── gradio-demo.service        # Runs the Docker Compose app as a service
│   └── freenove-control.service   # Runs the host daemon as a service
│
├── Dockerfile                     # Container image (uses rpi-lgpio for Docker GPIO)
├── docker-compose.yml             # Compose config — mounts GPIO devices and socket
├── .dockerignore
│
└── (see /datavisualization/ at repo root for the older monolithic version)
```

---

## Running Locally (no Docker)

Install dependencies once:

```bash
pip install gradio smbus2 RPi.GPIO
```

Start the dashboard:

```bash
cd week08/projectone
python3 main.py
```

Open `http://<pi-ip-address>:7860` in a browser.

Override default pins with environment variables:

```bash
FREENOVE_BUTTON_PIN=26 \
FREENOVE_ACTIVE_BUZZER_PIN=12 \
FREENOVE_PASSIVE_BUZZER_PIN=14 \
FREENOVE_LCD_ADDR=0x27 \
python3 main.py
```

---

## Running with Docker

Docker uses `rpi-lgpio` instead of `RPi.GPIO` — same API, but works inside a container using `/dev/gpiochip0` directly instead of `/proc/device-tree`.

### Build and start

```bash
cd week08/projectone
sudo docker compose up --build
```

First build takes ~2–3 minutes (downloads base image, installs deps). Subsequent starts are fast.

### Stop

```bash
sudo docker compose down
```

### View logs

```bash
sudo docker compose logs -f
```

### Docker environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `RPI_LGPIO_CHIP` | `0` | GPIO chip (`/dev/gpiochip0`) |
| `RPI_LGPIO_REVISION` | `00c04171` | Board revision (required when `/proc/device-tree` is missing in Docker) |
| `GRADIO_SERVER_PORT` | `7860` | Web UI port |

---

## System Control Tab & Daemon

The **System** tab in the dashboard (Reboot, Shutdown, Restart Service) cannot call `systemctl` directly from inside Docker. Instead:

1. A small daemon (`daemon/freenove_control_daemon.py`) runs **on the host**, managed by `freenove-control.service`.
2. The daemon listens on a Unix socket (`/run/freenove-control/control.sock`).
3. The container sends a command string over the socket; the daemon executes the system action.
4. The socket directory is bind-mounted into the container via `docker-compose.yml`.

Supported socket commands: `PING`, `REBOOT`, `SHUTDOWN`, `SERVICE_STOP`, `SERVICE_RESTART`.

### Start the daemon manually (without systemd)

```bash
sudo python3 daemon/freenove_control_daemon.py
```

---

## Dashboard Tabs

### Button
Polls GPIO 26 every 100 ms and shows live state (**Pressed** / **Released**) and raw GPIO level (**LOW** / **HIGH**). Software debouncing (50 ms window) filters noise.

### Active Buzzer
ON / OFF toggle and a timed Beep button with adjustable duration (0.05–2.0 s). The active buzzer has its own oscillator so no PWM is needed.

### Passive Buzzer
Three sliders:
- **Frequency** (100–4000 Hz) — pitch
- **Duration** (0.1–3.0 s) — how long it plays
- **Duty Cycle** (1–99%) — volume / drive strength

### LCD
Two text inputs (max 16 chars each) sent to the 16×2 display over I2C. Includes a Clear button.

### System
Sends commands to the host daemon: **Ping** (health check), **Restart Service**, **Reboot Pi**, **Shutdown Pi**.

---

## Key Concepts Demonstrated

| Concept | Where |
|---------|-------|
| Pull-up digital input | `hardware/basic_button.py` — HIGH by default, LOW when pressed |
| Software debouncing | `hardware/basic_button.py` — 50 ms stable-state window |
| PWM tone generation | `hardware/basic_buzzer.py` — `RPi.GPIO.PWM` adjusts frequency and duty cycle |
| I2C protocol | `hardware/basic_lcd.py` — 4-bit nibbles sent over I2C to a PCF8574 port expander |
| Gradio Blocks + Timer | `interface/pages/` — `gr.Timer` drives server-side polling without custom JS |
| Docker GPIO access | `Dockerfile` / `docker-compose.yml` — `rpi-lgpio` + `/dev/gpiochip0` device mount |
| Unix socket IPC | `daemon/freenove_control_daemon.py` — container-to-host command bridge |
| Systemd service units | `deploy/` — runs the app and daemon as managed system services |
