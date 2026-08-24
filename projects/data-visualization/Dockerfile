FROM python:3.12-slim

# Build tools needed by some pip packages (e.g. rpi-lgpio native extension)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# rpi-lgpio is a drop-in RPi.GPIO replacement that uses lgpio under the hood,
# which works inside Docker without the /proc/device-tree filesystem.
RUN pip install --no-cache-dir \
    rpi-lgpio \
    smbus2 \
    gradio

COPY . /app/interface/

# Default; docker-compose overrides this with explicit command
CMD ["python", "/app/interface/main.py"]
