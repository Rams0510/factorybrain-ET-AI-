FROM python:3.11-slim

# System deps: tesseract for OCR, opencv runtime libs, mysql client headers
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    libglib2.0-0 \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# pip's default resolver fetches large package-index JSON in one shot;
# on flaky/proxied/VPN connections (common on Windows+Docker Desktop) that
# download can get truncated mid-stream. --retries and a longer timeout
# make it self-heal instead of failing the whole build.
ENV PIP_DEFAULT_TIMEOUT=100
COPY requirements.txt .

# Install the large/binary-heavy packages first, in their own layer, so a
# transient network failure only needs to retry this step, not the rest.
RUN pip install --no-cache-dir --retries 10 --timeout 100 \
    opencv-python-headless==4.10.0.84 \
    pandas==2.2.3 \
    chromadb==0.5.5 \
    pymupdf==1.24.10

RUN pip install --no-cache-dir --retries 10 --timeout 100 -r requirements.txt

COPY . .

RUN mkdir -p /app/storage/uploads /app/secrets

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
