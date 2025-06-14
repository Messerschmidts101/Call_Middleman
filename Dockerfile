FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --upgrade pip && \
    pip install --prefer-binary --timeout=100 --retries=10 -r requirements.txt

# Expose the HTTPS port
EXPOSE 8000

# Run server with Flask-SocketIO and SSL
CMD ["python", "server.py"]
