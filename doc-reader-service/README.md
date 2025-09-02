# Document Reader Service

AI-powered document parsing and information extraction service using vision language models.

## Overview

The Document Reader Service is a specialized microservice that processes document images and PDFs to extract structured information using advanced AI vision models. It integrates with Ollama and the Gemma3:12b vision model to analyze documents and extract key information like names, dates, addresses, and other relevant document fields.

## Features

- **Multi-format Support**: Processes both image files (JPG, PNG, GIF, BMP, WebP) and PDF documents
- **AI-Powered Extraction**: Uses Gemma3:12b vision language model for intelligent document analysis
- **Person Image Extraction**: Automatically detects and extracts person photographs from documents ✨ **NEW**
- **Configurable Fields**: Customizable extraction fields through environment variables
- **RESTful API**: Clean REST API with comprehensive documentation
- **Admin Interface**: Protected admin endpoints with JWT authentication
- **Persistent Storage**: Dual storage system (temporary processing + persistent archival)
- **Health Monitoring**: Built-in health checks for service and dependencies
- **CORS Support**: Configurable CORS for frontend integration

## Supported Document Types

- Identity Documents (Driving License, Passport, ID Cards)
- Government Documents
- Certificates
- Forms
- Any document with structured text information

## Extracted Information Fields

The service can extract the following information (configurable):

- **document_type**: Type of document (driving_license, passport, etc.)
- **name**: Full name
- **date_of_birth**: Date of birth
- **country**: Country
- **date_of_issue**: Date of issue
- **expiry_date**: Expiry date
- **address**: Address
- **gender**: Gender
- **place_of_birth**: Place of birth
- **issuing_authority**: Issuing authority
- **nationality**: Nationality
- **pin_code**: PIN/Postal code
- **person_image**: Base64 encoded person image extracted from document ✨ **NEW**

## API Endpoints

### Public Endpoints

#### Health Check
```
GET /api/public/health
```
Returns service health status and dependency checks.

#### Document Processing
```
POST /api/public/doc-reader
```
Process a document file and extract information.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (document image or PDF)

**Response:**
```json
{
  "id": "document_id",
  "filename": "original_filename.pdf",
  "file_path": "/path/to/stored/file",
  "model": "gemma3:12b",
  "service": "doc-reader-service",
  "extraction_fields": ["name", "date_of_birth", ...],
  "processed_output": "raw AI model output",
  "extracted_info": {
    "document_type": "driving_license",
    "name": "John Doe",
    "date_of_birth": "1990-01-01",
    ...
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Admin Endpoints (Authentication Required)

#### List Documents
```
GET /api/admin/doc-reader?page=1&per_page=10
```
Get paginated list of processed documents.

#### Document Details
```
GET /api/admin/doc-reader/{doc_id}
```
Get detailed information about a specific document.

## Installation

### Using Docker (Recommended)

1. **Build the service:**
   ```bash
   docker build -t doc-reader-service .
   ```

2. **Run with docker-compose:**
   ```bash
   docker-compose up doc-reader-service
   ```

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install system dependencies:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install poppler-utils

   # macOS
   brew install poppler
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the service:**
   ```bash
   python app.py
   ```

## Configuration

The service is configured through environment variables:

### Core Configuration
- `PORT`: Service port (default: 8654)
- `MONGODB_URI`: MongoDB connection string
- `OLLAMA_URL`: Ollama API URL (default: http://host.docker.internal:11434)
- `VISION_MODEL`: AI model to use (default: gemma3:12b)

### Processing Configuration
- `MODEL_TIMEOUT`: AI model request timeout in seconds (default: 180)
- `ALLOWED_EXTENSIONS`: Supported file extensions (comma-separated)
- `MAX_CONTENT_LENGTH`: Maximum file size in bytes (default: 16MB)
- `EXTRACTION_FIELDS`: Fields to extract (comma-separated)

### Storage Configuration
- `STORAGE_PATH`: Temporary storage path (default: /app/data/uploads)
- `PERSISTENT_STORAGE`: Persistent storage path

### Security Configuration
- `JWT_SECRET_KEY`: Secret key for JWT token validation
- `JWT_ACCESS_TOKEN_EXPIRES`: Token expiry time in seconds
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)

## Usage Examples

### Process a Document Image
```bash
curl -X POST \
  http://localhost:8654/api/public/doc-reader \
  -H "Content-Type: multipart/form-data" \
  -F "file=@driving_license.jpg"
```

### Process a PDF Document
```bash
curl -X POST \
  http://localhost:8654/api/public/doc-reader \
  -H "Content-Type: multipart/form-data" \
  -F "file=@passport.pdf"
```

### Get Document List (Admin)
```bash
curl -X GET \
  http://localhost:8654/api/admin/doc-reader \
  -H "Authorization: Bearer your_jwt_token"
```

## Integration

### With Officer Insight API
The Document Reader Service is designed to integrate seamlessly with the Officer Insight API ecosystem:

```python
import requests

# Process document through the service
response = requests.post(
    'http://localhost:8654/api/public/doc-reader',
    files={'file': open('document.pdf', 'rb')}
)

extracted_info = response.json()['extracted_info']
```

### With Admin UI
The service integrates with the Admin UI for document management and monitoring.

## Development

### Project Structure
```
doc-reader-service/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── .env              # Environment configuration
└── README.md         # This file
```

### Adding New Extraction Fields

1. Update the `EXTRACTION_FIELDS` environment variable
2. Modify the `parse_document_info()` function to handle new fields
3. Update the API documentation models

### Extending Document Support

To add support for new document types:

1. Add file extensions to `ALLOWED_EXTENSIONS`
2. Implement processing logic in `process_document_with_ollama()`
3. Update the AI prompt to recognize new document types

## Monitoring

### Health Checks
The service provides comprehensive health monitoring:

```bash
curl http://localhost:8654/api/public/health
```

Response includes:
- Service status
- Database connectivity
- Ollama service status
- Model information
- Configuration details

### Logging
The service logs all operations including:
- Document processing requests
- AI model interactions
- Error conditions
- Performance metrics

## Security

### Authentication
Admin endpoints require JWT authentication with 'admin' role.

### File Validation
- File type validation based on extensions
- File size limits
- Secure filename handling

### Data Protection
- Temporary files are cleaned up after processing
- Persistent storage for archival purposes
- Database storage of processing results

## Dependencies

### Python Packages
- Flask: Web framework
- Flask-RESTX: API documentation and validation
- PyMongo: MongoDB integration
- PyMuPDF: PDF processing
- pdf2image: PDF to image conversion
- Pillow: Image processing
- python-dotenv: Environment management
- PyJWT: JWT token handling

### System Dependencies
- poppler-utils: PDF processing utilities

### External Services
- MongoDB: Document storage
- Ollama: AI model serving
- Gemma3:12b: Vision language model

## Performance

### Optimization Tips
1. Use appropriate file sizes (balance quality vs processing time)
2. Configure model timeout based on document complexity
3. Monitor storage usage for persistent files
4. Use pagination for large document lists

### Scaling
- Horizontal scaling supported through Docker
- Stateless design enables load balancing
- Shared MongoDB for data consistency

## Troubleshooting

### Common Issues

1. **PDF Processing Errors**
   - Ensure poppler-utils is installed
   - Check PDF file integrity
   - Verify file permissions

2. **AI Model Timeouts**
   - Increase `MODEL_TIMEOUT` setting
   - Check Ollama service availability
   - Verify model is downloaded

3. **File Upload Issues**
   - Check file size limits
   - Verify allowed extensions
   - Ensure storage paths exist

4. **Database Connection**
   - Verify MongoDB URI format
   - Check network connectivity
   - Validate credentials

## Support

For issues and questions:
1. Check the logs for error details
2. Verify configuration settings
3. Test with sample documents
4. Review the API documentation at `/docs/`

## Version History

- v1.0.0: Initial release with document processing capabilities
