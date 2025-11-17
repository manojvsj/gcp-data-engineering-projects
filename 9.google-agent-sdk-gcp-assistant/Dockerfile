# Use a small python base
FROM python:3.11-slim

WORKDIR /app

# Copy project
COPY . /app

# Install system deps if needed
RUN apt-get update && apt-get install -y gcc libpq-dev --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install python deps
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port used by Cloud Run
ENV PORT 8080

# Default command: run ADK web UI on 0.0.0.0:$PORT
# Run from parent directory so ADK can discover agent package 'agent'
CMD ["sh", "-c", "adk web --host 0.0.0.0 --port ${PORT}"]
