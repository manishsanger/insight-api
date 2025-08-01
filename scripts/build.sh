#!/bin/bash

# Insight API Build Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔨 Building Insight API Services..."

cd "$PROJECT_ROOT"

# Build all services
echo "Building Officer Insight API..."
docker-compose build officer-insight-api

echo "Building Admin UI..."
docker-compose build admin-ui

echo "Building Speech2Text Service..."
docker-compose build speech2text-service

echo "✅ All services have been built successfully"
echo ""
echo "🚀 To start services: ./scripts/start.sh"
