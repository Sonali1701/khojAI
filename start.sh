#!/bin/bash

# Render startup script for Age Progression App
echo "Starting Age Progression App deployment..."

# Set environment variables
export PYTHONPATH=$PYTHONPATH:/app
export FLASK_ENV=production
export UPLOAD_FOLDER=/tmp/uploads

# Create necessary directories
mkdir -p /tmp/uploads
mkdir -p /tmp/uploads/found
mkdir -p /tmp/uploads/missing
mkdir -p /tmp/static/uploads

# Copy static files if they exist
if [ -d "/app/static" ]; then
    cp -r /app/static/* /tmp/static/ 2>/dev/null || true
fi

# Download Fast-AgingGAN model if not present
if [ ! -d "/app/Fast-AgingGAN" ]; then
    echo "Downloading Fast-AgingGAN model..."
    git clone https://github.com/HasnainRaz/Fast-AgingGAN.git /app/Fast-AgingGAN
fi

# Verify model files exist
if [ ! -f "/app/Fast-AgingGAN/pretrained_model/state_dict.pth" ]; then
    echo "Error: Fast-AgingGAN model weights not found!"
    exit 1
fi

echo "Startup completed. Starting application..."
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
