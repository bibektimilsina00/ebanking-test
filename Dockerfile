# Use an official Python runtime as a base image
FROM python:3.8-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends default-libmysqlclient-dev gcc pkg-config default-mysql-client \
    && rm -rf /var/lib/apt/lists/*



# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/
COPY entrypoint.sh /app/

# Collect static files

# Run entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]