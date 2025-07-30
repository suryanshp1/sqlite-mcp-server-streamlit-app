FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY data/ ./data/

# Expose ports
EXPOSE 8501 3001

# Start script
COPY start.sh .
RUN dos2unix start.sh
RUN chmod +x start.sh

CMD ["bash", "./start.sh"]
