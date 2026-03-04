#!/bin/bash
set -e  # Exit on error

echo "================================"
echo "Starting application deployment"
echo "================================"

# Check environment variables
echo "Checking environment variables..."
echo "PORT: ${PORT:-NOT SET}"
echo "DOCLING_MODEL_PATH: ${DOCLING_MODEL_PATH:-NOT SET}"
echo "DOCLING_MAX_WORKERS: ${DOCLING_MAX_WORKERS:-NOT SET}"

# Wait for storage mount (Azure Storage can take time to mount)
if [ ! -z "$DOCLING_MODEL_PATH" ]; then
    echo "Waiting for model path to be available..."
    MAX_WAIT=60
    WAITED=0
    while [ ! -d "$DOCLING_MODEL_PATH" ] && [ $WAITED -lt $MAX_WAIT ]; do
        echo "Model path not yet available, waiting... ($WAITED/$MAX_WAIT seconds)"
        sleep 5
        WAITED=$((WAITED + 5))
    done
    
    if [ -d "$DOCLING_MODEL_PATH" ]; then
        echo "✓ Model path is available: $DOCLING_MODEL_PATH"
    else
        echo "✗ ERROR: Model path not available after ${MAX_WAIT}s: $DOCLING_MODEL_PATH"
        exit 1
    fi
else
    echo "⚠ WARNING: DOCLING_MODEL_PATH not set"
fi

# Change to the app directory
cd /home/site/wwwroot

# Install dependencies from requirements.txt
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Verify the docling_endpoint package can be imported
echo "Verifying installation..."
python -c "from docling_endpoint.extractor import get_converter; print('✓ docling_endpoint imports successfully')" || {
    echo "✗ Failed to import docling_endpoint"
    exit 1
}

# Start the application - api.py is now in root!
echo "Starting gunicorn..."
exec gunicorn -k uvicorn.workers.UvicornWorker \
    -w 1 \
    -b 0.0.0.0:$PORT \
    --timeout 300 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    api:app