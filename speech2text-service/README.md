# Speech2Text Service

A REST API service for converting audio files to text using OpenAI Whisper.

## Features

- **Whisper Integration**: Uses OpenAI Whisper for high-quality audio transcription
- **Multiple Audio Formats**: Supports WAV, MP3, MP4, MPEG, MPGA, M4A, WEBM, FLAC
- **Token Authentication**: Secure API access with configurable tokens
- **File Storage**: Persistent storage of processed audio files
- **Health Monitoring**: Built-in health check endpoints
- **Swagger Documentation**: Complete API documentation
- **Test Suite**: Comprehensive test coverage

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

- `POST /api/convert` - Convert audio file to text
- `GET /api/health` - Health check endpoint
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

### Convert Audio File
```bash
curl -X POST http://localhost:8652/api/convert \
  -H "Authorization: Bearer insight_speech_token_2024" \
  -F "audio_file=@recording.wav"
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

### Successful Conversion
```json
{
  "text": "This is the transcribed text from the audio file",
  "file_id": "uuid-generated-id",
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
- `WHISPER_MODEL`: Whisper model to use (default: turbo)
- `MAX_CONTENT_LENGTH`: Maximum file size in bytes (default: 100MB)

## Available Whisper Models

- **turbo**: Fastest model, good for real-time applications
- **base**: Balanced speed and accuracy
- **small**: Better accuracy, slower processing
- **medium**: High accuracy, slower processing
- **large**: Best accuracy, slowest processing

## File Limits

- **Maximum file size**: 100MB
- **Supported formats**: WAV, MP3, MP4, MPEG, MPGA, M4A, WEBM, FLAC
- **Processing timeout**: 2 minutes per file

## Dependencies

- Flask 2.3.3
- Flask-CORS 4.0.0
- flask-restx 1.2.0
- openai-whisper 20231117
- torch 2.0.1
- torchaudio 2.0.2
- requests 2.31.0
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
export WHISPER_MODEL="turbo"
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
  -e WHISPER_MODEL="turbo" \
  -v /path/to/audio/storage:/app/audio_files \
  speech2text-service
```

## API Documentation

Once the service is running, visit http://localhost:8652/docs/ for interactive API documentation.

## Health Check

The service provides a comprehensive health check at `/api/health` that monitors:
- Whisper model loading status
- Available disk space
- Directory accessibility
- Overall service status

Example health response:
```json
{
  "status": "healthy",
  "timestamp": "2024-07-25T10:30:00Z",
  "model": {
    "name": "turbo",
    "status": "loaded"
  },
  "storage": {
    "audio_directory": true,
    "temp_directory": true,
    "free_space_gb": 25.6
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

- **Model Loading**: Whisper model is loaded once at startup
- **Processing Time**: Varies by file length and model size
- **Memory Usage**: Larger models require more memory
- **Disk Space**: Audio files are stored permanently

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

1. **Model Loading Errors**
   - Ensure sufficient disk space
   - Check internet connectivity for initial model download

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
