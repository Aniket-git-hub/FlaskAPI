# docker/celery/Dockerfile

FROM python:3.11-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install NVIDIA CUDA Toolkit (example for CUDA 11.8, adjust as needed)
# RUN curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/debian10/x86_64/cuda-keyring_1.0-1_all.deb | dpkg -i -
# RUN apt-get update && apt-get install -y cuda-toolkit-11-8

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user and set permissions
RUN addgroup --system celery && adduser --system --group celery
RUN chown -R celery:celery /app

COPY . .

RUN mkdir -p /app/uploads && chmod 777 /app/uploads

CMD ["celery", "-A", "app.celery", "worker", "--concurrency=12"]
