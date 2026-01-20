FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y calibre && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 10000

# Start app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
