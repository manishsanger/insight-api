#!/bin/bash

# Insight API Stop Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🛑 Stopping Insight API Services..."

cd "$PROJECT_ROOT"

# Stop all services
docker-compose down

echo "✅ All services have been stopped"
echo ""
echo "💡 To start services again: ./scripts/start.sh"
echo "💡 To start with clean data: ./scripts/start.sh clean"
