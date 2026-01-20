FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    xz-utils \
    wget \
    fontconfig \
    libfreetype6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Download and install Calibre portable
RUN wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 10000

# Start Flask app with Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
