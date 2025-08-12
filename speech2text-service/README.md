# Speech2Text Service

A REST API service for converting audio files to text and processing them with Ollama AI for structured information extraction.

## Features

- **Audio Preprocessing**: Uses FFmpeg for audio format conversion and preprocessing
- **AI Text Processing**: Uses Ollama AI (llama3.2:latest model) for advanced text processing
- **Structured Data Extraction**: Specialized for traffic offense report parsing
- **Multiple Audio Formats**: Supports WAV, MP3, MP4, MPEG, MPGA, M4A, WEBM, FLAC
- **Token Authentication**: Secure API access with configurable tokens
- **File Storage**: Persistent storage of processed audio files
- **Health Monitoring**: Built-in health check endpoints with Ollama connectivity
- **Swagger Documentation**: Complete API documentation
- **Test Suite**: Comprehensive test coverage
- **Enhanced Prompt Engineering**: Optimized for law enforcement use cases

## Supported Audio Formats

- WAV (Waveform Audio File Format)
- MP3 (MPEG Audio Layer III)
- MP4 (MPEG-4 Audio)
- MPEG (MPEG Audio)
- MPGA (MPEG Audio)
- M4A (MPEG-4 Audio)
- WEBM (WebM Audio)
- FLAC (Free Lossless Audio Codec)

## API Endpoints

- `POST /api/convert` - Convert audio file to text and process with Ollama AI
- `POST /api/process-text` - Process text directly with Ollama AI for structured extraction
- `GET /api/health` - Health check endpoint with Ollama connectivity status
- `GET /api/files` - List stored audio files (requires authentication)

## Authentication

All API endpoints except health check require authentication using Bearer token.

### Default Token
- **Token**: `insight_speech_token_2024`

Include the token in the Authorization header:
```
Authorization: Bearer insight_speech_token_2024
```

## Request Examples

### Convert Audio File with AI Processing
```bash
curl -X POST http://localhost:8652/api/convert \
  -H "Authorization: Bearer insight_speech_token_2024" \
  -F "audio_file=@recording.wav"
```

### Process Text with Ollama AI
```bash
curl -X POST http://localhost:8652/api/process-text \
  -H "Authorization: Bearer insight_speech_token_2024" \
  -H "Content-Type: application/json" \
  -d '{"text": "Officer observed red Honda Civic speeding on Main Street"}'
```

### Health Check
```bash
curl -X GET http://localhost:8652/api/health
```

### List Files (Admin)
```bash
curl -X GET http://localhost:8652/api/files \
  -H "Authorization: Bearer insight_speech_token_2024"
```

## Response Format

### Successful Conversion and Processing
```json
{
  "text": "This is the transcribed text from the audio file",
  "processed_output": "Structured output from Ollama AI with extracted information",
  "file_id": "uuid-generated-id",
  "timestamp": "2024-07-25T10:30:00Z"
}
```

### Text Processing Response
```json
{
  "text": "Officer observed red Honda Civic speeding on Main Street",
  "processed_output": "Offence Category: Speeding\nVehicle Manufacturer: Honda\nVehicle Model: Civic (Red)\nLocation Of Offence: Main Street",
  "file_id": null,
  "timestamp": "2024-07-25T10:30:00Z"
}
```

### Error Response
```json
{
  "message": "Error description"
}
```

## Environment Variables

- `API_TOKEN`: Authentication token (default: insight_speech_token_2024)
- `OLLAMA_URL`: Ollama AI service URL (default: http://host.docker.internal:11434)
- `OLLAMA_MODEL`: Ollama model name (default: llama3.2:latest)
- `MAX_CONTENT_LENGTH`: Maximum file size in bytes (default: 100MB)

## Available AI Models

- **llama3.2:latest**: Optimized for structured data extraction and traffic offense parsing
- **Alternative models**: Can be configured via OLLAMA_MODEL environment variable

## AI Processing Features

- **Structured Data Extraction**: Converts unstructured text into organized fields
- **Traffic Offense Parsing**: Specialized for law enforcement use cases
- **Enhanced Prompt Engineering**: Optimized prompts for consistent output format
- **Multi-format Support**: Handles various input text formats and styles

## File Limits

- **Maximum file size**: 100MB
- **Supported formats**: WAV, MP3, MP4, MPEG, MPGA, M4A, WEBM, FLAC
- **Processing timeout**: 2 minutes per file
- **AI Processing**: Additional time for Ollama text analysis

## Dependencies

- Flask 2.3.3
- Flask-CORS 4.0.0
- flask-restx 1.2.0
- requests 2.31.0 (for Ollama API integration)
- python-multipart 0.0.6
- Werkzeug 2.3.7
- gunicorn 21.2.0
- pytest 7.4.2
- pytest-flask 1.2.0

## Running Locally

1. Install system dependencies:
```bash
# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg

# On macOS
brew install ffmpeg
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables (optional):
```bash
export API_TOKEN="your-custom-token"
export OLLAMA_URL="http://host.docker.internal:11434"
export OLLAMA_MODEL="llama3.2:latest"
```

4. Run the application:
```bash
python app.py
```

The service will be available at http://localhost:8652

## Docker Usage

### Build Image
```bash
docker build -t speech2text-service .
```

### Run Container
```bash
docker run -d \
  -p 8652:8652 \
  -e API_TOKEN="your-token" \
  -e OLLAMA_URL="http://host.docker.internal:11434" \
  -e OLLAMA_MODEL="llama3.2:latest" \
  -v /path/to/audio/storage:/app/audio_files \
  speech2text-service
```

## API Documentation

Once the service is running, visit http://localhost:8652/docs/ for interactive API documentation.

## Health Check

The service provides a comprehensive health check at `/api/health` that monitors:
- Ollama AI service connectivity and model availability
- Available disk space
- Directory accessibility
- Overall service status

Example health response:
```json
{
  "status": "healthy",
  "timestamp": "2024-07-25T10:30:00Z",
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

## Testing

Run the test suite:
```bash
pytest tests/
```

### Test Coverage
- Authentication tests
- File upload tests
- Ollama AI integration tests
- Health check tests
- API documentation accessibility
- Error handling

## Error Handling

The API returns appropriate HTTP status codes:
- 200: Success
- 400: Bad Request (invalid file format, no file provided)
- 401: Unauthorized (invalid/missing token)
- 500: Internal Server Error (processing error)

## File Storage

- Processed audio files are stored permanently in `/app/audio_files`
- Temporary files are stored in `/app/temp` during processing
- File naming convention: `{uuid}_{original_filename}`
- Storage monitoring included in health checks

## Performance Considerations

- **Audio Preprocessing**: FFmpeg handles format conversion efficiently
- **AI Processing**: Ollama model processing time varies by text complexity
- **Processing Time**: Varies by file length and text analysis requirements
- **Memory Usage**: Optimized for efficient memory usage
- **Disk Space**: Audio files are stored permanently, processed output cached

## Security

- Token-based authentication for all API operations
- File type validation
- File size limits
- Secure file handling with temporary storage cleanup

## Monitoring

- Health check endpoint for service monitoring
- File listing endpoint for storage monitoring
- Processing logs for debugging
- Error tracking and reporting

## Troubleshooting

### Common Issues

1. **Ollama Connection Errors**
   - Ensure Ollama service is running on host.docker.internal:11434
   - Check network connectivity between containers
   - Verify llama3.2:latest model is available

2. **Audio Processing Errors**
   - Verify audio file format is supported
   - Check file size limits
   - Ensure ffmpeg is installed

3. **Authentication Errors**
   - Verify token is correct
   - Check Authorization header format

4. **Storage Issues**
   - Ensure write permissions to audio_files directory
   - Check available disk space
