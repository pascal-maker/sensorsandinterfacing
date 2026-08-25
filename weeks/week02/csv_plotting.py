"""Reusable CSV storage and time-series plotting helpers."""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt


class CSVStorage:
    """Read and write rows in a CSV file with one consistent header."""

    def __init__(self, path, headers):
        self.path = Path(path)
        self.headers = list(headers)

    def _prepare_directory(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def overwrite(self, rows):
        """Replace the file with the supplied rows."""
        self._prepare_directory()
        with self.path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(self.headers)
            writer.writerows(rows)

    def append(self, rows):
        """Append rows, creating the file and header when necessary."""
        rows = list(rows)
        if not rows:
            return 0

        self._prepare_directory()
        needs_header = not self.path.exists() or self.path.stat().st_size == 0
        with self.path.open("a", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            if needs_header:
                writer.writerow(self.headers)
            writer.writerows(rows)
        return len(rows)

    def read_rows(self):
        """Return saved rows as dictionaries keyed by the header names."""
        if not self.path.exists() or self.path.stat().st_size == 0:
            return []
        with self.path.open("r", newline="", encoding="utf-8") as csv_file:
            return list(csv.DictReader(csv_file))

    def to_dataframe(self):
        """Return the CSV contents as a pandas DataFrame."""
        import pandas as pd

        if not self.path.exists() or self.path.stat().st_size == 0:
            return pd.DataFrame(columns=self.headers)
        return pd.read_csv(self.path)


class TimeSeriesPlotter:
    """Save line or step plots whose horizontal axis contains datetimes."""

    def __init__(self, title, x_label="Time", y_label="Value", figsize=(10, 4)):
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.figsize = figsize

    def save(
        self,
        path,
        times,
        values,
        *,
        style="line",
        y_ticks=None,
        color="steelblue",
    ):
        """Save a plot and return its path, or return None for empty data."""
        times = list(times)
        values = list(values)
        if not times or not values:
            return None
        if len(times) != len(values):
            raise ValueError("times and values must contain the same number of items")

        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        figure, axis = plt.subplots(figsize=self.figsize)
        if style == "line":
            axis.plot(times, values, marker="o", linewidth=1, color=color)
        elif style == "step":
            axis.step(times, values, where="post", marker="o", color=color)
        else:
            plt.close(figure)
            raise ValueError("style must be 'line' or 'step'")

        axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        axis.set_xlabel(self.x_label)
        axis.set_ylabel(self.y_label)
        axis.set_title(self.title)
        if y_ticks is not None:
            positions, labels = y_ticks
            axis.set_yticks(positions, labels)
        figure.autofmt_xdate()
        figure.tight_layout()
        figure.savefig(output_path)
        plt.close(figure)
        return str(output_path)
