import time


class AutoOffTimer:
    """Maps a potentiometer value to an optional auto-off deadline."""

    def __init__(self, minimum=5, middle=30, maximum=60, manual_threshold=250):
        self.minimum = minimum
        self.middle = middle
        self.maximum = maximum
        self.manual_threshold = manual_threshold
        self.seconds = minimum
        self.deadline = None

    def update_from_raw(self, raw_value):
        self.seconds = self.raw_to_seconds(raw_value)
        return self.seconds

    def raw_to_seconds(self, raw_value):
        if raw_value >= self.manual_threshold:
            return None

        if raw_value <= 128:
            return self.minimum + (raw_value / 128) * (self.middle - self.minimum)

        scale = (raw_value - 128) / (self.manual_threshold - 128)
        return self.middle + scale * (self.maximum - self.middle)

    def start(self):
        self.deadline = None if self.seconds is None else time.time() + self.seconds

    def cancel(self):
        self.deadline = None

    def expired(self):
        return self.deadline is not None and time.time() >= self.deadline

    def label(self):
        return "manual" if self.seconds is None else f"{self.seconds:.1f}s"
