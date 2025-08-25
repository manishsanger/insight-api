# Officer Insight API System - Complete API Documentation

## Overview

The Officer Insight API System is a comprehensive microservices architecture designed for law enforcement data processing. The system uses advanced AI models for text processing, speech recognition, and computer vision to extract structured information from various data sources.

## System Architecture

### Services Overview
- **Officer Insight API** (Port 8650): Core text/audio processing and system coordination
- **Car Identifier Service** (Port 8653): Specialized vehicle image analysis using Gemma3:12b
- **Speech2Text Service** (Port 8652): Audio processing using Whisper AI
- **Admin UI** (Port 8651): React-based administrative interface
- **MongoDB** (Port 27017): Database service for data persistence

### AI Integration
- **Gemma3:12b**: Vision model for vehicle identification and analysis
- **Llama3.2:latest**: Language model for text processing and information extraction
- **Whisper AI**: Speech-to-text conversion for audio files
- **Ollama**: Local AI model serving platform

## Service URLs

- **Officer Insight API**: `http://localhost:8650`
- **Car Identifier Service**: `http://localhost:8653`
- **Speech2Text Service**: `http://localhost:8652`
- **Admin UI**: `http://localhost:8651`

## Authentication

Most endpoints require JWT authentication. Obtain a token through the login endpoint:

### Login
**Endpoint:** `POST http://localhost:8650/api/auth/login`

**Request:**
```json
{
  "username": "admin",
  "password": "Apple@123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "role": "admin"
}
```

**Usage:**
```bash
Authorization: Bearer <access_token>
```

## Officer Insight API (Port 8650)

### Base URL
```
http://localhost:8650/api
```

### Public Endpoints

#### Parse Message
**Endpoint:** `POST /public/parse-message`

Process text message or audio file and extract structured information.

**Request (Text):**
```bash
curl -X POST "http://localhost:8650/api/public/parse-message" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=Officer Johnson reporting traffic violation. Red Honda Civic plate ABC123 speeding in school zone."
```

**Request (Audio):**
```bash
curl -X POST "http://localhost:8650/api/public/parse-message" \
  -H "Content-Type: multipart/form-data" \
  -F "audio_message=@path/to/audio/file.wav"
```

**Response:**
```json
{
  "id": "66f1a2b3c4d5e6f7g8h9i0j1",
  "text": "Officer Johnson reporting traffic violation. Red Honda Civic plate ABC123 speeding in school zone.",
  "processed_output": "- Offence Category: Traffic Violation\n- Driver Name: Not mentioned\n- Vehicle Registration: ABC123\n- Vehicle Make: Honda\n- Vehicle Color: Red\n- Vehicle Model: Civic\n- Location of Offence: school zone\n- Offence: speeding",
  "extracted_info": {
    "offence_category": "Traffic Violation",
    "vehicle_registration": "ABC123", 
    "vehicle_make": "Honda",
    "vehicle_color": "Red",
    "vehicle_model": "Civic",
    "location_of_offence": "school zone",
    "offence": "speeding"
  }
}
```

#### Health Check
**Endpoint:** `GET /public/health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-22T10:30:00Z",
  "services": {
    "database": "healthy",
    "speech2text": "healthy"
  }
}
```

### Admin Endpoints (JWT Required)

#### Get Parameters
**Endpoint:** `GET /admin/parameters`

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "data": [
    {
      "id": "66f1a2b3c4d5e6f7g8h9i0j1",
      "_id": "66f1a2b3c4d5e6f7g8h9i0j1",
      "name": "person_name",
      "description": "Name of the person involved",
      "active": true,
      "created_at": "2025-08-22T10:30:00Z"
    }
  ]
}
```

#### Create Parameter
**Endpoint:** `POST /admin/parameters`

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request:**
```json
{
  "name": "incident_time",
  "description": "Time when incident occurred",
  "active": true
}
```

#### Get Requests Log
**Endpoint:** `GET /admin/requests`

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)
- `start_date` (optional): Start date filter (ISO format)
- `end_date` (optional): End date filter (ISO format)

**Response:**
```json
{
  "data": [
    {
      "id": "66f1a2b3c4d5e6f7g8h9i0j1",
      "endpoint": "/api/public/parse-message",
      "status": "success",
      "extraction_id": "66f1a2b3c4d5e6f7g8h9i0j2",
      "created_at": "2025-08-22T10:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 10,
  "pages": 15
}
```

#### Dashboard Statistics
**Endpoint:** `GET /admin/dashboard`

**Query Parameters:**
- `start_date` (optional): Start date filter
- `end_date` (optional): End date filter

**Response:**
```json
{
  "total_requests": 1250,
  "successful_requests": 1180,
  "error_requests": 70,
  "success_rate": 94.4
}
```

## Car Identifier Service (Port 8653)

### Base URL
```
http://localhost:8653/api
```

### Public Endpoints

#### Vehicle Image Analysis
**Endpoint:** `POST /public/car-identifier`

Analyze vehicle image using Gemma3:12b vision model.

**Request:**
```bash
curl -X POST "http://localhost:8653/api/public/car-identifier" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@path/to/vehicle/image.jpg"
```

**Supported Formats:**
- JPG, JPEG, PNG, GIF, BMP, WEBP
- Maximum file size: 16MB

**Response:**
```json
{
  "id": "66f1a2b3c4d5e6f7g8h9i0j1",
  "filename": "vehicle_image.jpg",
  "model": "gemma3:12b",
  "service": "car-identifier-service",
  "extraction_fields": [
    "vehicle_registration",
    "vehicle_make", 
    "vehicle_color",
    "vehicle_model"
  ],
  "processed_output": "- Vehicle Make: BMW\n- Vehicle Color: Blue\n- Vehicle Model: 320i\n- Vehicle Registration: XYZ789",
  "extracted_info": {
    "vehicle_make": "BMW",
    "vehicle_color": "Blue", 
    "vehicle_model": "320i",
    "vehicle_registration": "XYZ789"
  }
}
```

#### Health Check
**Endpoint:** `GET /public/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "car-identifier-service",
  "model": "gemma3:12b",
  "extraction_fields": [
    "vehicle_registration",
    "vehicle_make",
    "vehicle_color", 
    "vehicle_model"
  ],
  "timestamp": "2025-08-22T10:30:00Z",
  "services": {
    "database": "healthy",
    "ollama": "healthy"
  }
}
```

## Speech2Text Service (Port 8652)

### Base URL
```
http://localhost:8652/api
```

### Public Endpoints

#### Convert Audio to Text
**Endpoint:** `POST /convert`

**Headers:**
```
Authorization: Bearer insight_speech_token_2024
```

**Request:**
```bash
curl -X POST "http://localhost:8652/api/convert" \
  -H "Authorization: Bearer insight_speech_token_2024" \
  -F "audio_file=@path/to/audio/file.wav"
```

**Supported Formats:**
- WAV, MP3, M4A, FLAC, OGG

**Response:**
```json
{
  "text": "Officer Johnson reporting a traffic violation on Main Street...",
  "filename": "report_audio.wav",
  "duration": 45.3,
  "processing_time": 8.7
}
```

#### Process Text with AI
**Endpoint:** `POST /process-text`

**Headers:**
```
Authorization: Bearer insight_speech_token_2024
Content-Type: application/json
```

**Request:**
```json
{
  "text": "Officer Johnson reporting traffic violation. Red Honda Civic plate ABC123 speeding in school zone."
}
```

**Response:**
```json
{
  "processed_output": "- Offence Category: Traffic Violation\n- Vehicle Registration: ABC123\n- Vehicle Make: Honda\n- Vehicle Color: Red\n- Vehicle Model: Civic\n- Location of Offence: school zone\n- Offence: speeding"
}
```

#### Health Check
**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "speech2text-service",
  "whisper_model": "base",
  "timestamp": "2025-08-22T10:30:00Z"
}
```

## Configuration

### Environment Variables

#### Car Identifier Service
```bash
VISION_MODEL=gemma3:12b
EXTRACTION_FIELDS=vehicle_registration,vehicle_make,vehicle_color,vehicle_model
MODEL_TIMEOUT=180
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,bmp,webp
MAX_CONTENT_LENGTH=16777216
CORS_ORIGINS=http://localhost:8651,http://localhost:3000
```

#### Officer Insight API
```bash
MONGODB_URI=mongodb://admin:Apple%40123@mongodb:27017/insight_db?authSource=admin
SPEECH2TEXT_API_URL=http://speech2text-service:8652
SPEECH2TEXT_API_TOKEN=insight_speech_token_2024
OLLAMA_URL=http://host.docker.internal:11434
JWT_SECRET_KEY=insight-api-jwt-secret-key-2024
```

#### Speech2Text Service
```bash
API_TOKEN=insight_speech_token_2024
WHISPER_MODEL=base
OLLAMA_URL=http://host.docker.internal:11434
```

### Configurable Extraction Fields

#### Default Text Extraction Fields
- `person_name` - Names of individuals involved
- `vehicle_number` - License plate numbers
- `vehicle_make` - Vehicle manufacturer/brand
- `vehicle_color` - Vehicle color
- `vehicle_model` - Vehicle model/series
- `location` - Incident locations
- `event_crime_violation` - Type of incident/violation

#### Vehicle Analysis Fields (Configurable)
- `vehicle_registration` - License plate recognition
- `vehicle_make` - Manufacturer identification
- `vehicle_color` - Color detection  
- `vehicle_model` - Model recognition
- `vehicle_type` - Vehicle classification
- `vehicle_year` - Year estimation
- `vehicle_condition` - Condition assessment

## Error Handling

### Standard Error Response Format
```json
{
  "message": "Error description",
  "error": "Detailed error information",
  "timestamp": "2025-08-22T10:30:00Z"
}
```

### Common HTTP Status Codes
- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Error Examples

#### Missing Authentication
```json
{
  "message": "Authentication required",
  "error": "Missing or invalid JWT token"
}
```

#### Invalid File Format
```json
{
  "message": "Invalid file type. Supported formats: jpg, jpeg, png, gif, bmp, webp"
}
```

#### Service Unavailable
```json
{
  "message": "Failed to process image with AI vision model",
  "error": "Ollama service unavailable"
}
```

## Rate Limiting

- **Default Limit**: 100 requests per minute per IP
- **Burst Limit**: 20 requests per second
- **Headers**: Rate limit information included in response headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1692705600
```

## Integration Examples

### Python Integration

```python
import requests
import json

# Authentication
auth_response = requests.post(
    "http://localhost:8650/api/auth/login",
    json={"username": "admin", "password": "Apple@123"}
)
token = auth_response.json()["access_token"]

# Text processing
text_response = requests.post(
    "http://localhost:8650/api/public/parse-message",
    data={"message": "Officer Johnson reporting traffic violation..."}
)

# Vehicle image analysis  
with open("vehicle.jpg", "rb") as image_file:
    car_response = requests.post(
        "http://localhost:8653/api/public/car-identifier",
        files={"image": image_file}
    )

# Audio processing
with open("report.wav", "rb") as audio_file:
    audio_response = requests.post(
        "http://localhost:8650/api/public/parse-message",
        files={"audio_message": audio_file}
    )

print("Vehicle info:", car_response.json()["extracted_info"])
```

### JavaScript/Node.js Integration

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

// Authentication
const authResponse = await axios.post('http://localhost:8650/api/auth/login', {
  username: 'admin',
  password: 'Apple@123'
});
const token = authResponse.data.access_token;

// Vehicle image analysis
const form = new FormData();
form.append('image', fs.createReadStream('vehicle.jpg'));

const carResponse = await axios.post(
  'http://localhost:8653/api/public/car-identifier',
  form,
  { headers: form.getHeaders() }
);

console.log('Vehicle info:', carResponse.data.extracted_info);
```

### cURL Examples

```bash
# Authentication
curl -X POST "http://localhost:8650/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Apple@123"}'

# Text processing
curl -X POST "http://localhost:8650/api/public/parse-message" \
  -d "message=Officer Johnson reporting traffic violation..."

# Vehicle image analysis
curl -X POST "http://localhost:8653/api/public/car-identifier" \
  -F "image=@vehicle.jpg"

# Audio processing  
curl -X POST "http://localhost:8650/api/public/parse-message" \
  -F "audio_message=@report.wav"

# Health checks
curl http://localhost:8650/api/public/health
curl http://localhost:8653/api/public/health
curl http://localhost:8652/api/health
```

## Performance Considerations

### Response Times
- **Text Processing**: ~2-5 seconds for typical police reports
- **Audio Processing**: ~10-30 seconds depending on file length  
- **Image Analysis**: ~5-15 seconds for vehicle identification
- **Health Checks**: <1 second

### Concurrent Requests
- All services support multiple concurrent requests
- Database connection pooling for optimal performance
- AI model queuing for resource management

### File Size Limits
- **Images**: 16MB maximum
- **Audio**: 100MB maximum  
- **Text**: 10KB maximum

## Testing

### Postman Collection
Import the provided Postman collection for comprehensive API testing:
- Collection file: `postman/Officer_Insight_API.postman_collection.json`
- Environment file: `postman/Officer_Insight_API.postman_environment.json`

### Automated Testing
```bash
# Run comprehensive tests
python test_deployment.py

# Test individual services
curl http://localhost:8650/api/public/health
curl http://localhost:8653/api/public/health  
curl http://localhost:8652/api/health
```

## Troubleshooting

### Common Issues

1. **Service connectivity issues**
   - Verify all containers are running: `docker ps`
   - Check network connectivity between services
   - Review service logs: `docker logs <container-name>`

2. **AI model errors**
   - Ensure Ollama is running with required models
   - Check model compatibility and resource usage
   - Verify timeout settings

3. **Authentication errors**
   - Verify JWT token is valid and not expired
   - Check token format in Authorization header
   - Ensure correct username/password

4. **File upload errors**
   - Verify file format is supported
   - Check file size limits
   - Ensure proper Content-Type headers

### Debug Endpoints

```bash
# Service health
GET /api/public/health    # Officer API & Car Identifier
GET /api/health          # Speech2Text Service

# Service logs (Docker)
docker logs insight-officer-api
docker logs insight-car-identifier  
docker logs insight-speech2text
```

## Support

For additional support:
- Check service-specific README files
- Review error logs for detailed information
- Submit issues to the project repository
- Consult the troubleshooting guides
