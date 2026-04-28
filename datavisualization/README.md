# Data Visualization — Monolithic GPIO Dashboard

An earlier, single-file version of the GPIO dashboard. All services and the Gradio UI live in one `main.py` for simplicity.

The refactored version with separate `hardware/`, `interface/`, `daemon/`, and `deploy/` layers is in `week08/projectone/`.

---

## Files

| File | Purpose |
|------|---------|
| `main.py` | Single-file Gradio dashboard (Button, Active Buzzer, Passive Buzzer, LCD tabs) |
| `buttonservice.py` | `ButtonService` — debounced GPIO digital input |
| `buzzerservice.py` | `ActiveBuzzerService` + `PassiveBuzzerService` — GPIO buzzer drivers |
| `lcdservice.py` | `LCDService` — HD44780 16×2 LCD over I2C |
| `gpio_compat.py` | `RPi.GPIO` / `rpi-lgpio` compatibility shim |
| `basicbutton.py` | Standalone single-tab button demo |
| `Dockerfile` | Container image |
| `docker-compose.yml` | Docker Compose config |

---

## Hardware

| Component | GPIO Pin | Protocol |
|-----------|----------|----------|
| Push Button | GPIO 26 | Digital IN (pull-up) |
| Active Buzzer | GPIO 12 | Digital OUT |
| Passive Buzzer | GPIO 14 | PWM OUT |
| 16x2 LCD | SDA / SCL | I2C (`0x27`) |

---

## Run locally

```bash
cd datavisualization
pip install gradio smbus2 RPi.GPIO
python3 main.py
```

Open `http://<pi-ip>:7860`.

## Run with Docker

```bash
cd datavisualization
sudo docker compose up --build
```
