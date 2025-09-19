# Officer Insight API

A comprehensive Flask-based microservice for law enforcement data processing, including text/audio analysis, image management, person management, and vehicle management.

## Features

### Core Features
- **Audio to Text Conversion**: Process audio files to extract text using Speech2Text service
- **AI-Powered Information Extraction**: Extract structured information using Ollama AI
- **JWT Authentication**: Secure API access with role-based authentication
- **Admin Panel Integration**: Complete admin interface for system management

### New Features (v2.2.3+)
- **Image Management System**: Upload, store, and manage images with HTTP serving
- **Person Management**: Complete CRUD operations for person records
- **Vehicle Management**: Complete CRUD operations for vehicle records
- **Persistent Storage**: Organized file storage with date-based directory structure
- **Soft Delete Support**: Mark records as deleted without permanent removal

## API Endpoints

### Authentication
- `POST /api/auth/login` - User authentication

### Images API
- `POST /api/images/upload` - Upload single or multiple images
- `GET /api/images/list` - Get paginated list of images
- `POST /api/images/get-by-ids` - Get images by list of IDs
- `GET /api/images/{id}` - Get image details
- `DELETE /api/images/{id}` - Delete image
- `POST /api/images/bulk-delete` - Delete multiple images
- `GET /api/images/serve/{date}/{filename}` - Serve image over HTTP
- `GET /api/images/health` - Images service health check

### Persons API
- `POST /api/persons/create` - Create new person
- `GET /api/persons/list` - Get paginated list of persons
- `GET /api/persons/search` - Search persons by name
- `GET /api/persons/{id}` - Get person details
- `PUT /api/persons/{id}` - Update person
- `PATCH /api/persons/{id}/soft-delete` - Soft delete person
- `PATCH /api/persons/{id}/restore` - Restore soft deleted person
- `DELETE /api/persons/{id}` - Hard delete person
- `GET /api/persons/health` - Persons service health check

### Vehicles API
- `POST /api/vehicles/create` - Create new vehicle
- `GET /api/vehicles/list` - Get paginated list of vehicles
- `GET /api/vehicles/search` - Search vehicles by VRN, make, or color
- `GET /api/vehicles/{id}` - Get vehicle details
- `PUT /api/vehicles/{id}` - Update vehicle
- `PATCH /api/vehicles/{id}/soft-delete` - Soft delete vehicle
- `PATCH /api/vehicles/{id}/restore` - Restore soft deleted vehicle
- `DELETE /api/vehicles/{id}` - Hard delete vehicle
- `GET /api/vehicles/health` - Vehicles service health check

### Legacy APIs
- `POST /api/public/parse-message` - Parse text or audio message
- `GET /api/public/health` - Service health check
- `GET /api/admin/parameters` - Get extraction parameters
- `POST /api/admin/parameters` - Create extraction parameter
- `GET /api/admin/requests` - Get API request history
- `GET /api/admin/dashboard` - Get dashboard statistics

## Data Models

### Image Model
```json
{
  "id": "string",
  "storage_path": "string",
  "image_url": "string",
  "filename": "string",
  "upload_date": "datetime",
  "uploaded_by": "string",
  "username": "string",
  "file_size": "integer",
  "file_type": "string"
}
```

### Person Model
```json
{
  "id": "string",
  "name": "string",
  "first_name": "string (required)",
  "last_name": "string (required)",
  "phone_number": "string",
  "mobile_number": "string",
  "gender": "string (Male/Female/Other)",
  "date_of_birth": "string (YYYY-MM-DD)",
  "place_of_birth": "string",
  "nationality": "string",
  "pin_code": "string",
  "address": "string",
  "person_photos": "array of image objects",
  "type_of_document": "string",
  "date_of_issue": "string (YYYY-MM-DD)",
  "expiry_date": "string (YYYY-MM-DD)",
  "is_deleted": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Vehicle Model
```json
{
  "id": "string",
  "name": "string",
  "vehicle_registration_number": "string (required)",
  "model": "string",
  "vehicle_make": "string",
  "vehicle_model": "string",
  "vehicle_color": "string",
  "country_of_origin": "string",
  "vehicle_photos": "array of image objects",
  "is_deleted": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## File Storage

### Image Storage Structure
```
/app/data/images/
├── 2024-09-19/
│   ├── uuid1.jpg
│   ├── uuid2.png
│   └── uuid3.jpeg
├── 2024-09-20/
│   └── uuid4.jpg
└── ...
```

### Supported File Types
- **Images**: JPG, JPEG, PNG, GIF, BMP, TIFF
- **Maximum File Size**: 16MB per image
- **Storage**: Persistent volume mounted at `/app/data`

## Environment Variables

```env
MONGODB_URI=mongodb://admin:Apple%40123@mongodb:27017/insight_db?authSource=admin
SPEECH2TEXT_API_URL=http://speech2text-service:8652
SPEECH2TEXT_API_TOKEN=insight_speech_token_2024
OLLAMA_URL=http://host.docker.internal:11434
JWT_SECRET_KEY=insight-api-jwt-secret-key-2024
MAX_CONTENT_LENGTH=16777216
```

## MongoDB Collections

### New Collections
- **images**: Stores image metadata and file paths
- **persons**: Stores person records with photo references
- **vehicles**: Stores vehicle records with photo references

### Existing Collections
- **users**: User accounts and authentication
- **parameters**: AI extraction parameters
- **requests**: API request logging
- **extractions**: Text processing results

## Installation & Setup

### Docker Deployment (Recommended)

1. **Build and run the service**:
   ```bash
   cd officer-insight-api
   docker build -t officer-insight-api .
   docker run -p 8650:8650 \
     -v /path/to/data:/app/data \
     -e MONGODB_URI="mongodb://admin:Apple%40123@mongodb:27017/insight_db?authSource=admin" \
     officer-insight-api
   ```

2. **Using Docker Compose** (from project root):
   ```bash
   docker-compose up officer-insight-api
   ```

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export MONGODB_URI="mongodb://admin:Apple%40123@localhost:27017/insight_db?authSource=admin"
   export SPEECH2TEXT_API_URL="http://localhost:8652"
   export OLLAMA_URL="http://localhost:11434"
   ```

3. **Create data directory**:
   ```bash
   mkdir -p /app/data/images
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

## API Usage Examples

### Authentication
```bash
# Login to get JWT token
curl -X POST "http://localhost:8650/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Apple@123"}'

# Use token in subsequent requests
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8650/api/images/list"
```

### Image Upload
```bash
# Upload images
curl -X POST "http://localhost:8650/api/images/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "user_id=user123" \
  -F "username=john_doe" \
  -F "images=@image1.jpg" \
  -F "images=@image2.png"
```

### Person Management
```bash
# Create person
curl -X POST "http://localhost:8650/api/persons/create" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "gender": "Male",
    "date_of_birth": "1990-05-15",
    "person_photos": ["image_id_1", "image_id_2"]
  }'

# Search persons
curl "http://localhost:8650/api/persons/search?first_name=John&last_name=Doe" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Vehicle Management
```bash
# Create vehicle
curl -X POST "http://localhost:8650/api/vehicles/create" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_registration_number": "ABC123",
    "vehicle_make": "Ford",
    "vehicle_color": "White",
    "vehicle_photos": ["image_id_1"]
  }'

# Search by VRN
curl "http://localhost:8650/api/vehicles/search?vrn=ABC123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## API Documentation

- **Swagger UI**: Available at `http://localhost:8650/docs/`
- **Postman Collection**: Import `../postman/Officer-Insight-API-Complete.json`

## Error Handling

All APIs return consistent error responses:

```json
{
  "message": "Error description",
  "errors": ["List of validation errors"],
  "status": "error"
}
```

## Health Monitoring

Monitor service health using dedicated endpoints:
- Main service: `GET /api/public/health`
- Images service: `GET /api/images/health`
- Persons service: `GET /api/persons/health`
- Vehicles service: `GET /api/vehicles/health`

## Security Features

- **JWT Authentication**: All APIs except health checks require authentication
- **File Type Validation**: Only allowed image formats are accepted
- **File Size Limits**: Maximum 16MB per image
- **Path Sanitization**: Secure filename handling to prevent directory traversal
- **Soft Delete**: Records can be marked as deleted without losing data

## Architecture

### Service Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Images API    │    │    Persons API   │    │  Vehicles API   │
├─────────────────┤    ├──────────────────┤    ├─────────────────┤
│ • Upload        │    │ • CRUD           │    │ • CRUD          │
│ • Storage       │    │ • Search         │    │ • Search by VRN │
│ • HTTP Serving  │    │ • Soft Delete    │    │ • Soft Delete   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────┐
                    │    Core Flask App   │
                    │ • Authentication    │
                    │ • Text Processing   │
                    │ • Admin APIs        │
                    └─────────────────────┘
                                 │
                    ┌─────────────────────┐
                    │      MongoDB        │
                    │ • images            │
                    │ • persons           │
                    │ • vehicles          │
                    │ • users             │
                    └─────────────────────┘
```

### File Storage Architecture
```
Docker Volume Mount: /app/data
├── images/
│   ├── 2024-09-19/
│   │   ├── uuid1.jpg
│   │   └── uuid2.png
│   └── 2024-09-20/
│       └── uuid3.jpg
└── [future expansions]
```

## Version History

- **v2.2.3**: Added comprehensive Images, Persons, and Vehicles APIs
- **v2.2.2**: Enhanced documentation and security features
- **v2.2.1**: Bug fixes and performance improvements
- **v2.2.0**: Core text processing and audio analysis features

## Support

For API documentation and testing:
1. Use Swagger UI at `http://localhost:8650/docs/`
2. Import the Postman collection for comprehensive testing
3. Check health endpoints for service status monitoring
