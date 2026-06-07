FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install deps first so the layer caches across code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Daphne is the ASGI server (Channels). Bind all interfaces for the container.
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
