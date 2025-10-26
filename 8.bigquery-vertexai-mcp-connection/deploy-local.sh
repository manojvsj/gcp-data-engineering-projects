#!/bin/bash

# Deploy locally with Docker Compose

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "🧹 Cleaning up existing containers..."
docker compose down 2>/dev/null || true
docker stop mcp-bigquery-server streamlit-app 2>/dev/null || true
docker rm mcp-bigquery-server streamlit-app 2>/dev/null || true

echo "� Checking ports..."
lsof -ti:8080 | xargs kill -9 2>/dev/null || true
lsof -ti:8501 | xargs kill -9 2>/dev/null || true

echo "�🚀 Starting services with Docker Compose..."
docker compose up -d --build

echo ""
echo "✅ Services running:"
echo "   MCP Server: http://localhost:8080"
echo "   Streamlit: http://localhost:8501"
echo ""
echo "To view logs: docker compose logs -f"
echo "To stop: docker compose down"
