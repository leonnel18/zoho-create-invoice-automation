FROM python:3.11-slim

WORKDIR /app

# Install system build deps (needed by psycopg2-binary)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer cache)
COPY web/backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY web/backend/ web/backend/
COPY tools/ tools/

# Create data dirs
RUN mkdir -p data/users

EXPOSE 8000

CMD python -m uvicorn web.backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
