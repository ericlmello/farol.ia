FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# libs que o Playwright/Chromium costuma precisar
RUN apt-get update && apt-get install -y \
    fontconfig fonts-liberation libnss3 libnspr4 libdbus-1-3 \
    libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libasound2 \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# curl p/ healthcheck (usado no compose)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Instala o Chromium do Playwright
RUN playwright install chromium

COPY app.py /app/app.py
COPY templates /app/templates
COPY static /app/static

RUN useradd -m appuser
USER appuser

EXPOSE 8000

# Sem HEALTHCHECK aqui; faremos no compose.
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
