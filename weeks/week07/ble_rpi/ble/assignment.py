"""Compatibility launcher for the complete BLE motor assignment."""

from pathlib import Path
import runpy
import sys


# The complete assignment lives one directory above this helper folder. Add
# that directory so its ``ble`` package import resolves, then execute it.
BLE_RPI_DIR = Path(__file__).resolve().parents[1]
if str(BLE_RPI_DIR) not in sys.path:
    sys.path.insert(0, str(BLE_RPI_DIR))


if __name__ == "__main__":
    runpy.run_path(str(BLE_RPI_DIR / "assignment.py"), run_name="__main__")
