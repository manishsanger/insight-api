#!/bin/bash

# Insight API Management Script
# Usage: ./start.sh [clean]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting Insight API Services..."

# Check if clean flag is provided
CLEAN_START=false
if [ "$1" = "clean" ]; then
    CLEAN_START=true
    echo "🧹 Clean start requested - will reset all data"
fi

cd "$PROJECT_ROOT"

# Create data directories if they don't exist
echo "📁 Creating data directories..."
mkdir -p /Users/manishsanger/docker-data/mongodb
mkdir -p /Users/manishsanger/docker-data/officer-insight-api
mkdir -p /Users/manishsanger/docker-data/admin-ui
mkdir -p /Users/manishsanger/docker-data/speech2text-service

# If clean start, remove all data
if [ "$CLEAN_START" = true ]; then
    echo "🗑️  Removing existing data..."
    sudo rm -rf /Users/manishsanger/docker-data/mongodb/*
    sudo rm -rf /Users/manishsanger/docker-data/officer-insight-api/*
    sudo rm -rf /Users/manishsanger/docker-data/admin-ui/*
    sudo rm -rf /Users/manishsanger/docker-data/speech2text-service/*
    
    echo "🔄 Stopping and removing existing containers..."
    docker-compose down -v
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check MongoDB
echo "Checking MongoDB..."
timeout 30 bash -c 'until docker exec insight-mongodb mongosh --eval "db.adminCommand(\"ping\")" > /dev/null 2>&1; do sleep 1; done'
echo "✅ MongoDB is ready"

# Check Officer Insight API
echo "Checking Officer Insight API..."
timeout 60 bash -c 'until curl -s http://localhost:8650/api/health > /dev/null 2>&1; do sleep 2; done'
echo "✅ Officer Insight API is ready"

# Check Speech2Text Service
echo "Checking Speech2Text Service..."
timeout 60 bash -c 'until curl -s http://localhost:8652/api/health > /dev/null 2>&1; do sleep 2; done'
echo "✅ Speech2Text Service is ready"

# Check Admin UI
echo "Checking Admin UI..."
timeout 30 bash -c 'until curl -s http://localhost:8651/health > /dev/null 2>&1; do sleep 2; done'
echo "✅ Admin UI is ready"

# Load sample data if clean start
if [ "$CLEAN_START" = true ]; then
    echo "📊 Loading sample data..."
    sleep 10  # Give MongoDB a bit more time
    
    # Load sample data using mongoimport or direct insertion
    if [ -f "sample-data/sample_extractions.json" ]; then
        docker exec -i insight-mongodb mongoimport --username admin --password Apple@123 --authenticationDatabase admin --db insight_db --collection extractions --file /docker-entrypoint-initdb.d/sample_extractions.json --jsonArray || true
    fi
    
    echo "✅ Sample data loaded"
fi

echo ""
echo "🎉 All services are running successfully!"
echo ""
echo "📋 Service URLs:"
echo "   • Officer Insight API: http://localhost:8650"
echo "   • API Documentation:   http://localhost:8650/docs/"
echo "   • Admin UI:            http://localhost:8651"
echo "   • Speech2Text API:     http://localhost:8652"
echo "   • Speech2Text Docs:    http://localhost:8652/docs/"
echo ""
echo "🔐 Default Admin Credentials:"
echo "   • Username: admin"
echo "   • Password: Apple@123"
echo ""
echo "📊 To view logs: docker-compose logs -f [service-name]"
echo "🛑 To stop: ./scripts/stop.sh"
