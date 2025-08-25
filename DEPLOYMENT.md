# Officer Insight API System - Deployment Guide

## 🚀 Overview

This guide covers the deployment of the Officer Insight API System, a microservices-based architecture consisting of four main services:

1. **Officer Insight API** (Port 8650) - Core text/audio processing
2. **Car Identifier Service** (Port 8653) - Vehicle image analysis
3. **Speech2Text Service** (Port 8652) - Audio processing
4. **Admin UI** (Port 8651) - Web administration interface

## 📋 Prerequisites

### System Requirements
- **CPU**: 4+ cores (8+ recommended for production)
- **Memory**: 8GB RAM minimum (16GB+ recommended)
- **Storage**: 20GB+ available disk space
- **Network**: High-speed internet connection for AI model downloads

### Software Dependencies
- **Docker**: Version 20.0+ with Docker Compose
- **Ollama**: Local AI model serving platform
- **Git**: For repository cloning

### AI Models Required
```bash
# Required Ollama models
ollama pull gemma3:12b      # For vehicle image analysis
ollama pull llama3.2:latest # For text processing
```

## 🔧 Installation & Setup

### 1. Repository Setup

```bash
# Clone the repository
git clone https://github.com/manishsanger/insight-api.git
cd insight-api

# Verify directory structure
ls -la
# Should show: car-identifier-service/, officer-insight-api/, speech2text-service/, admin-ui/
```

### 2. Environment Configuration

#### Car Identifier Service Configuration
```bash
cd car-identifier-service
cp .env .env.local  # Create local configuration

# Edit .env.local with your settings
MONGODB_URI=mongodb://admin:Apple%40123@mongodb:27017/insight_db?authSource=admin
OLLAMA_URL=http://host.docker.internal:11434
VISION_MODEL=gemma3:12b
MODEL_TIMEOUT=180
EXTRACTION_FIELDS=vehicle_registration,vehicle_make,vehicle_color,vehicle_model
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,bmp,webp
MAX_CONTENT_LENGTH=16777216
CORS_ORIGINS=http://localhost:8651,http://localhost:3000
```

#### Officer Insight API Configuration
```bash
cd ../officer-insight-api
# Verify environment variables in docker-compose.yml
MONGODB_URI=mongodb://admin:Apple%40123@mongodb:27017/insight_db?authSource=admin
SPEECH2TEXT_API_URL=http://speech2text-service:8652
SPEECH2TEXT_API_TOKEN=insight_speech_token_2024
OLLAMA_URL=http://host.docker.internal:11434
```

### 3. Build and Deploy

#### Option A: Automated Build Script (Recommended)
```bash
# Make build script executable
chmod +x scripts/build.sh

# Run automated build and deployment
./scripts/build.sh

# The script will:
# 1. Stop existing containers
# 2. Build all service images
# 3. Prompt to start services
# 4. Display service URLs and health checks
```

#### Option B: Manual Deployment
```bash
# Stop existing containers
docker-compose down

# Build all services
docker-compose build --no-cache

# Start all services
docker-compose up -d

# Verify all services are running
docker-compose ps
```

### 4. Service Verification

#### Health Checks
```bash
# Check all service health
curl http://localhost:8650/api/public/health  # Officer API
curl http://localhost:8653/api/public/health  # Car Identifier
curl http://localhost:8652/api/health         # Speech2Text
curl http://localhost:8651                    # Admin UI (should return HTML)
```

#### Service Logs
```bash
# Monitor service logs
docker logs insight-officer-api
docker logs insight-car-identifier
docker logs insight-speech2text
docker logs insight-admin-ui
docker logs insight-mongodb
```

## 🌐 Service Access

### Service URLs
- **Officer Insight API**: http://localhost:8650
- **Car Identifier Service**: http://localhost:8653
- **Speech2Text Service**: http://localhost:8652
- **Admin UI**: http://localhost:8651
- **MongoDB**: localhost:27017

### API Documentation
- **Officer API Docs**: http://localhost:8650/docs/
- **Car Identifier Docs**: http://localhost:8653/docs/
- **Speech2Text Docs**: http://localhost:8652/docs/

### Default Credentials
- **Username**: `admin`
- **Password**: `Apple@123`

## ⚙️ Configuration Management

### Environment Variables

#### Car Identifier Service (.env)
```bash
# Database Configuration
MONGODB_URI=mongodb://admin:Apple%40123@mongodb:27017/insight_db?authSource=admin

# AI Model Configuration
OLLAMA_URL=http://host.docker.internal:11434
VISION_MODEL=gemma3:12b
MODEL_TIMEOUT=180

# Service Configuration
PORT=8653
CORS_ORIGINS=http://localhost:8651,http://localhost:3000

# File Upload Configuration
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,bmp,webp
MAX_CONTENT_LENGTH=16777216

# Extraction Configuration
EXTRACTION_FIELDS=vehicle_registration,vehicle_make,vehicle_color,vehicle_model
```

#### Docker Compose Environment
```yaml
# Officer Insight API
environment:
  MONGODB_URI: mongodb://admin:Apple%40123@mongodb:27017/insight_db?authSource=admin
  SPEECH2TEXT_API_URL: http://speech2text-service:8652
  SPEECH2TEXT_API_TOKEN: insight_speech_token_2024
  OLLAMA_URL: http://host.docker.internal:11434

# Car Identifier Service  
environment:
  MONGODB_URI: mongodb://admin:Apple%40123@mongodb:27017/insight_db?authSource=admin
  OLLAMA_URL: http://host.docker.internal:11434
  VISION_MODEL: gemma3:12b
  MODEL_TIMEOUT: 180
  EXTRACTION_FIELDS: vehicle_registration,vehicle_make,vehicle_color,vehicle_model
```

### Configurable Parameters

#### Extraction Fields (Car Identifier)
Customize what information is extracted from vehicle images:

```bash
# Default fields
EXTRACTION_FIELDS=vehicle_registration,vehicle_make,vehicle_color,vehicle_model

# Extended fields  
EXTRACTION_FIELDS=vehicle_registration,vehicle_make,vehicle_color,vehicle_model,vehicle_type,vehicle_year,vehicle_condition
```

#### AI Model Configuration
```bash
# Change vision model
VISION_MODEL=llava:latest          # Alternative vision model
VISION_MODEL=gemma3:12b           # Default (recommended)

# Adjust processing timeout
MODEL_TIMEOUT=120                 # Faster but may timeout on complex images
MODEL_TIMEOUT=300                 # Slower but more reliable
```

## 🔒 Security Configuration

### Database Security
```bash
# MongoDB credentials (change for production)
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=NewSecurePassword123!

# Update all services to use new credentials
MONGODB_URI=mongodb://admin:NewSecurePassword123%21@mongodb:27017/insight_db?authSource=admin
```

### JWT Security
```bash
# Generate new JWT secret (in officer-insight-api)
JWT_SECRET_KEY=your-new-super-secure-jwt-secret-key-2025
```

### API Token Security
```bash
# Change Speech2Text API token
SPEECH2TEXT_API_TOKEN=your-new-secure-api-token-2025
```

### CORS Configuration
```bash
# Restrict CORS origins for production
CORS_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com
```

## 📊 Production Deployment

### Docker Compose Production Configuration

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  mongodb:
    image: mongo:latest
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USERNAME}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    volumes:
      - mongodb_data:/data/db
    networks:
      - insight-network
    # Remove port mapping for production (internal access only)

  officer-insight-api:
    build: ./officer-insight-api
    restart: always
    environment:
      MONGODB_URI: mongodb://${MONGO_USERNAME}:${MONGO_PASSWORD}@mongodb:27017/insight_db?authSource=admin
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      SPEECH2TEXT_API_URL: http://speech2text-service:8652
      SPEECH2TEXT_API_TOKEN: ${SPEECH2TEXT_TOKEN}
      OLLAMA_URL: ${OLLAMA_URL}
    depends_on:
      - mongodb
      - speech2text-service
    networks:
      - insight-network
    volumes:
      - officer_api_data:/app/data

  car-identifier-service:
    build: ./car-identifier-service
    restart: always
    environment:
      MONGODB_URI: mongodb://${MONGO_USERNAME}:${MONGO_PASSWORD}@mongodb:27017/insight_db?authSource=admin
      OLLAMA_URL: ${OLLAMA_URL}
      VISION_MODEL: ${VISION_MODEL}
      MODEL_TIMEOUT: ${MODEL_TIMEOUT}
      EXTRACTION_FIELDS: ${EXTRACTION_FIELDS}
    depends_on:
      - mongodb
    networks:
      - insight-network
    volumes:
      - car_identifier_data:/app/data

networks:
  insight-network:
    driver: bridge

volumes:
  mongodb_data:
  officer_api_data:
  car_identifier_data:
  admin_ui_data:
  speech2text_data:
```

### Production Environment File
```bash
# .env.prod
MONGO_USERNAME=production_admin
MONGO_PASSWORD=super_secure_password_2025
JWT_SECRET_KEY=production-jwt-secret-key-very-long-and-secure
SPEECH2TEXT_TOKEN=production-speech-token-2025
OLLAMA_URL=http://production-ollama-server:11434
VISION_MODEL=gemma3:12b
MODEL_TIMEOUT=180
EXTRACTION_FIELDS=vehicle_registration,vehicle_make,vehicle_color,vehicle_model
```

### Nginx Reverse Proxy Configuration

```nginx
# /etc/nginx/sites-available/insight-api
server {
    listen 80;
    server_name your-domain.com;

    # Officer Insight API
    location /api/ {
        proxy_pass http://localhost:8650;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Car Identifier Service  
    location /car-api/ {
        proxy_pass http://localhost:8653/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Admin UI
    location / {
        proxy_pass http://localhost:8651;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📈 Monitoring & Maintenance

### Service Monitoring
```bash
# Check service status
docker-compose ps

# Monitor resource usage
docker stats

# Check service logs
docker-compose logs -f officer-insight-api
docker-compose logs -f car-identifier-service
docker-compose logs -f speech2text-service
```

### Health Check Monitoring
```bash
#!/bin/bash
# health-check.sh - Run this periodically

services=(
    "http://localhost:8650/api/public/health"
    "http://localhost:8653/api/public/health" 
    "http://localhost:8652/api/health"
)

for service in "${services[@]}"; do
    if curl -f "$service" >/dev/null 2>&1; then
        echo "✅ $service - Healthy"
    else
        echo "❌ $service - Unhealthy"
    fi
done
```

### Database Backup
```bash
# Create MongoDB backup
docker exec insight-mongodb mongodump --host localhost --port 27017 --username admin --password Apple@123 --authenticationDatabase admin --out /backup

# Copy backup from container
docker cp insight-mongodb:/backup ./mongodb-backup-$(date +%Y%m%d)
```

### Log Rotation
```bash
# Configure Docker log rotation in /etc/docker/daemon.json
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m",
        "max-file": "5"
    }
}
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Service Connectivity Issues
```bash
# Check if all containers are running
docker-compose ps

# Check Docker network
docker network ls
docker network inspect insight-api_insight-network

# Restart specific service
docker-compose restart car-identifier-service
```

#### 2. AI Model Issues
```bash
# Verify Ollama is running and models are available
curl http://localhost:11434/api/version
curl http://localhost:11434/api/tags

# Pull missing models
ollama pull gemma3:12b
ollama pull llama3.2:latest
```

#### 3. Database Connection Issues
```bash
# Check MongoDB container
docker logs insight-mongodb

# Test database connection
docker exec -it insight-mongodb mongo -u admin -p Apple@123 --authenticationDatabase admin

# Verify database exists
use insight_db
show collections
```

#### 4. Port Conflicts
```bash
# Check what's using ports
netstat -tulpn | grep :8650
netstat -tulpn | grep :8653

# Kill processes using ports
sudo kill -9 $(lsof -t -i:8650)
```

### Performance Issues

#### Memory Optimization
```bash
# Monitor memory usage
docker stats --no-stream

# Limit container memory in docker-compose.yml
services:
  car-identifier-service:
    mem_limit: 2g
    memswap_limit: 2g
```

#### Processing Optimization
```bash
# Adjust model timeout for performance vs accuracy
MODEL_TIMEOUT=120    # Faster processing
MODEL_TIMEOUT=300    # More accurate but slower

# Reduce image size before processing
MAX_CONTENT_LENGTH=8388608  # 8MB limit instead of 16MB
```

## 🔧 Development Deployment

### Local Development Setup
```bash
# Set up development environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies for individual service development
cd car-identifier-service
pip install -r requirements.txt

# Run service locally for development
python app.py
```

### Development Docker Compose
```bash
# Use development override
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Mount source code for live reload
volumes:
  - ./car-identifier-service:/app
  - ./officer-insight-api:/app
```

## 📚 Additional Resources

### Documentation Links
- [System README](./README.md) - Overview and quick start
- [API Documentation](./API_DOCUMENTATION.md) - Complete API reference
- [Car Identifier Service](./car-identifier-service/README.md) - Service-specific guide
- [Project Status](./PROJECT_STATUS.md) - Current system status

### Support
- **Issues**: Submit to project repository
- **Documentation**: Check service-specific README files
- **Logs**: Use `docker logs <container-name>` for debugging
- **Health Checks**: Monitor service health endpoints

### Best Practices
1. **Always backup data** before major updates
2. **Test in development** environment first
3. **Monitor service health** regularly
4. **Keep AI models updated** for best performance
5. **Secure credentials** in production environments
6. **Use reverse proxy** for production deployments
7. **Implement log rotation** to manage disk space
8. **Regular security updates** for all components

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Verify system requirements
- [ ] Install Docker and Docker Compose
- [ ] Install and configure Ollama
- [ ] Download required AI models
- [ ] Clone repository and check structure

### Deployment
- [ ] Configure environment variables
- [ ] Build all service images
- [ ] Start services with docker-compose
- [ ] Verify all services are running
- [ ] Test health check endpoints

### Post-Deployment
- [ ] Test all API endpoints
- [ ] Verify Admin UI access
- [ ] Test image upload and processing
- [ ] Test audio processing
- [ ] Configure monitoring and backup
- [ ] Set up log rotation
- [ ] Document any customizations

### Production Additional
- [ ] Configure reverse proxy
- [ ] Set up SSL certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting
- [ ] Create backup schedules
- [ ] Document disaster recovery procedures
