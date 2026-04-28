# Thin compatibility shim so all hardware modules import GPIO from one place.
#
# Locally:  RPi.GPIO talks to the kernel GPIO driver directly.
# In Docker: rpi-lgpio provides the exact same RPi.GPIO API but uses lgpio
#            underneath, which works without /proc/device-tree being present.
# Either way, the import below resolves to the same surface — no code changes needed.

import RPi.GPIO as GPIO

__all__ = ["GPIO"]
