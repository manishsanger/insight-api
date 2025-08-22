# Deployment Guide - Insight API

This guide provides detailed instructions for deploying the Insight API system in various environments.

## 🏗️ System Requirements

### Hardware Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended for Ollama AI processing
- **Storage**: 50GB+ available space
- **Network**: Internet connectivity for initial setup and Ollama model access

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git (for source code)
- **Ollama with Gemma3:12b vision model** (for vehicle image identification)
- 4GB+ available RAM for containers

### Supported Operating Systems
- Ubuntu 20.04+
- CentOS 8+
- macOS 10.15+
- Windows 10+ (with WSL2)

## 🐳 Docker Deployment (Recommended)

### 1. Clone Repository
```bash
git clone https://github.com/manishsanger/insight-api.git
cd insight-api
```

### 2. Configure Environment (Optional)
```bash
# Copy and modify environment file
cp .env.example .env
# Edit .env file with your configurations
```

### 3. Create Data Directories
```bash
sudo mkdir -p /Users/manishsanger/docker-data/{mongodb,officer-insight-api,admin-ui,speech2text-service}
sudo chown -R $USER:$USER /Users/manishsanger/docker-data
```

### 4. Deploy Services
```bash
# Install Gemma3 model for vehicle identification
ollama pull gemma3:12b

# Clean deployment (fresh data)
./scripts/start.sh clean

# Normal deployment (preserve data)
./scripts/start.sh
```

### 5. Verify Deployment
```bash
# Check all services are running
docker-compose ps

# Check service logs
./scripts/logs.sh

# Test health endpoints
curl http://localhost:8650/api/health
curl http://localhost:8651/health
curl http://localhost:8652/api/health
```

## 🔧 Configuration Options

### Environment Variables

**Docker Compose Level:**
```yaml
# docker-compose.yml
environment:
  MONGODB_URI: mongodb://admin:Apple@123@mongodb:27017/insight_db?authSource=admin
  SPEECH2TEXT_API_TOKEN: insight_speech_token_2024
  OLLAMA_URL: http://host.docker.internal:11434
```

**Service-Specific:**

**Officer Insight API:**
- `MONGODB_URI`: Database connection string
- `SPEECH2TEXT_API_URL`: Speech service URL
- `SPEECH2TEXT_API_TOKEN`: Authentication token
- `OLLAMA_URL`: AI service endpoint
- `JWT_SECRET_KEY`: JWT signing secret

**Speech2Text Service:**
- `API_TOKEN`: Authentication token
- `OLLAMA_URL`: Ollama AI service URL
- `OLLAMA_MODEL`: Ollama model name
- `MAX_CONTENT_LENGTH`: Maximum file size

**Admin UI:**
- `REACT_APP_API_BASE_URL`: Backend API URL
- `NODE_ENV`: Environment mode

### Port Configuration
```yaml
# Default ports (modify in docker-compose.yml if needed)
services:
  mongodb: 27017:27017
  officer-insight-api: 8650:8650
  admin-ui: 8651:8651
  speech2text-service: 8652:8652
```

### Volume Mounts
```yaml
# Persistent data storage
volumes:
  - /Users/manishsanger/docker-data/mongodb:/data/db
  - /Users/manishsanger/docker-data/officer-insight-api:/app/data
  - /Users/manishsanger/docker-data/admin-ui:/app/data
  - /Users/manishsanger/docker-data/speech2text-service:/app/audio_files
```

## 🌐 Production Deployment

### 1. Security Hardening

**Change Default Credentials:**
```bash
# Update in docker-compose.yml
MONGO_INITDB_ROOT_PASSWORD: "your-secure-password"

# Update in admin panel after first login
# Username: admin, Password: your-new-password
```

**Update API Tokens:**
```bash
# Change Speech2Text API token
SPEECH2TEXT_API_TOKEN: "your-secure-token-2024"

# Update JWT secret
JWT_SECRET_KEY: "your-jwt-secret-key"
```

### 2. HTTPS Configuration

**Using Nginx Reverse Proxy:**
```nginx
# /etc/nginx/sites-available/insight-api
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location /api/ {
        proxy_pass http://localhost:8650/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /admin/ {
        proxy_pass http://localhost:8651/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /speech/ {
        proxy_pass http://localhost:8652/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Database Backup Strategy

**Automated MongoDB Backup:**
```bash
#!/bin/bash
# backup-mongodb.sh
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

docker exec insight-mongodb mongodump \
  --username admin \
  --password Apple@123 \
  --authenticationDatabase admin \
  --db insight_db \
  --out /tmp/backup_$DATE

docker cp insight-mongodb:/tmp/backup_$DATE $BACKUP_DIR/
docker exec insight-mongodb rm -rf /tmp/backup_$DATE

# Keep only last 7 days of backups
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} \;
```

**Cron Schedule:**
```bash
# Add to crontab
0 2 * * * /path/to/backup-mongodb.sh
```

### 4. Log Management

**Log Rotation Configuration:**
```bash
# /etc/logrotate.d/insight-api
/var/log/insight-api/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

**Docker Logging:**
```yaml
# docker-compose.yml
services:
  officer-insight-api:
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"
```

## 📊 Monitoring Setup

### 1. Health Check Monitoring

**Docker Health Checks:**
```yaml
# docker-compose.yml
services:
  officer-insight-api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8650/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

**External Monitoring Script:**
```bash
#!/bin/bash
# health-monitor.sh
services=("8650/api/health" "8651/health" "8652/api/health")

for service in "${services[@]}"; do
    if ! curl -f "http://localhost:$service" > /dev/null 2>&1; then
        echo "Service $service is down" | mail -s "Service Alert" admin@company.com
    fi
done
```

### 2. Performance Monitoring

**Resource Usage:**
```bash
# Monitor Docker container resources
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
```

### 3. Application Metrics

**Custom Metrics Endpoint:**
- Request count and response times
- Error rates by endpoint
- Database query performance
- Audio processing times

## 🔄 Update and Maintenance

### 1. Application Updates

**Rolling Update Process:**
```bash
# 1. Pull latest code
git pull origin main

# 2. Build new images
./scripts/build.sh

# 3. Update services one by one
docker-compose up -d --no-deps officer-insight-api
docker-compose up -d --no-deps admin-ui
docker-compose up -d --no-deps speech2text-service

# 4. Verify health
./scripts/logs.sh
```

### 2. Database Maintenance

**MongoDB Maintenance:**
```bash
# Compact collections
docker exec insight-mongodb mongosh --eval "db.runCommand({compact: 'requests'})"

# Rebuild indexes
docker exec insight-mongodb mongosh --eval "db.extractions.reIndex()"

# Database statistics
docker exec insight-mongodb mongosh --eval "db.stats()"
```

### 3. Clean Up

**Remove Old Data:**
```bash
# Clean old audio files (older than 30 days)
find /Users/manishsanger/docker-data/speech2text-service -name "*.wav" -mtime +30 -delete

# Clean old request logs (keep last 90 days)
docker exec insight-mongodb mongosh --eval "
  db.requests.deleteMany({
    created_at: { \$lt: new Date(Date.now() - 90*24*60*60*1000) }
  })
"
```

## 🚨 Troubleshooting

### Common Deployment Issues

**1. Port Conflicts:**
```bash
# Check what's using the ports
sudo netstat -tulpn | grep :8650
sudo lsof -i :8650

# Kill conflicting processes
sudo kill -9 <PID>
```

**2. Permission Issues:**
```bash
# Fix data directory permissions
sudo chown -R $USER:$USER /Users/manishsanger/docker-data
chmod -R 755 /Users/manishsanger/docker-data
```

**3. Memory Issues:**
```bash
# Check available memory
free -h

# Increase Docker memory limit
# Docker Desktop -> Settings -> Resources -> Memory
```

**4. Network Issues:**
```bash
# Check Docker networks
docker network ls
docker network inspect insight-api_insight-network

# Recreate network if needed
docker-compose down
docker network prune
docker-compose up -d
```

### Service-Specific Issues

**MongoDB:**
```bash
# Check MongoDB logs
docker logs insight-mongodb

# Connect to MongoDB
docker exec -it insight-mongodb mongosh -u admin -p Apple@123

# Check database status
docker exec insight-mongodb mongosh --eval "db.adminCommand('serverStatus')"
```

**Officer Insight API:**
```bash
# Check API logs
docker logs insight-officer-api

# Test API directly
curl -v http://localhost:8650/api/health
```

**Speech2Text Service:**
```bash
# Check Ollama connectivity and model availability
docker logs insight-speech2text

# Test audio conversion with AI processing
curl -X POST http://localhost:8652/api/convert \
  -H "Authorization: Bearer insight_speech_token_2024" \
  -F "audio_file=@test.wav"

# Test direct text processing
curl -X POST http://localhost:8652/api/process-text \
  -H "Authorization: Bearer insight_speech_token_2024" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test message for AI processing"}'
```

## 🔐 Security Considerations

### 1. Network Security
- Use firewall to restrict access to necessary ports only
- Implement VPN access for admin interfaces
- Use HTTPS for all external communications

### 2. Container Security
- Regularly update base images
- Scan images for vulnerabilities
- Use non-root users in containers
- Implement resource limits

### 3. Data Security
- Encrypt data at rest
- Use secure backup procedures
- Implement access logging
- Regular security audits

### 4. Authentication Security
- Use strong passwords and tokens
- Implement password rotation
- Monitor authentication logs
- Use multi-factor authentication

## 📞 Support and Maintenance

### 1. Log Analysis
- Monitor application logs for errors
- Set up log aggregation (ELK stack)
- Create alerts for critical errors
- Regular log review processes

### 2. Performance Tuning
- Monitor resource usage trends
- Optimize database queries
- Scale services based on load
- Cache frequently accessed data

### 3. Disaster Recovery
- Regular backup testing
- Document recovery procedures
- Maintain standby environments
- Practice disaster recovery scenarios

This deployment guide provides comprehensive instructions for setting up, configuring, and maintaining the Insight API system in production environments. Follow the security recommendations and monitoring practices to ensure reliable operation.
