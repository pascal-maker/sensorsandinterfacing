from RPi import GPIO # import GPIO library
import smbus # import smbus library for I2C communication
import time # import time library for delays
import csv # import csv library for saving data
import os # import os library for folders and paths
from datetime import datetime # import datetime library for timestamps

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib") # set writable matplotlib config folder

import matplotlib # import matplotlib for graph saving
matplotlib.use("Agg") # use non-screen backend for Raspberry Pi
import matplotlib.pyplot as plt # import pyplot for plotting
import matplotlib.dates as mdates # import date formatting for graph x-axis

# GPIO Setup
GPIO.setmode(GPIO.BCM) # set the GPIO mode to BCM
GPIO.setwarnings(False) # disable GPIO warnings

# ADS7830 ADC Configuration
ADC_ADDR = 0x48 # ADC I2C address
ADC_CHANNEL = 4 # potentiometer connected to ADC channel 4
ADC_COMMANDS = [0x84, 0xC4, 0x94, 0xD4, 0xA4, 0xE4, 0xB4, 0xF4] # ADS7830 commands for channels 0-7

# Shift Register Pins
DATA_PIN = 22 # shift register data pin
CLOCK_PIN = 17 # shift register clock pin
LATCH_PIN = 27 # shift register latch pin

# Button Pin
BUTTON_PIN = 20 # button pin for toggling the LED matrix

# Timing
SAMPLE_INTERVAL = 1 # read potentiometer every 1 second
SHIFT_DELAY = 0.001 # delay for shift register bit timing
ROW_DELAY = 0.002 # delay for LED matrix row scanning

# Data Files
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # folder of this script
DATA_DIR = os.path.join(BASE_DIR, "data") # data folder inside praticalexam2
CSV_PATH = os.path.join(DATA_DIR, "potentiometer_log.csv") # csv output path
PLOT_PATH = os.path.join(DATA_DIR, "potentiometer_timing.png") # graph output path

# I2C Bus
i2c = smbus.SMBus(1) # initialize I2C bus 1

# GPIO Pin Setup
GPIO.setup(DATA_PIN, GPIO.OUT) # setup shift register data pin as output
GPIO.setup(CLOCK_PIN, GPIO.OUT) # setup shift register clock pin as output
GPIO.setup(LATCH_PIN, GPIO.OUT) # setup shift register latch pin as output
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # setup button as input with pull-up

# Program State
matrix_active = True # button toggles the matrix on or off
matrix_data = [0x00] * 8 # 8 rows of matrix data
scroll_buffer = [0x00] * 8 # 8 columns of potentiometer history
logged_times = [] # timestamps for graph
logged_values = [] # potentiometer values for graph
csv_file = None # csv file object
csv_writer = None # csv writer object


def read_adc(channel): # read one ADC channel
    """Read one ADS7830 channel and return a value from 0 to 255."""
    if not 0 <= channel <= 7: # check if channel is valid
        raise ValueError("ADC channel must be between 0 and 7") # raise error for wrong channel
    return i2c.read_byte_data(ADC_ADDR, ADC_COMMANDS[channel]) # send command and read value


def shift_byte_out(byte, msb_first=True): # shift out one byte
    """Send 8 bits to the shift register."""
    bits = range(7, -1, -1) if msb_first else range(8) # choose bit order
    for bit_position in bits: # loop through all bits
        bit = (byte >> bit_position) & 0x01 # get the current bit
        GPIO.output(DATA_PIN, bit) # write bit to data pin
        GPIO.output(CLOCK_PIN, GPIO.HIGH) # pulse clock high
        time.sleep(SHIFT_DELAY) # wait for stable signal
        GPIO.output(CLOCK_PIN, GPIO.LOW) # pulse clock low
        time.sleep(SHIFT_DELAY) # wait for stable signal


def shift_out_16bit(value, msb_first=False): # shift out 16-bit value
    """Send 16 bits to two chained shift registers."""
    high_byte = (value >> 8) & 0xFF # get upper 8 bits
    low_byte = value & 0xFF # get lower 8 bits

    GPIO.output(LATCH_PIN, GPIO.LOW) # lower latch before shifting
    if msb_first: # send high byte first if msb_first is true
        shift_byte_out(high_byte, msb_first)
        shift_byte_out(low_byte, msb_first)
    else: # send low byte first for this matrix wiring
        shift_byte_out(low_byte, msb_first)
        shift_byte_out(high_byte, msb_first)
    GPIO.output(LATCH_PIN, GPIO.HIGH) # raise latch to show outputs
    time.sleep(SHIFT_DELAY) # wait after latch


def draw_matrix(): # draw current matrix data
    """Scan all 8 matrix rows once."""
    for row in range(8): # loop through rows
        row_selector = 1 << row # select one row
        col_data = matrix_data[row] # get column bits for this row
        value = (row_selector << 8) | (~col_data & 0xFF) # combine row and inverted columns
        shift_out_16bit(value, msb_first=False) # send row data to shift registers
        time.sleep(ROW_DELAY) # small delay so row is visible


def clear_matrix(): # clear the matrix
    """Turn all matrix LEDs off."""
    global matrix_data, scroll_buffer
    matrix_data = [0x00] * 8 # clear row data
    scroll_buffer = [0x00] * 8 # clear history data
    draw_matrix() # update physical matrix


def potentiometer_to_column(raw_value): # convert ADC value to one matrix column
    """Convert a 0-255 potentiometer value to a vertical LED column."""
    filled_leds = round((raw_value / 255.0) * 8) # calculate number of LEDs to turn on
    if filled_leds <= 0: # no LEDs for very low value
        return 0x00
    return (1 << filled_leds) - 1 # bottom LEDs on, example 4 LEDs is 00001111


def update_matrix_from_scroll_buffer(): # convert column history into matrix rows
    """Convert the 8 column values in scroll_buffer into 8 matrix rows."""
    for row in range(8): # loop through matrix rows
        row_byte = 0 # start with empty row
        for col in range(8): # loop through matrix columns
            column_pattern = scroll_buffer[col] # get column pattern
            bit_position = 7 - row # row 0 is top, row 7 is bottom
            if column_pattern & (1 << bit_position): # check if LED should be on
                row_byte |= 1 << col # turn on the column bit for this row
        matrix_data[row] = row_byte # store the row byte


def add_value_to_matrix(raw_value): # add new value to scrolling matrix
    """Shift old values left and add the newest value on the right."""
    scroll_buffer.pop(0) # remove oldest value from the left
    scroll_buffer.append(potentiometer_to_column(raw_value)) # add newest value on the right
    update_matrix_from_scroll_buffer() # rebuild matrix rows


def button_callback(channel): # handle button press
    """Toggle the matrix on or off when the button is pressed."""
    global matrix_active
    matrix_active = not matrix_active # switch matrix state
    if not matrix_active: # if matrix is off
        clear_matrix() # turn all LEDs off
    print(f"Matrix {'ON' if matrix_active else 'OFF'}") # print current state


def setup_csv(): # setup csv logging
    """Create data folder and open CSV file."""
    global csv_file, csv_writer
    os.makedirs(DATA_DIR, exist_ok=True) # create data folder if needed
    file_is_new = not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0 # check if header is needed
    csv_file = open(CSV_PATH, "a", newline="", encoding="utf-8") # open csv in append mode
    csv_writer = csv.writer(csv_file) # create csv writer
    if file_is_new: # write header only for new file
        csv_writer.writerow(["Timestamp", "Potentiometer Value (0-255)"]) # write csv header
        csv_file.flush() # save header immediately


def log_value(raw_value): # log value to csv
    """Write one reading to CSV and flush immediately."""
    timestamp = datetime.now().strftime("%H:%M:%S") # create readable timestamp
    csv_writer.writerow([timestamp, raw_value]) # write timestamp and value
    csv_file.flush() # flush immediately so data is not lost


def save_graph(): # save graph on exit
    """Save a PNG graph of the recorded potentiometer values."""
    if not logged_values: # do nothing if no values were recorded
        return

    fig, ax = plt.subplots(figsize=(8, 4)) # create graph
    ax.plot(logged_times, logged_values, marker="o", linestyle="-", color="b", label="Potentiometer value") # plot values
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S")) # format x-axis time
    fig.autofmt_xdate() # rotate date labels
    ax.set_xlabel("Time") # x-axis label
    ax.set_ylabel("Potentiometer value (0-255)") # y-axis label
    ax.set_title("Potentiometer values over time") # graph title
    ax.legend() # show legend
    plt.tight_layout() # fix spacing
    plt.savefig(PLOT_PATH) # save graph
    plt.close(fig) # close graph
    print(f"Graph saved: {PLOT_PATH}") # print graph path


def cleanup(): # cleanup hardware and files
    """Clean up GPIO, I2C, and file resources."""
    if csv_file is not None: # close csv file if open
        csv_file.flush() # flush last data
        csv_file.close() # close file
    try:
        shift_out_16bit(0x0000, msb_first=False) # turn off matrix outputs
    except Exception:
        pass # ignore cleanup errors
    i2c.close() # close I2C bus
    GPIO.cleanup() # cleanup GPIO pins
    print("GPIO cleaned up.") # print cleanup message


# Setup button callback
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300) # detect button press

# Setup CSV file
setup_csv() # prepare csv logging

print("Program started. Press Ctrl+C to stop.") # startup message
print(f"Potentiometer: ADS7830 channel {ADC_CHANNEL}") # print potentiometer channel
print(f"Button on GPIO {BUTTON_PIN}: toggle matrix on/off") # print button pin

try:
    while True: # main loop
        raw = read_adc(ADC_CHANNEL) # read potentiometer value
        log_value(raw) # save value to csv
        logged_times.append(datetime.now()) # store time for graph
        logged_values.append(raw) # store value for graph

        if matrix_active: # only update display when matrix is active
            add_value_to_matrix(raw) # add newest value to matrix history
            draw_matrix() # update LED matrix

        time.sleep(SAMPLE_INTERVAL) # wait 1 second before next reading

except KeyboardInterrupt:
    print("\nProgram stopped by user.") # print stop message

finally:
    save_graph() # save graph before exit
    cleanup() # cleanup hardware
