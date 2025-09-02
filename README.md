# Officer Insight API System

## 🎯 Overview

Officer Insight API is a comprehensive microservices-based system designed to assist law enforcement officers in processing and extracting structured information from various data sources including text reports, audio recordings, and vehicle images. The system leverages advanced AI models for speech-to-text conversion, text processing, and computer vision analysis.

## 🏗️ System Architecture

The system consists of five main microservices:

### 🔧 Officer Insight API (Port 8650)
- **Purpose**: Core API service for text/audio processing and system coordination
- **Features**: JWT authentication, user management, text extraction, audio-to-text conversion
- **AI Model**: Llama3.2:latest for text processing
- **Database**: MongoDB for data persistence

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

### 🎤 Speech2Text Service (Port 8652)
- **Purpose**: Audio processing and speech-to-text conversion
- **Features**: Multi-format audio support, Whisper AI integration
- **AI Model**: OpenAI Whisper for speech recognition
- **Formats**: WAV, MP3, M4A, FLAC, OGG

### 🖥️ Admin UI (Port 8651)
- **Purpose**: Web-based administration interface
- **Features**: User management, system monitoring, data visualization
- **Technology**: React.js with Material-UI
- **Authentication**: JWT-based secure access

## ✨ Key Features

### 🎯 Core Capabilities
- **Multi-Source Data Processing**: Text, audio, image, and document inputs
- **AI-Powered Analysis**: Advanced machine learning models for accurate extraction
- **Document Intelligence**: Automated parsing of identity documents, certificates, and forms
- **Vehicle Recognition**: Comprehensive vehicle identification and analysis
- **Structured Data Output**: Consistent JSON format for all extractions
- **Real-time Processing**: Fast response times for immediate insights
- **Microservices Architecture**: Scalable and maintainable design

### 🔒 Security & Authentication
- JWT-based authentication system
- Role-based access control (Admin/User)
- Secure API endpoints with CORS protection
- Input validation and sanitization

### 📊 Data Management
- MongoDB integration for persistent storage
- Request logging and audit trails
- Extraction history and analytics
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
  - `gemma3:12b` (for vehicle identification)
  - `llama3.2:latest` (for text processing)

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
curl http://localhost:8650/api/public/health  # Officer API
curl http://localhost:8653/api/public/health  # Car Identifier
curl http://localhost:8652/api/health         # Speech2Text
```

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

### Text Processing
```bash
curl -X POST "http://localhost:8650/api/public/parse-message" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=Officer Johnson reporting traffic violation. Red Honda Civic plate ABC123 speeding in school zone."
```

### Document Processing (with optional parameters)
```bash
# Extract both person image and text information (default)
curl -X POST "http://localhost:8654/api/public/doc-reader" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/document/passport.pdf"

# Extract only text information
curl -X POST "http://localhost:8654/api/public/doc-reader" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/document/passport.pdf" \
  -F "extract_person_image=false" \
  -F "extract_text_info=true"

# Extract only person image
curl -X POST "http://localhost:8654/api/public/doc-reader" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/document/passport.pdf" \
  -F "extract_person_image=true" \
  -F "extract_text_info=false"
```

### Vehicle Image Analysis
```bash
curl -X POST "http://localhost:8653/api/public/car-identifier" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@path/to/vehicle/image.jpg"
```

### Audio Processing
```bash
curl -X POST "http://localhost:8650/api/public/parse-message" \
  -H "Content-Type: multipart/form-data" \
  -F "audio_message=@path/to/audio/report.wav"
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

```bash
# Test all services
python test_deployment.py

# Test specific endpoints
curl http://localhost:8654/api/public/health
curl http://localhost:8653/api/public/health
curl http://localhost:8650/api/public/health
curl http://localhost:8652/api/health
```

## 📊 Monitoring & Health Checks

### Service Health Endpoints
- Officer API: `GET /api/public/health`
- Car Identifier: `GET /api/public/health`
- Document Reader: `GET /api/public/health`
- Speech2Text: `GET /api/health`

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

- **Authentication**: JWT-based token authentication
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
