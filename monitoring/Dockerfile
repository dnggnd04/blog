FROM python:3.11-slim

WORKDIR /app

# Cài các system deps cần thiết để gọi docker & đọc /proc
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl docker.io docker-compose-v2 \
    && rm -rf /var/lib/apt/lists/*

# Cài Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

EXPOSE 8080

# Chạy với 2 workers (monitoring service nhẹ, không cần nhiều)
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
