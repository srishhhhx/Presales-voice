# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

# Install system deps for audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./src/
COPY config/ ./config/
COPY .env.example .env.example

# Create writable logs directory
RUN mkdir -p logs

# Expose LiveKit worker HTTP port (health check)
EXPOSE 8080

ENTRYPOINT ["python", "src/main.py", "start"]
