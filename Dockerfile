# Multi-stage production container for Helper-AI
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final runtime image
FROM python:3.11-slim

LABEL maintainer="Helper-AI Contributors"
LABEL description="Autonomous AI Agent with PC & Internet Control"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH" \
    PORT=8000 \
    HOST=0.0.0.0

WORKDIR /app

# Install lightweight runtime libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application source code
COPY . /app

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/status')" || exit 1

EXPOSE 8000 3000

CMD ["python", "app.py"]
