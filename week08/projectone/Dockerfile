FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir rpi-lgpio smbus2 gradio

COPY hardware/   /app/hardware/
COPY interface/  /app/interface/
COPY main.py     /app/main.py

# Needed so "from hardware.*" and "from interface.*" resolve correctly
ENV PYTHONPATH=/app

CMD ["python", "/app/main.py"]
