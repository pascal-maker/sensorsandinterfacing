# Sensors and Interfacing

Raspberry Pi coursework, hardware experiments, assignments, and exam-preparation material for a Sensors and Interfacing module.

## Start here

- Browse the weekly labs in [`weeks/`](weeks/).
- Open the graded and larger applications in [`projects/`](projects/).
- Use the practical exams, retake material, and reusable snippets in [`exams/`](exams/).
- Read exam notes in [`docs/exams/`](docs/exams/).

Most programs access Raspberry Pi GPIO or I2C hardware directly. Run them on a configured Raspberry Pi unless a project README says that simulation is supported.

## Repository layout

```text
.
├── weeks/                         Weekly labs, consistently numbered
│   ├── week01/                    GPIO basics
│   ├── week02/                    Buttons, edge detection, logging
│   ├── week03/                    BCD and bit manipulation
│   ├── week04/                    ADC, PWM, and joystick input
│   ├── week05/                    Communication and servo control
│   ├── week06/                    MPU-6050 exercises
│   ├── week07/                    Motors and Bluetooth LE
│   ├── week08/                    Shift registers and buzzer project
│   ├── week09/                    Displays, keypad, and LED matrix
│   └── week11/                    RFID and camera exercises
├── projects/
│   ├── course-assignment/         Multi-screen LCD assignment
│   └── data-visualization/        Dockerized hardware dashboard
├── exams/
│   ├── practice/                  Practical exam exercises
│   ├── sandi-retake/              Khalil Ahmad retake files
│   ├── copy-paste-kit/            Reusable exam components/examples
│   └── bcd-7segment-auto-off-logger/
├── docs/exams/                    Exam Q&A and retake notes
├── main.py                        Legacy combined hardware demo
├── mpu6050.py                     Standalone MPU-6050 driver
└── temperature.py                 Standalone temperature example
```

Week 10 is not present in the current course material.

## Exam resources

The [`exams/copy-paste-kit/README.md`](exams/copy-paste-kit/README.md) explains the small reusable modules for ADC input, buttons, CSV logging, joysticks, LED matrices, shift registers, and seven-segment displays. Complete examples are under [`exams/copy-paste-kit/examples/`](exams/copy-paste-kit/examples/).

The retake supplied from the upstream repository is in [`exams/sandi-retake/`](exams/sandi-retake/), including `KhalilAhmadRetake.py`, LED-matrix and shift-register helpers, and sample potentiometer data.

## Projects

Each larger project keeps its own instructions:

- [`projects/data-visualization/README.md`](projects/data-visualization/README.md)
- [`weeks/week08/projectone/README.md`](weeks/week08/projectone/README.md)

The course assignment is in [`projects/course-assignment/`](projects/course-assignment/). Its scripts are designed to be run from that directory because several imports are local to the project.

## Basic setup

Enable the interfaces required by the exercise through `raspi-config`, then install the dependencies used by that exercise. Common dependencies include:

```bash
python -m pip install smbus2 RPi.GPIO
```

Some folders need additional packages such as OpenCV, Gradio, Matplotlib, or Bluetooth libraries. Check the nearest README or imports before running a script.

## Notes

- GPIO pin assignments vary by exercise. Review the constants near the top of a script before connecting hardware.
- Data files and captured media are retained when they support an exercise.
- Generated Python caches, editor metadata, operating-system metadata, and temporary office lock files are ignored.
- `main.py` is a legacy combined demo. Its `BCDReader` dependency is not present in the current repository, so the weekly and project entry points are the reliable starting points.

## Author

**pascal-maker** — Raspberry Pi, Python, and embedded systems coursework.
