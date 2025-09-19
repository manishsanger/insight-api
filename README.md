# Officer Insight API System

## 🎯 Overview

Officer Insight API is a comprehensive microservices-based system designed to assist law enforcement officers in processing and extracting structured information from various data sources including text reports, audio recordings, and vehicle images. The system leverages advanced AI models for speech-to-text conversion, text processing, and computer vision analysis.

## 🏗️ System Architecture

The system consists of five main microservices:

### 🔧 Officer Insight API (Port 8650)
- **Purpose**: Core API service for text/audio processing, image management, person management, and vehicle management
- **Features**: 
  - JWT authentication and user management
  - **🎤 FULL AUDIO PROCESSING PIPELINE**: Complete audio-to-text conversion with AI extraction (NEWLY FUNCTIONAL!)
  - Text extraction and structured information processing
  - **Image Management System**: Upload, store, and serve images with organized file structure
  - **Person Management**: Complete CRUD operations for person records with photo attachments
  - **Vehicle Management**: Complete CRUD operations for vehicle records with photo attachments
  - **User-Specific Data Access**: Dedicated endpoints for users to access only their own data
  - Soft delete capabilities for data preservation
  - RESTful APIs with comprehensive pagination and search
- **AI Model**: Llama3.2:latest for text processing
- **Database**: MongoDB for data persistence
- **Storage**: Persistent file storage for images with date-based organization

### 🚗 Car Identifier Service (Port 8653)
- **Purpose**: Specialized AI-powered vehicle identification from images
- **Features**: License plate recognition, vehicle make/model/color identification
- **AI Model**: Gemma3:12b vision model for vehicle analysis
- **Configuration**: Fully configurable extraction fields and parameters

### 📄 Document Reader Service (Port 8654)
- **Purpose**: AI-powered document parsing and information extraction from images and PDFs
- **Features**: Identity document analysis, structured data extraction, multi-format support, optional selective extraction
- **AI Model**: Gemma3:12b vision model for document analysis
- **Formats**: JPG, PNG, PDF, and other image formats
- **Optional Parameters**: 
  - `extract_person_image`: Extract person's photo from document (default: true)
  - `extract_text_info`: Extract text information from document (default: true)

### 🎤 Speech2Text Service (Port 8652) ⭐ FULLY FUNCTIONAL
- **Purpose**: Audio processing and speech-to-text conversion with JWT authentication
- **Features**: Multi-format audio support, Whisper AI integration, seamless inter-service communication
- **AI Model**: OpenAI Whisper for speech recognition + Llama3.2:latest for text processing
- **Formats**: WAV, MP3, M4A, FLAC, OGG
- **Authentication**: JWT-based secure communication with officer-insight-api

### 🖥️ Admin UI (Port 8651)
- **Purpose**: Web-based administration interface
- **Features**: User management, system monitoring, data visualization
- **Technology**: React.js with Material-UI
- **Authentication**: JWT-based secure access

## ✨ Key Features

### 🎯 Core Capabilities
- **🎤 COMPLETE AUDIO PROCESSING PIPELINE**: Audio → Speech Recognition → AI Extraction → Structured Data (WORKING!)
- **Multi-Source Data Processing**: Text, audio, image, and document inputs
- **AI-Powered Analysis**: Advanced machine learning models for accurate extraction
- **Document Intelligence**: Automated parsing of identity documents, certificates, and forms
- **Vehicle Recognition**: Comprehensive vehicle identification and analysis
- **Structured Data Output**: Consistent JSON format for all extractions
- **Real-time Processing**: Fast response times for immediate insights
- **Microservices Architecture**: Scalable and maintainable design

### 🔒 Security & Authentication
- JWT-based authentication system with Bearer tokens across all services
- Role-based access control (Admin/User)
- All endpoints secured except health and auth endpoints
- CORS protection and input validation
- Secure inter-service communication with synchronized JWT authentication

### 📊 Data Management
- MongoDB integration for persistent storage
- Request logging and audit trails
- Extraction history and analytics
- **User Data Isolation**: Each user can only access their own created data
- Automatic user association on data creation
- Configurable data retention policies

### 🌐 API Integration
- RESTful API design with OpenAPI documentation
- Swagger UI for interactive API testing
- Comprehensive error handling and status codes
- Health monitoring endpoints

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Ollama with required models:
  - `gemma3:12b` (for vehicle identification and document reading)
  - `llama3.2:latest` (for text processing and audio content analysis)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/manishsanger/insight-api.git
cd insight-api
```

2. **Install required AI models:**
```bash
# Install Ollama models
ollama pull gemma3:12b
ollama pull llama3.2:latest
```

3. **Build and start all services:**
```bash
# Make build script executable
chmod +x scripts/build.sh

# Build and start all services
./scripts/build.sh
```

4. **Verify deployment:**
```bash
# Check service health
# Test all services are running
curl http://localhost:8650/api/public/health     # Officer API
curl http://localhost:8653/api/public/health     # Car Identifier
curl http://localhost:8654/api/public/health     # Document Reader
curl http://localhost:8652/api/public/health     # Speech2Text
```

### ⚠️ Important: Persistent Storage Configuration

All services use the **global docker-data directory** for persistent storage:
```
/Users/manishsanger/docker-data/
├── mongodb/                    # MongoDB data
├── officer-insight-api/        # Images, uploads, user data
├── car-identifier-service/     # Vehicle analysis data
├── doc-reader-service/         # Document analysis data
├── admin-ui/                   # UI data
└── speech2text-service/        # Audio processing data
```

**Note**: The system does NOT use the local `./docker-data/` directory. All persistent data is stored in the global location to avoid conflicts and ensure data persistence across deployments.

### Service URLs
- **Officer Insight API**: http://localhost:8650
- **Car Identifier Service**: http://localhost:8653
- **Document Reader Service**: http://localhost:8654
- **Speech2Text Service**: http://localhost:8652
- **Admin UI**: http://localhost:8651
- **MongoDB**: localhost:27017

### API Documentation
- **Officer API Docs**: http://localhost:8650/docs/
- **Car Identifier Docs**: http://localhost:8653/docs/
- **Document Reader Docs**: http://localhost:8654/docs/
- **Speech2Text Docs**: http://localhost:8652/docs/

### Default Credentials
- **Username**: admin
- **Password**: Apple@123

## 📋 API Usage Examples

### Authentication Flow
All endpoints (except `/health` and `/auth`) require JWT Bearer token authentication.

1. **Login to get JWT token**:
```bash
curl -X POST "http://localhost:8650/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Apple@123"}'
```

2. **Use the token in subsequent requests**:
```bash
# Replace YOUR_JWT_TOKEN with the token from login response
export TOKEN="YOUR_JWT_TOKEN"
```

### Text Processing
```bash
curl -X POST "http://localhost:8650/api/parse-message" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Authorization: Bearer $TOKEN" \
  -d "message=Officer Johnson reporting traffic violation. Red Honda Civic plate ABC123 speeding in school zone."
```

### Document Processing (with optional parameters)
```bash
# Extract both person image and text information (default)
curl -X POST "http://localhost:8654/api/doc-reader" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@path/to/document/passport.pdf"

# Extract only text information
curl -X POST "http://localhost:8654/api/doc-reader" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@path/to/document/passport.pdf" \
  -F "extract_person_image=false" \
  -F "extract_text_info=true"

# Extract only person image
curl -X POST "http://localhost:8654/api/doc-reader" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@path/to/document/passport.pdf" \
  -F "extract_person_image=true" \
  -F "extract_text_info=false"
```

### Vehicle Image Analysis
```bash
curl -X POST "http://localhost:8653/api/car-identifier" \
  -H "Authorization: Bearer $TOKEN" \
  -F "image=@path/to/vehicle/image.jpg"
```

### Audio Processing ⭐ FULLY FUNCTIONAL
```bash
# Process audio file (traffic offence report example)
curl -X POST "http://localhost:8650/api/parse-message" \
  -H "Authorization: Bearer $TOKEN" \
  -F "audio_message=@test-data/traffic-offence-report.wav"

# Expected Response:
# {
#   "id": "68cda46e730539f1afe6aea7",
#   "text": "Add Traffic Offence Report. Offence Occurred at 10:00am on 15/05/2025...",
#   "extracted_info": {
#     "driver_name": "James Smith",
#     "vehicle_registration": "OU18ZFB", 
#     "vehicle_make": "BMW",
#     "offence": "No Seat Belt"
#   },
#   "has_audio": true
# }
```

## ⚙️ Configuration

### Environment Variables

#### Document Reader Service
```bash
VISION_MODEL=gemma3:12b                    # AI model for document analysis
EXTRACTION_FIELDS=document_type,name,date_of_birth,country,date_of_issue,expiry_date,address,gender,place_of_birth,issuing_authority,nationality,pin_code
MODEL_TIMEOUT=180                          # Processing timeout in seconds
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,bmp,webp,pdf
MAX_CONTENT_LENGTH=16777216               # 16MB file size limit
```

#### Car Identifier Service
```bash
VISION_MODEL=gemma3:12b                    # AI model for vehicle analysis
EXTRACTION_FIELDS=vehicle_registration,vehicle_make,vehicle_color,vehicle_model
MODEL_TIMEOUT=180                          # Processing timeout in seconds
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,bmp,webp
MAX_CONTENT_LENGTH=16777216               # 16MB file size limit
```

#### Officer Insight API
```bash
OLLAMA_URL=http://host.docker.internal:11434
SPEECH2TEXT_API_URL=http://speech2text-service:8652
MONGODB_URI=mongodb://admin:Apple%40123@mongodb:27017/insight_db?authSource=admin

# Image Management Configuration (New)
IMAGES_UPLOAD_BASE_PATH=/app/data/images   # Base directory for image storage
IMAGES_ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,bmp,tiff,webp  # Allowed file types
IMAGES_MAX_FILE_SIZE=16777216              # Maximum file size in bytes (16MB)
```

#### Speech2Text Service
```bash
JWT_SECRET_KEY=your-secret-key             # JWT token secret
WHISPER_MODEL=base                         # Whisper model size
```

### Extraction Parameters

The system supports configurable extraction fields:

**Default Fields:**
- `person_name` - Names of individuals involved
- `vehicle_number` - License plate numbers
- `vehicle_make` - Vehicle manufacturer/brand
- `vehicle_color` - Vehicle color
- `vehicle_model` - Vehicle model/series
- `location` - Incident locations
- `event_crime_violation` - Type of incident/violation

**Vehicle Analysis Fields:**
- `vehicle_registration` - License plate recognition
- `vehicle_make` - Manufacturer identification
- `vehicle_color` - Color detection
- `vehicle_model` - Model recognition
- `vehicle_type` - Vehicle classification
- `vehicle_year` - Year estimation
- `vehicle_condition` - Condition assessment

**Document Analysis Fields:**
- `document_type` - Type identification (passport, license, ID)
- `name` - Full name extraction
- `date_of_birth` - Birth date recognition
- `country` - Country information
- `date_of_issue` - Issue date extraction
- `expiry_date` - Expiration date recognition
- `address` - Address information
- `gender` - Gender identification
- `place_of_birth` - Birth place extraction
- `issuing_authority` - Authority information
- `nationality` - Nationality extraction
- `pin_code` - Postal/ZIP code recognition

### Image Management Configuration

The Officer Insight API image management system supports configurable parameters through environment variables.

#### Configurable Parameters

**1. Upload Base Path**
- **Environment Variable**: `IMAGES_UPLOAD_BASE_PATH`
- **Default**: `/app/data/images`
- **Description**: Base directory for storing uploaded images
- **Example**: `IMAGES_UPLOAD_BASE_PATH=/custom/upload/path`

**2. Allowed File Extensions**
- **Environment Variable**: `IMAGES_ALLOWED_EXTENSIONS`
- **Default**: `jpg,jpeg,png,gif,bmp,tiff`
- **Description**: Comma-separated list of allowed file extensions
- **Example**: `IMAGES_ALLOWED_EXTENSIONS=jpg,png,webp,avif`

**3. Maximum File Size**
- **Environment Variable**: `IMAGES_MAX_FILE_SIZE`
- **Default**: `16777216` (16MB)
- **Description**: Maximum file size in bytes
- **Example**: `IMAGES_MAX_FILE_SIZE=33554432` (32MB)

#### Customization Examples

**Large File Support:**
```yaml
environment:
  IMAGES_MAX_FILE_SIZE: 104857600  # 100MB
  IMAGES_ALLOWED_EXTENSIONS: jpg,jpeg,png,gif,bmp,tiff,webp,raw,cr2,nef
```

**Restricted File Types:**
```yaml
environment:
  IMAGES_ALLOWED_EXTENSIONS: jpg,png
  IMAGES_MAX_FILE_SIZE: 5242880  # 5MB
```

**Custom Upload Directory:**
```yaml
environment:
  IMAGES_UPLOAD_BASE_PATH: /mnt/shared/images
volumes:
  - /host/shared/images:/mnt/shared/images
```

#### API Impact

These configuration changes affect the following endpoints:
- `POST /api/images/upload` - File validation and storage
- `GET /api/images/health` - Reports current configuration
- `GET /api/images/serve/{path}` - File serving from configured path

#### Health Check Response

The health endpoint returns current configuration:
```json
{
  "status": "healthy",
  "upload_directory": "/app/data/images",
  "allowed_extensions": ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"],
  "max_file_size": 16777216
}
```

#### Validation Rules

1. **File Size**: Files exceeding `IMAGES_MAX_FILE_SIZE` are rejected
2. **File Extensions**: Only files with extensions in `IMAGES_ALLOWED_EXTENSIONS` are accepted
3. **Upload Path**: Directory is created automatically if it doesn't exist
4. **Security**: File names are sanitized and given unique UUIDs

#### Deployment Considerations

1. **Volume Mapping**: Ensure Docker volumes match `IMAGES_UPLOAD_BASE_PATH`
2. **Permissions**: Upload directory must be writable by the application
3. **Storage**: Consider available disk space when setting large file size limits
4. **Security**: Restrict file extensions based on security requirements

## 🔧 Development

### Local Development Setup

1. **Set up Python environment:**
```bash
cd car-identifier-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Run individual services:**
```bash
# Document Reader Service
cd doc-reader-service && python app.py

# Car Identifier Service
cd car-identifier-service && python app.py

# Officer Insight API
cd officer-insight-api && python app.py

# Speech2Text Service
cd speech2text-service && python app.py
```

### Testing

#### Automated Testing
```bash
# Test all services
python tests/test_deployment.py

# Test specific endpoints
curl http://localhost:8654/api/public/health
curl http://localhost:8653/api/public/health
curl http://localhost:8650/api/public/health
curl http://localhost:8652/api/public/health
```

#### API Testing with Postman Collections

The `postman/` directory contains comprehensive collections for testing all services:

**Service-Specific Collections:**
- `Officer-Insight-API-Complete.json` - Complete Officer API testing (Images, Persons, Vehicles)
- `Car-Identifier-Service.json` - Vehicle identification service
- `Doc-Reader-Service.json` - Document parsing service  
- `Speech2Text-Service.json` - Audio transcription service

**System Collections:**
- `Complete-System-Collection.json` - Full integration testing across all services
- `Insight-API-Test-Collection.json` - Legacy comprehensive test suite

**Quick Start:**
1. Import desired collection(s) into Postman
2. Run "Admin Login" to get authentication token
3. Execute health checks to verify all services
4. Test individual features as needed

See [Postman Collections Guide](./postman/README.md) for detailed instructions.

## 📊 Monitoring & Health Checks

### Service Health Endpoints
- Officer API: `GET /api/public/health`
- Car Identifier: `GET /api/public/health`
- Document Reader: `GET /api/public/health`
- Speech2Text: `GET /api/public/health`

### Logging
- Request/response logging
- Error tracking and reporting
- Performance metrics
- Database operation logs

### Database Monitoring
- MongoDB connection status
- Collection statistics
- Query performance metrics
- Storage utilization

## 🔒 Security Features & Best Practices

- **Authentication**: JWT Bearer token authentication for all endpoints
- **Authorization**: Role-based access control (Admin/User roles)
- **Public Endpoints**: Only `/health` and `/auth` endpoints are publicly accessible
- **Token Validation**: All API requests require valid JWT tokens
- **Secure Headers**: CORS protection and input validation
- **Authorization**: Role-based access control
- **Input Validation**: File type and size restrictions
- **CORS Protection**: Configurable cross-origin policies
- **Error Handling**: Secure error messages without information leakage
- **Rate Limiting**: Protection against abuse (configurable)
- **Data Privacy**: 
  - No sensitive user data logged
  - Automatic exclusion of personal documents from git repository
  - Secure handling of extracted personal information
  - Configurable data retention policies

### 🚨 Security Guidelines

⚠️ **IMPORTANT**: This system processes sensitive personal information including:
- Identity documents (passports, driver's licenses)
- Personal photos extracted from documents
- Vehicle registration information
- Audio recordings containing personal data

**Best Practices:**
1. **Never commit test files containing real personal data**
2. **Use anonymized/synthetic test data for development**
3. **Run security check before committing**: `./scripts/security-check.sh`
4. **Implement proper data retention and deletion policies**
5. **Ensure secure transmission (HTTPS) in production**
6. **Regular security audits and vulnerability assessments**
7. **Proper access controls and user authentication**

### 🔍 Pre-Commit Security Check

Before committing any changes, run the security check script:

```bash
./scripts/security-check.sh
```

This script will:
- Check for personal document images
- Scan for potential real personal data patterns
- Identify large image files that might be real documents
- Warn about files that need review

## 📈 Performance Optimization

- **Microservices Architecture**: Independent scaling of components
- **Connection Pooling**: Efficient database connections
- **Async Processing**: Non-blocking operations where possible
- **Caching**: Response caching for repeated requests
- **Resource Management**: Memory and CPU optimization

## 🗄️ Database Schema

### Collections
- **users**: User accounts and authentication
- **parameters**: Configurable extraction parameters
- **extractions**: Processed data and results
- **requests**: API request logs and audit trails

### Data Models
- Extraction results with timestamps
- User activity tracking
- System configuration history
- Error logs and debugging information

## 📚 Additional Documentation

- [API Documentation](./API_DOCUMENTATION.md) - Detailed API reference
- [Car Identifier Service](./car-identifier-service/README.md) - Vehicle analysis service guide
- [Document Reader Service](./doc-reader-service/README.md) - Document parsing service guide
- [Deployment Guide](./DEPLOYMENT.md) - Production deployment instructions
- [Postman Testing](./POSTMAN_TESTING_GUIDE.md) - API testing with Postman
- [Postman Collections](./postman/README.md) - Complete collection guide
- [Changelog](./CHANGELOG.md) - Version history and updates
- [Project Status](./PROJECT_STATUS.md) - Current development status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes and add tests
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/new-feature`)
6. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support & Troubleshooting

### Common Issues

1. **Service connectivity issues**
   - Verify Docker containers are running
   - Check network configuration
   - Review service logs

2. **AI model errors**
   - Ensure Ollama is running and models are installed
   - Check model compatibility
   - Verify timeout settings

3. **Database connection problems**
   - Confirm MongoDB is accessible
   - Validate connection strings
   - Check authentication credentials

### Getting Help
- Check the troubleshooting guides in individual service READMEs
- Review service logs: `docker logs <container-name>`
- Submit issues to the project repository
- Check the project documentation and wiki

## 🚀 Roadmap

- **Real-time Processing**: WebSocket support for live updates
- **Enhanced AI Models**: Integration of newer vision and language models
- **Advanced Analytics**: Machine learning insights and reporting
- **Mobile Integration**: Mobile API optimization and SDKs
- **Cloud Deployment**: Kubernetes deployment configurations
- **API Gateway**: Centralized API management and routing
