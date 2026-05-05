# Use a stable official Python runtime as a parent image
FROM python:3.12-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Create a non-root user and group
RUN addgroup -S django && adduser -S django -G django

# Install system dependencies
RUN set -ex && \
    apk add --no-cache --virtual .build-deps build-base postgresql-dev && \
    apk add --no-cache libpq && \
    python -m pip install --upgrade pip setuptools wheel && \
    apk del .build-deps

# Copy only requirements first to leverage Docker cache
COPY requirements.txt /app/

# Install Python dependencies as root (required for system-wide install)
RUN pip install --no-cache-dir --timeout 600 -r requirements.txt

# Copy project files
COPY . /app/

# Create directories for static and media and set ownership
RUN mkdir -p /app/staticfiles /app/media && \
    chown -R django:django /app

# Switch to the non-root user
USER django

# Expose port 8000
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "valve_project.wsgi:application"]
