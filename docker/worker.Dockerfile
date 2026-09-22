FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ poppler-utils tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY workers ./workers
COPY backend ./backend

RUN mkdir -p /app/data /app/models /app/evaluation /app/logs

CMD ["python", "workers/worker.py"]