# docker/celery/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install Python packages as root
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user and set permissions
RUN addgroup --system celery && adduser --system --group celery
RUN chown -R celery:celery /app

# Switch to non-root user
USER celery

COPY . .

CMD ["celery", "-A", "app.celery_worker:celery", "worker", "--concurrency=16"]
