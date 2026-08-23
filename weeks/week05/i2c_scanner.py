"""List devices detected on the Raspberry Pi I2C bus."""

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus


def scan_i2c_bus(bus_id=1, first_address=0x03, last_address=0x77):
    """Return the valid I2C addresses that acknowledge a request."""
    bus = SMBus(bus_id)
    found = []
    try:
        for address in range(first_address, last_address + 1):
            try:
                bus.write_quick(address)
            except OSError:
                continue
            found.append(address)
    finally:
        bus.close()
    return found


if __name__ == "__main__":
    devices = scan_i2c_bus()
    if devices:
        print("I2C devices:", ", ".join(f"0x{address:02X}" for address in devices))
    else:
        print("No I2C devices found")
