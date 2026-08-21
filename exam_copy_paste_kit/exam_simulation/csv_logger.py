import csv
import os
import time
from pathlib import Path


class CSVLogger:
    def __init__(self, filename, headers):
        path = Path(filename)
        if not path.is_absolute():
            path = Path(__import__("__main__").__file__).resolve().parent / path

        self.path = path
        self.file = self.path.open("a", newline="")
        self.writer = csv.writer(self.file)

        if self.path.stat().st_size == 0:
            self.writer.writerow(headers)
            self.flush()

    def write(self, *values):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.writer.writerow([timestamp, *values])
        self.flush()

    def flush(self):
        self.file.flush()
        os.fsync(self.file.fileno())

    def close(self):
        self.file.close()
