#!/bin/bash
set -e

echo "🚀 Starting Docling Endpoint API"

# Wait for Azure Storage mount
if [ ! -z "$DOCLING_MODEL_PATH" ]; then
    echo "⏳ Waiting for model storage mount..."
    timeout 60 bash -c 'until [ -d "$DOCLING_MODEL_PATH" ]; do sleep 2; done' || {
        echo "❌ Storage mount timeout"
        exit 1
    }
    echo "✅ Model path ready: $DOCLING_MODEL_PATH"
fi

# Verify installation
python -c "from docling_endpoint.extractor import get_converter" || exit 1

# Start app
cd /home/site/wwwroot
exec gunicorn -k uvicorn.workers.UvicornWorker \
    -w 1 \
    -b 0.0.0.0:$PORT \
    --timeout 300 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    api:app