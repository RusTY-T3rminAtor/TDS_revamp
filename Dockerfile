# Dockerfile - Debian slim + Python + Chromium for headless Selenium
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CHROME_BIN=/usr/bin/chromium
ENV PIP_NO_CACHE_DIR=1
ENV PORT=8080

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    ca-certificates \
    wget \
    curl \
    unzip \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    chromium \
    chromium-driver \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools
RUN pip install -r /app/requirements.txt

COPY . /app

EXPOSE ${PORT}

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--workers", "2", "--worker-class", "gthread"]
