#!/bin/bash

# Insight API Logs Script
# Usage: ./logs.sh [service-name]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

if [ "$1" ]; then
    echo "📋 Showing logs for $1..."
    docker-compose logs -f "$1"
else
    echo "📋 Showing logs for all services..."
    echo "Available services: officer-insight-api, admin-ui, speech2text-service, mongodb"
    echo ""
    docker-compose logs -f
fi
