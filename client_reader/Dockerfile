FROM python:3.12-alpine

# Install dependencies
RUN pip install pika
RUN apk add --no-cache bash

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create app directory
WORKDIR /app

# Create log directory
RUN mkdir -p /var/log/client_reader && \
    chmod -R 777 /var/log/client_reader

# Copy logging module
COPY ../log_utils /app/log_utils/

# Copy application files
COPY ./client_reader/client_reader_v2.py .

CMD ["python", "client_reader_v2.py"]