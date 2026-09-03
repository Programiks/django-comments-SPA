# Dockerfile
# Docker configuration for Django comment system SPA

# Use official Python image (slim version for smaller size)
FROM python:3.12-slim

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevent Python from writing .pyc files
# PYTHONUNBUFFERED: Ensure Python logs are sent straight to terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for PostgreSQL and image processing
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into container
COPY . .

# Collect static files (optional, uncomment if using Django static files)
# RUN python manage.py collectstatic --noinput

# Expose port 8000 for Django development server
EXPOSE 8000

# Run Django development server (bind to 0.0.0.0 for external access)
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate --noinput && daphne -b 0.0.0.0 -p $PORT config.asgi:application"]
