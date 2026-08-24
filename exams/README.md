# Exams

Exam material is grouped by exam type and named for the hardware task it assesses.

## Practical exams

| Exam | Topic | Main file |
|---|---|---|
| [Exam 1](practical/exam-01-motion-bomb-defusal/) | MPU-6050 motion-sensitive bomb defusal with LCD, buttons, RGB LED, and buzzer | `solution.py` |
| [Exam 2](practical/exam-02-potentiometer-matrix-logger/) | ADS7830 potentiometer logging, scrolling LED matrix, and saved graph | `solution.py` |
| [Exam 3](practical/exam-03-potentiometer-matrix-retake/) | Potentiometer history, CSV logging, LED matrix, and display toggle | `solution.py` |
| [Exam 4](practical/exam-04-bcd-seven-segment-auto-off-logger/) | BCD input, four-digit display, potentiometer auto-off, button, and CSV logging | `solution.py` |

Exam 3 is the former `KhalilAhmadRetake.py`. It was renamed by topic and refactored into a class-based application. The original sample data is preserved under its `data/` directory.

## Other material

- [`theory/`](theory/) contains study notes, a question bank, and bit-operation practice questions.
- [`copy_paste_kit/`](copy_paste_kit/) contains reusable hardware classes and small examples.

Practical Exam 4 is the complete self-contained class-based solution. The shorter
[`bcd_7seg_auto_off_logger.py`](copy_paste_kit/examples/bcd_7seg_auto_off_logger.py)
is intentionally retained as a composition example using the reusable kit classes.
