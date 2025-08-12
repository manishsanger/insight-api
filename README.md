# Insight API - Audio and Text Processing System

A comprehensive microservices-based application for processing audio files and text messages to extract structured information using AI. The system consists of three main services that work together to provide a complete solution for law enforcement and security applications.

## 🏗️ System Architecture

The application consists of three microservices:

1. **Officer Insight API** (Python/Flask) - Main REST API service
2. **Admin UI** (React/Node.js) - Administrative web interface  
3. **Speech2Text Service** (Python/Ollama) - Audio to text conversion and AI processing

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- 4GB+ available RAM
- 10GB+ available disk space
- **Ollama with LLaVA vision model** (for vehicle image identification)

### Start All Services
```bash
# Start with fresh data
./scripts/start.sh clean

# Start normally (preserve existing data)
./scripts/start.sh
```

### Setup LLaVA Vision Model (Required for Image Identification)
```bash
# Pull the LLaVA vision model in Ollama
ollama pull llava

# Verify the model is available
ollama list
```

### Access the Services
- **Admin UI**: http://localhost:8651
- **Officer Insight API**: http://localhost:8650
- **API Documentation**: http://localhost:8650/docs/
- **Speech2Text API**: http://localhost:8652
- **Speech2Text Docs**: http://localhost:8652/docs/

### Default Credentials
- **Username**: admin
- **Password**: Apple@123

## 📋 Service Overview

### Officer Insight API (Port 8650)
**Main REST API service for processing audio and text messages**

**Key Features:**
- Audio file processing through Speech2Text integration
- Text message parsing and information extraction
- **Vehicle image identification using AI vision models**
- AI-powered extraction using Ollama with enhanced prompt engineering
- JWT-based authentication for admin operations
- Configurable extraction parameters
- Request logging and monitoring
- Health check endpoints
- Swagger API documentation

**Default Extraction Parameters:**
- Person name
- Vehicle registration number  
- Vehicle make (manufacturer/brand)
- Vehicle color
- Vehicle model
- Location
- Event/crime/violation type

### Admin UI (Port 8651)
**Responsive React-based administrative interface**

**Key Features:**
- Dashboard with system statistics and charts
- Parameter management (create, edit, delete extraction parameters)
- Request monitoring with filtering and pagination
- User management with role-based access
- Date range filtering for historical data
- Real-time health monitoring
- Mobile-responsive design

### Speech2Text Service (Port 8652)
**Audio to text conversion using Ollama AI**

**Key Features:**
- High-quality audio transcription using FFmpeg audio preprocessing
- Advanced text processing with Ollama AI (llama3.2:latest model)
- Support for multiple audio formats (WAV, MP3, MP4, FLAC, etc.)
- Token-based authentication
- File storage with persistent mounting
- Health monitoring and file management
- Comprehensive test suite
- API documentation
- Structured information extraction for traffic offense reports

## 🔧 Management Scripts

Located in the `scripts/` directory:

- `./scripts/start.sh [clean]` - Start all services (optionally with clean data)
- `./scripts/stop.sh` - Stop all services
- `./scripts/build.sh` - Build all Docker images
- `./scripts/logs.sh [service-name]` - View service logs

## 💾 Data Persistence

All data is persisted in `/Users/manishsanger/docker-data/`:
- `mongodb/` - MongoDB database files
- `officer-insight-api/` - API service data
- `admin-ui/` - Admin UI data  
- `speech2text-service/` - Audio files storage

## 🌐 API Usage Examples

### Parse Text Message
```bash
curl -X POST http://localhost:8650/api/public/parse-message \
  -F "message=Add Traffic Offence Report. Driver name is James Smith, male, DOB 12/02/2000. Vehicle Registration OU18ZFB a blue BMW 420. Offence is No Seat Belt at Oxford Road, Cheltenham."
```

**Example Response:**
```json
{
  "extracted_info": {
    "driver_name": "James Smith",
    "date_of_birth": "12/02/2000", 
    "gender": "Male",
    "vehicle_registration": "OU18ZFB",
    "vehicle_make": "BMW",
    "vehicle_color": "Blue", 
    "vehicle_model": "420",
    "offence": "No Seat Belt",
    "location_of_offence": "Oxford Road, Cheltenham"
  }
}
```

### Parse Audio File
```bash
curl -X POST http://localhost:8650/api/public/parse-message \
  -F "audio_message=@recording.wav"
```

### Identify Vehicle from Image
```bash
curl -X POST http://localhost:8650/api/public/car-identifier \
  -F "image=@vehicle_photo.jpg"
```

**Example Response:**
```json
{
  "extracted_info": {
    "vehicle_registration": "AB67XYZ",
    "vehicle_make": "BMW",
    "vehicle_color": "Blue",
    "vehicle_model": "320i"
  }
}
```

### Admin Authentication
```bash
curl -X POST http://localhost:8650/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Apple@123"}'
```

## 🏥 Health Monitoring

Each service provides health check endpoints:
- Officer Insight API: `GET /api/health`
- Speech2Text Service: `GET /api/health`  
- Admin UI: `GET /health`

## 🔒 Security Features

- JWT-based authentication for admin operations
- Token-based authentication for Speech2Text service
- Role-based access control (admin/user roles)
- CORS protection
- Input validation and sanitization
- Secure password hashing (bcrypt)

## 📊 Default Sample Data

When started with the `clean` flag, the system loads sample extraction data including:
- Vehicle incidents with license plates
- Suspicious activity reports
- Traffic violations
- Theft reports
- Parking violations

## 🛠️ Technology Stack

**Backend Services:**
- Python 3.11 with Flask
- MongoDB for data storage
- Ollama AI for text processing and structured data extraction
- **Ollama LLaVA for vehicle image identification**
- FFmpeg for audio preprocessing
- JWT for authentication
- Docker for containerization
- **Pillow (PIL) for image processing**

**Frontend:**
- React 18 with React Admin
- Node.js/Express for serving
- Recharts for data visualization
- Responsive design with mobile support

**Infrastructure:**
- Docker Compose for orchestration
- Persistent volume mounting
- Network isolation
- Health check monitoring

## 📈 Performance Characteristics

**Speech2Text Service:**
- Supports files up to 100MB
- Processing time varies by audio length and AI processing complexity
- Ollama llama3.2:latest model optimized for structured data extraction
- Enhanced prompt engineering for traffic offense report parsing

**Officer Insight API:**
- Handles concurrent requests
- MongoDB indexing for fast queries
- Caching for improved performance

**Admin UI:**
- Lazy loading for optimal performance
- Pagination for large datasets
- Real-time updates

## 🔧 Configuration

Key environment variables:
- `MONGODB_URI` - Database connection string
- `SPEECH2TEXT_API_TOKEN` - Service authentication token
- `OLLAMA_URL` - Ollama AI service endpoint (http://host.docker.internal:11434)
- `OLLAMA_MODEL` - Ollama model name (llama3.2:latest)
- `REACT_APP_API_BASE_URL` - Frontend API configuration

## 📚 Documentation

Each service includes comprehensive documentation:
- `README.md` - Main project documentation and quick start guide
- `API_DOCUMENTATION.md` - Complete API reference with examples
- `CHANGELOG.md` - Version history and migration notes
- `officer-insight-api/README.md` - API service documentation
- `speech2text-service/README.md` - Speech service documentation  
- `admin-ui/README.md` - Admin interface documentation
- `DEPLOYMENT.md` - Detailed deployment instructions
- Interactive API docs available at `/docs/` endpoints

## 🚨 Troubleshooting

### Common Issues
1. **Services not starting**: Check Docker is running and ports are available
2. **Database connection errors**: Ensure MongoDB container is healthy
3. **Audio processing failures**: Verify audio file format and size
4. **Authentication issues**: Check credentials and token expiration

### Debug Commands
```bash
# Check service logs
./scripts/logs.sh [service-name]

# Check container status
docker-compose ps

# Restart specific service
docker-compose restart [service-name]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Check the service-specific README files
- Review the API documentation at `/docs/` endpoints
- Check the troubleshooting section
- Review Docker logs for error details