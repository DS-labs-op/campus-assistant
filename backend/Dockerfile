FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install CPU-only PyTorch first (much smaller than GPU version)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/logs data/chroma documents

# Make start script executable
RUN chmod +x start.sh

# Expose port (Railway uses dynamic PORT)
EXPOSE ${PORT:-8000}

# Run the application via start script
CMD ["./start.sh"]
