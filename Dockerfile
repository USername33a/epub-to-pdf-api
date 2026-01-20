# Use full Debian image instead of slim
FROM debian:bookworm-slim

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    xz-utils \
    fontconfig \
    libfreetype6 \
    libxrender1 \
    libjpeg62-turbo \
    libpng16-16 \
    && rm -rf /var/lib/apt/lists/*

# Install Calibre from official binary
RUN wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 10000

# Start Flask app with Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
