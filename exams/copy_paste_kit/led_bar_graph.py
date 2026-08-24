class LedBarGraph:
    """LED bar graph through a 74HC595 chain."""

    def __init__(self, shift_register, led_count=10):
        self.shift_register = shift_register
        self.led_count = led_count

    def value_to_pattern(self, value, max_value=255):
        on_count = round((value / max_value) * self.led_count)
        on_count = max(0, min(self.led_count, on_count))
        return (1 << on_count) - 1 if on_count else 0

    def show_value(self, value, max_value=255):
        pattern = self.value_to_pattern(value, max_value)
        self.shift_register.write_16_bits(pattern)
        return pattern.bit_count()

    def clear(self):
        self.shift_register.write_16_bits(0x0000)
