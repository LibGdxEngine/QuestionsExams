# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app/

# Run migrations
RUN python manage.py makemigrations
RUN python manage.py migrate

# Expose the port the app runs on
EXPOSE 8000

# Create an entrypoint script
RUN echo '#!/bin/sh\n\
python manage.py makemigrations\n\
python manage.py migrate\n\
python manage.py runserver 0.0.0.0:8000' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
