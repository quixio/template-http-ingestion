#!/bin/sh
set -e

echo "📦 Running database initialization..."
python /app/db_helpers.py

echo "🚀 Starting Streamlit..."
exec streamlit run /app/main.py --server.port=80 --server.enableCORS=false --server.address=0.0.0.0
