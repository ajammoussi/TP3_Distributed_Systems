FROM python:3.12-alpine

# Install dependencies
RUN pip install pika
RUN apk add --no-cache bash

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO
ENV PYTHONPATH=/app

# Create app directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/data && \
    mkdir -p /var/log/replica && \
    chmod -R 777 /var/log/replica

# Copy logging module
COPY ../log_utils /app/log_utils/

# Copy application files
COPY ./replica/replica.py .

CMD ["python", "replica.py"]
