#!/bin/bash

# Build script for all services in the Officer Insight API system

echo "🚀 Building Officer Insight API System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    print_error "docker-compose is not installed. Please install docker-compose and try again."
    exit 1
fi

print_status "Stopping existing containers..."
docker-compose down

print_status "Building all services..."

# Build officer-insight-api
print_status "Building officer-insight-api..."
docker build -t officer-insight-api:latest ./officer-insight-api
if [ $? -eq 0 ]; then
    print_success "officer-insight-api built successfully"
else
    print_error "Failed to build officer-insight-api"
    exit 1
fi

# Build car-identifier-service
print_status "Building car-identifier-service..."
docker build -t car-identifier-service:latest ./car-identifier-service
if [ $? -eq 0 ]; then
    print_success "car-identifier-service built successfully"
else
    print_error "Failed to build car-identifier-service"
    exit 1
fi

# Build speech2text-service
print_status "Building speech2text-service..."
docker build -t speech2text-service:latest ./speech2text-service
if [ $? -eq 0 ]; then
    print_success "speech2text-service built successfully"
else
    print_error "Failed to build speech2text-service"
    exit 1
fi

# Build admin-ui
print_status "Building admin-ui..."
docker build -t admin-ui:latest ./admin-ui
if [ $? -eq 0 ]; then
    print_success "admin-ui built successfully"
else
    print_error "Failed to build admin-ui"
    exit 1
fi

print_success "All services built successfully!"

# Option to start services
read -p "Do you want to start all services now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Starting all services..."
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        print_success "All services started successfully!"
        echo
        print_status "Service URLs:"
        echo "  🔧 Officer Insight API: http://localhost:8650"
        echo "  � Car Identifier Service: http://localhost:8653"
        echo "  🎤 Speech2Text Service: http://localhost:8652"
        echo "  🖥️  Admin UI: http://localhost:8651"
        echo "  📊 MongoDB: localhost:27017"
        echo
        print_status "API Documentation:"
        echo "  📚 Officer API Docs: http://localhost:8650/docs/"
        echo "  📚 Car Identifier Docs: http://localhost:8653/docs/"
        echo "  📚 Speech2Text Docs: http://localhost:8652/docs/"
        echo
        print_status "Health Checks:"
        echo "  ❤️  Officer API Health: http://localhost:8650/api/public/health"
        echo "  ❤️  Car Identifier Health: http://localhost:8653/api/public/health"
        echo "  ❤️  Speech2Text Health: http://localhost:8652/api/health"
    else
        print_error "Failed to start services"
        exit 1
    fi
else
    print_status "Services built but not started. Use 'docker-compose up -d' to start them."
fi

print_success "Build process completed!"
