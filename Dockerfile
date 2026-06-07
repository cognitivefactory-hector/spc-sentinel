FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install deps first so the layer caches across code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run as a non-root user.
RUN useradd --create-home --uid 10001 appuser
USER appuser

# Render (and most PaaS) inject $PORT; fall back to 8000 for local `docker run`.
ENV PORT=8000
EXPOSE 8000

# Shell form so ${PORT} expands. Daphne is the ASGI server (Channels).
CMD daphne -b 0.0.0.0 -p ${PORT} config.asgi:application
