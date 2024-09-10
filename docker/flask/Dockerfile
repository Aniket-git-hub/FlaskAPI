# docker/flask/Dockerfile

FROM python:3.11-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
    curl \
    libglib2.0-0 \
    imagemagick \
    libsm6 \
    ffmpeg \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# # Install NVIDIA CUDA Toolkit (example for CUDA 11.8, adjust as needed)
# RUN curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/debian10/x86_64/cuda-keyring_1.0-1_all.deb | dpkg -i -
# RUN apt-get update && apt-get install -y cuda-toolkit-11-8

COPY policy.xml /etc/ImageMagick-6/policy.xml

# Upgrade pip and install requirements
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --timeout=120 --no-cache-dir -r requirements.txt

WORKDIR /app

COPY . .

RUN mkdir -p /app/uploads /app/logos /app/processed_videos && \
    chmod 777 /app/uploads /app/logos /app/processed_videos

EXPOSE 8000

CMD ["gunicorn", "app:create_app()", "-b", "0.0.0.0:8000", "-w", "4"]
