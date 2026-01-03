# Use an official Python runtime as a parent image
FROM python:3.14.2-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN set -ex && \
    apk add --no-cache --virtual .build-deps build-base postgresql-dev && \
    apk add --no-cache libpq && \
    python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --timeout 600 -r requirements.txt && \
    apk del .build-deps

# Copy project
COPY . /app/

# Expose port 8000
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "valve_project.wsgi:application"]
