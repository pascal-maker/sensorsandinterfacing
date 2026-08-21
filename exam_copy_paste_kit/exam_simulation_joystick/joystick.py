class Joystick:
    def __init__(self, adc, x_channel=6, y_channel=5, low=80, high=180):
        self.adc = adc
        self.x_channel = x_channel
        self.y_channel = y_channel
        self.low = low
        self.high = high

    def read(self):
        return self.adc.read(self.x_channel), self.adc.read(self.y_channel)

    def direction(self):
        x_value, y_value = self.read()

        if x_value < self.low:
            return "LEFT", x_value, y_value
        if x_value > self.high:
            return "RIGHT", x_value, y_value
        if y_value < self.low:
            return "DOWN", x_value, y_value
        if y_value > self.high:
            return "UP", x_value, y_value
        return "CENTER", x_value, y_value

    @staticmethod
    def value_to_index(value, size=8):
        index = round((value / 255) * (size - 1))
        return max(0, min(size - 1, index))
