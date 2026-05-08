import time
from shift_register import ShiftRegister

class LedMatrix8x8:
    # 0.5 ms pause between rows — gives the shift register time to latch
    # each row before the next one is sent
    ROW_DELAY = 0.0005

    def __init__(self, shift_register):
        self.shift_register = shift_register
        # row_data holds the pixel state for all 8 rows.
        # Each byte represents one row: bit x = 1 means pixel at column x is on.
        self.row_data = [0x00] * 8

    def toggle_pixel(self, x, y):
        # XOR flips bit x in row y — turns the pixel on if it was off, off if it was on,
        # without touching any other pixels in that row
        self.row_data[y] ^= (1 << x)

    def get_pixel(self, x, y):
        # Shift row byte right by x so bit x lands at position 0, then mask with 1
        # to read just that bit. Returns 1 if on, 0 if off.
        return (self.row_data[y] >> x) & 1

    def clear(self):
        # Reset all 8 row bytes to 0x00 — every pixel off
        self.row_data = [0x00] * 8

    def refresh_once(self, cursor_x=None, cursor_y=None, cursor_visible=False):
        # Row scanning: drive one row at a time, cycling through all 8.
        # The rows switch fast enough that the eye sees the full matrix lit at once.
        for row in range(8):
            row_byte = 1 << row           # selects which row to activate (one bit set)
            col_byte = self.row_data[row] # pixel on/off data for this row

            # Cursor overlay: XOR the cursor's column bit into this row's data.
            # This makes the cursor blink on top of existing pixel state — it doesn't overwrite it.
            if cursor_visible and cursor_y == row:
                col_byte ^= (1 << cursor_x)

            # Invert columns — the matrix hardware uses active-low column logic,
            # so all bits must be flipped before sending
            col_byte = ~col_byte & 0xFF

            # Pack into a 16-bit value: high byte = column data, low byte = row select.
            # Both are sent together in one shift register write.
            value = (col_byte << 8) | row_byte

            # Alternative if the display appears mirrored or wrong:
            # value = (row_byte << 8) | col_byte

            # LSB_TO_MSB matches the bit order of this matrix's wiring
            self.shift_register.shift_out_16bit(
                value,
                direction=ShiftRegister.LSB_TO_MSB
            )

            time.sleep(self.ROW_DELAY)

    def blank(self):
        # 0x00FF → high byte 0x00 (all columns off after inversion logic),
        # low byte 0xFF (no specific row selected) — turns the whole display dark
        self.shift_register.shift_out_16bit(
            0x00FF,
            direction=ShiftRegister.LSB_TO_MSB
        )