# Insight API - Complete API Documentation

## Overview

The Insight API is a comprehensive microservices-based system for processing audio files and text messages to extract structured information using Ollama AI. This documentation covers all API endpoints, authentication methods, and integration examples.

## System Architecture

### Services Overview
- **Officer Insight API** (Port 8650): Main REST API service
- **Speech2Text Service** (Port 8652): Audio processing and AI text extraction
- **Admin UI** (Port 8651): React-based administrative interface
- **MongoDB** (Port 27017): Database service

### AI Integration
- **Ollama AI**: llama3.2:latest model running on http://host.docker.internal:11434
- **Enhanced Prompt Engineering**: Optimized for traffic offense report parsing
- **Structured Data Extraction**: Converts unstructured text into organized fields

## Officer Insight API (Port 8650)

### Base URL
```
http://localhost:8650/api
```

### Authentication

#### Login
**Endpoint:** `POST /auth/login`

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
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "user_id",
    "username": "admin",
    "role": "admin"
  }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8650/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Apple@123"}'
```

### Public Endpoints

#### Parse Message
**Endpoint:** `POST /public/parse-message`

**Description:** Process text messages or audio files to extract structured information.

**Content-Type:** `application/x-www-form-urlencoded` or `multipart/form-data`

**Parameters:**
- `message` (string, optional): Text message to process
- `audio_message` (file, optional): Audio file to process

**Text Message Example:**
```bash
curl -X POST http://localhost:8650/api/public/parse-message \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=Officer observed a red Honda Civic with license plate ABC-123 speeding at 65 mph in a 45 mph zone on Main Street at 3:30 PM on October 15th, 2023. Driver identified as John Smith, DOB 03/15/1985."
```

**Audio File Example:**
```bash
curl -X POST http://localhost:8650/api/public/parse-message \
  -F "audio_message=@traffic_report.wav"
```

**Response:**
```json
{
  "id": "extraction_id",
  "text": "Officer observed a red Honda Civic...",
  "processed_output": "Offence Category: Speeding\nDriver Name: John Smith\nDate Of Birth: 15/03/1985\nLocation Of Offence: Main Street\nOffence Occurred At: 3:30 PM, October 15th, 2023\nOffence: Speeding at 65 mph in a 45 mph zone\nVehicle Registration: ABC-123\nVehicle Manufacturer: Honda\nVehicle Model: Civic (Red)",
  "extracted_info": {
    "offence_category": "Speeding",
    "driver_name": "John Smith",
    "date_of_birth": "15/03/1985",
    "location_of_offence": "Main Street",
    "offence_occurred_at": "3:30 PM, October 15th, 2023",
    "offence": "Speeding at 65 mph in a 45 mph zone",
    "vehicle_registration": "ABC-123",
    "vehicle_manufacturer": "Honda",
    "vehicle_model": "Civic (Red)"
  }
}
```

#### Health Check
**Endpoint:** `GET /public/health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-12T10:30:00Z",
  "services": {
    "database": "healthy",
    "speech2text": "healthy"
  }
}
```

### Admin Endpoints (Requires JWT)

#### Dashboard Statistics
**Endpoint:** `GET /admin/dashboard`

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "total_requests": 150,
  "successful_requests": 142,
  "failed_requests": 8,
  "success_rate": 94.67,
  "recent_extractions": [...],
  "request_status_distribution": [
    {"status": "success", "count": 142},
    {"status": "error", "count": 8}
  ]
}
```

#### Parameter Management

**List Parameters:** `GET /admin/parameters`
**Create Parameter:** `POST /admin/parameters`
**Update Parameter:** `PUT /admin/parameters/{id}`
**Delete Parameter:** `DELETE /admin/parameters/{id}`

**Parameter Object:**
```json
{
  "name": "driver_license",
  "description": "Driver's license number",
  "active": true
}
```

#### Request Monitoring

**List Requests:** `GET /admin/requests`

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 10)
- `status` (string): Filter by status (success/error)

#### User Management

**List Users:** `GET /admin/users`
**Create User:** `POST /admin/users`
**Update User:** `PUT /admin/users/{id}`
**Delete User:** `DELETE /admin/users/{id}`

## Speech2Text Service (Port 8652)

### Base URL
```
http://localhost:8652/api
```

### Authentication
All endpoints (except health) require Bearer token authentication:
```
Authorization: Bearer insight_speech_token_2024
```

### Endpoints

#### Convert Audio with AI Processing
**Endpoint:** `POST /convert`

**Description:** Convert audio file to text and process with Ollama AI for structured extraction.

**Content-Type:** `multipart/form-data`

**Parameters:**
- `audio_file` (file, optional): Audio file to convert
- `text_message` (string, optional): Additional text to process

**Example:**
```bash
curl -X POST http://localhost:8652/api/convert \
  -H "Authorization: Bearer insight_speech_token_2024" \
  -F "audio_file=@recording.wav"
```

**Response:**
```json
{
  "text": "Officer Johnson stopped a blue Toyota Camry license plate XYZ789 for speeding",
  "processed_output": "Offence Category: Speeding\nVehicle Manufacturer: Toyota\nVehicle Model: Camry (Blue)\nVehicle Registration: XYZ789",
  "file_id": "uuid-generated-id",
  "timestamp": "2025-08-12T10:30:00Z"
}
```

#### Process Text with AI
**Endpoint:** `POST /process-text`

**Description:** Process text directly with Ollama AI for structured information extraction.

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "text": "Officer Smith observed a white BMW speeding at 70 mph in a 55 mph zone"
}
```

**Example:**
```bash
curl -X POST http://localhost:8652/api/process-text \
  -H "Authorization: Bearer insight_speech_token_2024" \
  -H "Content-Type: application/json" \
  -d '{"text": "Officer Smith observed a white BMW speeding at 70 mph in a 55 mph zone"}'
```

**Response:**
```json
{
  "text": "Officer Smith observed a white BMW speeding at 70 mph in a 55 mph zone",
  "processed_output": "Offence Category: Speeding\nVehicle Manufacturer: BMW\nVehicle Model: BMW (White)\nOffence: Speeding at 70 mph in a 55 mph zone",
  "file_id": null,
  "timestamp": "2025-08-12T10:30:00Z"
}
```

#### Health Check with Ollama Status
**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-12T10:30:00Z",
  "ollama": {
    "url": "http://host.docker.internal:11434",
    "model": "llama3.2:latest",
    "status": "healthy"
  },
  "storage": {
    "audio_directory": true,
    "temp_directory": true,
    "free_space_gb": 25.6
  },
  "dependencies": {
    "ffmpeg": true
  }
}
```

## Structured Data Extraction

### Default Extraction Fields

The Ollama AI model is optimized to extract the following information from traffic offense reports:

- **Offence Category**: Type of traffic violation
- **Driver Name**: Full name of the driver
- **Date Of Birth**: Driver's date of birth (DD/MM/YYYY format)
- **Gender**: Driver's gender
- **Address**: Driver's address
- **Location Of Offence**: Where the offense occurred
- **Offence Occurred At**: Date and time of the offense
- **Offence**: Specific description of the violation
- **Vehicle Registration**: License plate number
- **Vehicle Manufacturer**: Car manufacturer/brand
- **Vehicle Model**: Car model and color

### Enhanced Prompt Engineering

The system uses carefully crafted prompts to ensure consistent and accurate extraction:

```
You are an expert at extracting structured information from police reports and incident descriptions.

Parse the following text and extract information in the exact format shown in the example:

Input text: {user_text}

Please extract and format the information as follows:
- Offence Category: [type of offence]
- Driver Name: [full name]
- Date of Birth: [DD/MM/YYYY format]
- Gender: [Male/Female/Other]
- Address: [full address]
- Location of Offence: [location where offence occurred]
- Offence Occurred at: [time and date]
- Offence: [specific offence description]
- Vehicle Registration: [registration number]
- Vehicle Manufacturer: [car manufacturer]
- Vehicle Model: [car model and color]

Only include fields that are mentioned in the text. If information is not available, omit that field.
Format the response exactly as shown above with each field on a new line.
```

## Error Handling

### HTTP Status Codes

- **200**: Success
- **400**: Bad Request (missing parameters, invalid data)
- **401**: Unauthorized (invalid credentials/token)
- **404**: Not Found (resource doesn't exist)
- **500**: Internal Server Error (processing failure)

### Error Response Format

```json
{
  "message": "Error description",
  "details": "Additional error details (optional)"
}
```

### Common Error Scenarios

#### Authentication Errors
```json
{
  "message": "Invalid or missing API token"
}
```

#### File Processing Errors
```json
{
  "message": "Unsupported audio format",
  "details": "Supported formats: WAV, MP3, MP4, FLAC"
}
```

#### AI Processing Errors
```json
{
  "message": "Failed to process text with Ollama",
  "details": "Ollama service unavailable"
}
```

## Integration Examples

### Complete Workflow Example

```bash
# 1. Login to get JWT token
TOKEN=$(curl -s -X POST http://localhost:8650/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Apple@123"}' | \
  jq -r '.access_token')

# 2. Process a traffic report
curl -X POST http://localhost:8650/api/public/parse-message \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=Officer conducted traffic stop of red Honda Civic, plate ABC123, driver John Smith, speeding 65 in 45 zone on Main St at 2:30 PM"

# 3. Check dashboard statistics
curl -X GET http://localhost:8650/api/admin/dashboard \
  -H "Authorization: Bearer $TOKEN"

# 4. Process audio file directly
curl -X POST http://localhost:8652/api/convert \
  -H "Authorization: Bearer insight_speech_token_2024" \
  -F "audio_file=@traffic_report.wav"
```

### JavaScript Integration Example

```javascript
// Authentication
const login = async () => {
  const response = await fetch('http://localhost:8650/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: 'admin',
      password: 'Apple@123'
    })
  });
  const data = await response.json();
  return data.access_token;
};

// Process text message
const processMessage = async (message) => {
  const formData = new FormData();
  formData.append('message', message);
  
  const response = await fetch('http://localhost:8650/api/public/parse-message', {
    method: 'POST',
    body: formData
  });
  return await response.json();
};

// Process audio file
const processAudio = async (audioFile) => {
  const formData = new FormData();
  formData.append('audio_file', audioFile);
  
  const response = await fetch('http://localhost:8652/api/convert', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer insight_speech_token_2024'
    },
    body: formData
  });
  return await response.json();
};
```

### Python Integration Example

```python
import requests

# Authentication
def login():
    response = requests.post('http://localhost:8650/api/auth/login', 
                           json={'username': 'admin', 'password': 'Apple@123'})
    return response.json()['access_token']

# Process text message
def process_message(message):
    data = {'message': message}
    response = requests.post('http://localhost:8650/api/public/parse-message', 
                           data=data)
    return response.json()

# Process audio file
def process_audio(audio_file_path):
    with open(audio_file_path, 'rb') as f:
        files = {'audio_file': f}
        headers = {'Authorization': 'Bearer insight_speech_token_2024'}
        response = requests.post('http://localhost:8652/api/convert', 
                               files=files, headers=headers)
        return response.json()

# Example usage
if __name__ == "__main__":
    # Process text
    result = process_message("Officer stopped red car ABC123 for speeding")
    print("Text processing result:", result)
    
    # Process audio
    audio_result = process_audio("traffic_report.wav")
    print("Audio processing result:", audio_result)
```

## Rate Limiting and Performance

### Current Limits
- No explicit rate limiting implemented
- File size limit: 100MB for audio files
- Processing timeout: 2 minutes per request
- Concurrent request handling: Limited by container resources

### Performance Optimization
- Audio files are processed asynchronously
- Ollama AI responses are cached for identical inputs
- Database queries are optimized with proper indexing
- Container resources can be scaled based on load

## Monitoring and Logging

### Health Check Endpoints
- Officer Insight API: `GET /api/public/health`
- Speech2Text Service: `GET /api/health`
- Admin UI: `GET /health`

### Request Logging
All API requests are logged with:
- Timestamp
- Endpoint
- Status (success/error)
- Processing time
- User information (for authenticated requests)

### Metrics Available
- Total requests processed
- Success/failure rates
- Average processing times
- Resource utilization
- Ollama AI response times

## Security Considerations

### Authentication Methods
- JWT tokens for admin operations (24-hour expiry)
- Bearer tokens for service-to-service communication
- bcrypt password hashing for user accounts

### Data Protection
- Input validation on all endpoints
- File type verification for uploads
- SQL injection prevention
- XSS protection in responses

### Network Security
- CORS configuration for cross-origin requests
- HTTPS recommended for production
- Service isolation through Docker networking

## Support and Troubleshooting

### Common Issues

1. **Ollama Connection Failures**
   - Verify Ollama is running on http://host.docker.internal:11434
   - Check network connectivity between containers
   - Ensure llama3.2:latest model is available

2. **Audio Processing Errors**
   - Verify supported audio formats (WAV, MP3, MP4, FLAC)
   - Check file size limits (100MB max)
   - Ensure FFmpeg is properly installed

3. **Authentication Issues**
   - Verify JWT token hasn't expired
   - Check Bearer token format
   - Ensure correct credentials

4. **Performance Issues**
   - Monitor container resource usage
   - Check Ollama AI response times
   - Verify database connectivity

### Getting Help
- Check service logs: `docker logs [container-name]`
- Review API documentation at `/docs/` endpoints
- Monitor health check endpoints
- Check GitHub repository for updates

This comprehensive API documentation provides all the information needed to integrate with and use the Insight API system effectively.
