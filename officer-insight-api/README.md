# Officer Insight API

A REST API service for processing audio files and text messages to extract structured information using AI.

## Features

- **Audio to Text Conversion**: Convert audio files to text using Speech2Text service
- **Information Extraction**: Extract structured information using Ollama AI (llama3.2:latest model)
- **Enhanced Prompt Engineering**: Optimized prompts for traffic offense report parsing
- **Admin Panel Integration**: Secure admin APIs for managing extraction parameters
- **Health Monitoring**: Built-in health check endpoints
- **JWT Authentication**: Secure authentication for admin operations
- **Swagger Documentation**: Complete API documentation
- **MongoDB Integration**: Persistent storage for extracted data
- **Request Logging**: Track all API requests and responses

## API Endpoints

### Public APIs

- `POST /api/parse-message` - Parse text message or audio file
- `GET /api/health` - Health check endpoint

### Authentication

- `POST /api/auth/login` - Authenticate and get JWT token

### Admin APIs (Requires JWT)

- `GET /api/admin/parameters` - List extraction parameters
- `POST /api/admin/parameters` - Create new parameter
- `PUT /api/admin/parameters/{id}` - Update parameter
- `DELETE /api/admin/parameters/{id}` - Delete parameter
- `GET /api/admin/requests` - List API requests with pagination
- `GET /api/admin/users` - List users with pagination
- `POST /api/admin/users` - Create new user
- `PUT /api/admin/users/{id}` - Update user
- `DELETE /api/admin/users/{id}` - Delete user
- `GET /api/admin/dashboard` - Get dashboard statistics

## Default Extraction Parameters

The service extracts the following information by default:

- **person_name**: Name of the person involved
- **vehicle_number**: Vehicle license plate number
- **car_color**: Color of the vehicle
- **car_model**: Model of the vehicle
- **location**: Location where incident occurred
- **event_crime_violation**: Type of event, crime or violation

## Authentication

### Default Admin Credentials
- **Username**: admin
- **Password**: Apple@123

### JWT Token Usage
Include the JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Request Examples

### Parse Text Message
```bash
curl -X POST http://localhost:8650/api/parse-message \
  -F "message=Red Toyota Camry license plate ABC123 was involved in an accident at Main Street"
```

### Parse Audio File
```bash
curl -X POST http://localhost:8650/api/parse-message \
  -F "audio_message=@audio_file.wav"
```

### Admin Login
```bash
curl -X POST http://localhost:8650/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Apple@123"}'
```

### Get Parameters (Admin)
```bash
curl -X GET http://localhost:8650/api/admin/parameters \
  -H "Authorization: Bearer <jwt-token>"
```

## Environment Variables

- `MONGODB_URI`: MongoDB connection string
- `SPEECH2TEXT_API_URL`: Speech2Text service URL
- `SPEECH2TEXT_API_TOKEN`: Authentication token for Speech2Text service
- `OLLAMA_URL`: Ollama AI service URL (default: http://host.docker.internal:11434)
- `OLLAMA_MODEL`: Ollama model name (default: llama3.2:latest)
- `JWT_SECRET_KEY`: Secret key for JWT tokens

## Dependencies

- Flask 2.3.3
- Flask-PyMongo 2.3.0
- Flask-JWT-Extended 4.5.3
- Flask-CORS 4.0.0
- flask-restx 1.2.0
- pymongo 4.5.0
- bcrypt 4.0.1
- requests 2.31.0

## Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export MONGODB_URI="mongodb://admin:Apple@123@localhost:27017/insight_db?authSource=admin"
export SPEECH2TEXT_API_URL="http://localhost:8652"
export SPEECH2TEXT_API_TOKEN="insight_speech_token_2024"
export OLLAMA_URL="http://host.docker.internal:11434"
```

3. Run the application:
```bash
python app.py
```

The service will be available at http://localhost:8650

## API Documentation

Once the service is running, visit http://localhost:8650/docs/ for interactive API documentation.

## Health Check

The service provides a comprehensive health check at `/api/health` that monitors:
- Database connectivity
- Speech2Text service availability
- Overall service status

## Error Handling

The API returns appropriate HTTP status codes and error messages:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

## Logging

All API requests are logged to the database with:
- Endpoint accessed
- Status (success/error)
- Timestamp
- Additional metadata (extraction ID, error details)

## Data Storage

Extracted information is stored in MongoDB with the following structure:
```json
{
  "_id": "ObjectId",
  "original_text": "string",
  "extracted_info": {
    "person_name": "string or null",
    "vehicle_number": "string or null",
    "car_color": "string or null",
    "car_model": "string or null",
    "location": "string or null",
    "event_crime_violation": "string or null"
  },
  "has_audio": "boolean",
  "created_at": "datetime"
}
```
