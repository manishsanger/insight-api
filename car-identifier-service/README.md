# Car Identifier Service

## Overview

The Car Identifier Service is a specialized microservice designed to identify and extract vehicle information from images using AI-powered computer vision. This service uses the Gemma3:12b vision model through Ollama to analyze vehicle images and extract structured data including license plates, make, model, color, and other vehicle characteristics.

## Features

- **AI-Powered Vehicle Recognition**: Uses Gemma3:12b vision model for accurate vehicle identification
- **Configurable Extraction Fields**: Customizable parameters for different use cases
- **RESTful API**: Clean, documented API endpoints
- **Health Monitoring**: Built-in health checks and monitoring
- **Database Integration**: MongoDB for data persistence
- **Docker Support**: Containerized deployment
- **Flexible Configuration**: Environment-based configuration

## API Endpoints

### POST /api/public/car-identifier
Analyze a vehicle image and extract information.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: `image` (file) - Vehicle image (JPG, PNG, GIF, BMP, WEBP)

**Response:**
```json
{
  "id": "extraction_id",
  "filename": "uploaded_filename.jpg",
  "model": "gemma3:12b",
  "service": "car-identifier-service",
  "extraction_fields": ["vehicle_registration", "vehicle_make", "vehicle_color", "vehicle_model"],
  "processed_output": "Raw AI model output",
  "extracted_info": {
    "vehicle_make": "Toyota",
    "vehicle_color": "Blue",
    "vehicle_model": "Camry"
  }
}
```

### GET /api/public/health
Check service health and configuration.

**Response:**
```json
{
  "status": "healthy",
  "service": "car-identifier-service",
  "model": "gemma3:12b",
  "extraction_fields": ["vehicle_registration", "vehicle_make", "vehicle_color", "vehicle_model"],
  "timestamp": "2025-08-22T10:30:00Z",
  "services": {
    "database": "healthy",
    "ollama": "healthy"
  }
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://admin:Apple%40123@mongodb:27017/insight_db?authSource=admin` |
| `OLLAMA_URL` | Ollama service URL | `http://host.docker.internal:11434` |
| `VISION_MODEL` | AI vision model to use | `gemma3:12b` |
| `MODEL_TIMEOUT` | Model processing timeout (seconds) | `180` |
| `PORT` | Service port | `8653` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:8651,http://localhost:3000` |
| `ALLOWED_EXTENSIONS` | Supported file extensions | `jpg,jpeg,png,gif,bmp,webp` |
| `MAX_CONTENT_LENGTH` | Maximum file size (bytes) | `16777216` (16MB) |
| `EXTRACTION_FIELDS` | Fields to extract | `vehicle_registration,vehicle_make,vehicle_color,vehicle_model` |

### Configurable Extraction Fields

The service supports the following extraction fields:

- `vehicle_registration` - License plate number
- `vehicle_make` - Manufacturer/brand (Toyota, BMW, etc.)
- `vehicle_color` - Primary vehicle color
- `vehicle_model` - Model/series name
- `vehicle_type` - Vehicle type (car, truck, SUV, etc.)
- `vehicle_year` - Year of manufacture
- `vehicle_condition` - Vehicle condition assessment

## Installation & Deployment

### Docker Deployment (Recommended)

1. **Build the Docker image:**
```bash
docker build -t car-identifier-service:latest ./car-identifier-service
```

2. **Run with Docker Compose:**
```bash
docker-compose up car-identifier-service
```

### Local Development

1. **Install dependencies:**
```bash
cd car-identifier-service
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Run the service:**
```bash
python app.py
```

## Dependencies

### System Requirements
- Python 3.9+
- MongoDB 5.0+
- Ollama with Gemma3:12b model

### Python Dependencies
- Flask 2.3.3
- Flask-PyMongo 2.3.0
- Flask-CORS 4.0.0
- Flask-RESTX 1.2.0
- Pillow 10.0.1
- Requests 2.31.0

## Usage Examples

### cURL Example
```bash
curl -X POST \
  http://localhost:8653/api/public/car-identifier \
  -H "Content-Type: multipart/form-data" \
  -F "image=@path/to/vehicle/image.jpg"
```

### Python Example
```python
import requests

url = "http://localhost:8653/api/public/car-identifier"
files = {"image": open("vehicle.jpg", "rb")}

response = requests.post(url, files=files)
result = response.json()

print(f"Vehicle Make: {result['extracted_info'].get('vehicle_make')}")
print(f"Vehicle Color: {result['extracted_info'].get('vehicle_color')}")
```

### JavaScript/Fetch Example
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);

fetch('http://localhost:8653/api/public/car-identifier', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Vehicle info:', data.extracted_info);
});
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8653/docs/

## Monitoring & Logging

### Health Checks
The service provides health endpoints for monitoring:
- Database connectivity status
- Ollama service availability
- Overall service health

### Logging
- Request/response logging
- Error tracking
- Performance metrics
- Database operation logs

## Error Handling

The service provides comprehensive error handling for:

- **400 Bad Request**: Invalid file format, missing image
- **500 Internal Server Error**: AI model failures, database issues
- **503 Service Unavailable**: Ollama service unavailable

## Performance Considerations

- **Image Size**: Recommend images under 16MB for optimal performance
- **Processing Time**: Typical processing time is 5-15 seconds depending on image complexity
- **Concurrent Requests**: Service supports multiple concurrent image processing requests
- **Resource Usage**: Memory usage scales with image size and model complexity

## Security

- Input validation for file types and sizes
- CORS configuration for web security
- No authentication required for public endpoints
- Database connection security

## Troubleshooting

### Common Issues

1. **"Failed to process image"**
   - Check Ollama service is running
   - Verify model is available: `ollama list`
   - Check image format is supported

2. **Database connection errors**
   - Verify MongoDB is running
   - Check connection string in environment variables
   - Ensure database authentication is correct

3. **Timeout errors**
   - Increase `MODEL_TIMEOUT` for large images
   - Check Ollama service performance
   - Monitor system resources

### Logs
Check service logs for detailed error information:
```bash
docker logs insight-car-identifier
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is part of the Officer Insight API system. See the main project documentation for licensing information.

## Support

For issues and questions:
- Check the troubleshooting section
- Review logs for error details
- Submit issues to the project repository
