ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860 \
    GRADIO_TEMP_DIR=/tmp/gradio \
    XDG_CACHE_HOME=/tmp/.cache \
    HF_HOME=/tmp/.cache/huggingface \
    PYTHONPATH=/app

WORKDIR /app

# gcc and libc6-dev are needed to build rpi-lgpio's native extension
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --link requirements.txt ./

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

COPY --link hardware/ ./hardware/
COPY --link interface/ ./interface/
COPY --link main.py ./

EXPOSE 7860

# Runs as root because rpi-lgpio needs ioctl access to /dev/gpiochipN.
# docker-compose sets working_dir=/tmp because rpi-lgpio creates .lgd-nfy*
# notification files in the current working directory.
CMD ["python", "/app/main.py"]
