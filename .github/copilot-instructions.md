# GitHub Copilot Instructions - Officer Insight API System

## Architecture Overview
This is a **microservices-based law enforcement data processing system** with 5 services using Docker Compose orchestration:

- **officer-insight-api** (8650): Core Flask API with JWT auth, text/audio processing via Llama3.2:latest
- **car-identifier-service** (8653): Vehicle image analysis using Gemma3:12b vision model  
- **doc-reader-service** (8654): Document parsing (passports, IDs) using Gemma3:12b vision model
- **speech2text-service** (8652): Whisper-based audio transcription with Ollama text processing
- **admin-ui** (8651): React Admin interface for system management

**Critical**: All AI services depend on **Ollama** running at `host.docker.internal:11434`

## Key Development Patterns

### Flask Service Structure (All AI Services)
```python
# Standard service setup pattern
app = Flask(__name__)
mongo = PyMongo(app)  # MongoDB integration
api = Api(app, doc='/docs/')  # Flask-RESTX with Swagger

# Custom JSON encoder for MongoDB ObjectId serialization
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId): return str(o)
        return super().default(o)

# Consistent health check endpoint
@ns.route('/health')
def health(): return {'status': 'healthy', 'services': {...}}
```

### AI Model Integration Pattern
All services use this Ollama integration pattern:
```python
# Vision model call (car-identifier, doc-reader)
response = requests.post(f"{OLLAMA_URL}/api/generate", json={
    "model": "gemma3:12b",
    "prompt": prompt,
    "images": [base64_image],
    "stream": False
}, timeout=MODEL_TIMEOUT)

# Text model call (officer-insight-api, speech2text)
response = requests.post(f"{OLLAMA_URL}/api/generate", json={
    "model": "llama3.2:latest", 
    "prompt": prompt,
    "stream": False
})
```

### Authentication Pattern (JWT + Role-based)
```python
# Token validation decorator (admin endpoints)
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        data = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        if data.get('role') != 'admin': return {'message': 'Admin required'}, 403
        return f(*args, **kwargs)
    return decorated
```

## Critical Environment Configuration

### Required Ollama Models
```bash
ollama pull gemma3:12b      # Vision model (car/doc analysis)
ollama pull llama3.2:latest # Text processing
```

### Service Environment Patterns
All services follow this env config pattern:
```env
MONGODB_URI=mongodb://admin:Apple%40123@mongodb:27017/insight_db?authSource=admin
OLLAMA_URL=http://host.docker.internal:11434
VISION_MODEL=gemma3:12b
MODEL_TIMEOUT=180
EXTRACTION_FIELDS=field1,field2,field3  # Configurable extraction
```

## Essential Developer Workflows

### Quick Development Setup
```bash
# Build and start all services
./scripts/build.sh

# Test deployment
python tests/test_deployment.py

# Security check before commits
./scripts/security-check.sh
```

### Service-Specific Development
```bash
# Individual service development
cd car-identifier-service && python app.py
# Check health: curl http://localhost:8653/api/public/health
```

### API Testing Pattern
```bash
# Authentication required for all endpoints except health/auth
# 1. Login: POST /api/auth/login {"username":"admin","password":"Apple@123"}
# 2. Get JWT token and use in all requests
TOKEN=$(curl -X POST "http://localhost:8650/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Apple@123"}' | jq -r '.access_token')

# All API endpoints require JWT Bearer token
curl -X POST "http://localhost:8653/api/car-identifier" \
  -H "Authorization: Bearer $TOKEN" \
  -F "image=@test.jpg"
```

### Postman Testing Collections
**Location**: `postman/` directory with comprehensive service-specific collections:
- `Officer-Insight-API-Complete.json` - Complete Officer API testing
- `Car-Identifier-Service.json` - Vehicle analysis endpoints  
- `Doc-Reader-Service.json` - Document parsing endpoints
- `Speech2Text-Service.json` - Audio transcription endpoints
- `Complete-System-Collection.json` - Cross-service integration tests
- `TESTING_GUIDE.md` - Comprehensive testing instructions

**Usage**: Import collections with `Insight-API-Local-Environment.json` for automated testing

## Security & Data Privacy (CRITICAL)

### Sensitive Data Handling
**NEVER commit real personal data**. This system processes:
- Identity documents (passports, licenses)
- Personal photos from documents  
- Vehicle license plates
- Audio recordings with personal info

### File Exclusion Patterns (.gitignore)
```gitignore
*.jpeg *.jpg *.png *.gif *.bmp *.tiff
passport* license* id_card*
test_* sample_*
/docker-data/ /uploads/
```

**Important**: All services use `/Users/manishsanger/docker-data/` (global directory) for persistent storage, not local docker-data directory.

### Pre-commit Security Check
Always run: `./scripts/security-check.sh` before commits

## AI Response Parsing Patterns

### Structured Extraction Pattern (car/doc services)
```python
def parse_ai_response(ai_output):
    extracted_data = {}
    for line in ai_output.split('\n'):
        line = line.replace('**', '').strip()  # Remove markdown formatting
        if ':' in line:
            key, value = line.split(':', 1)
            field_name = key.lower().replace(' ', '_')
            if value.strip() and value not in ['[not visible]', 'unknown']:
                extracted_data[field_name] = value.strip()
    return extracted_data
```

## Common Integration Points

### Cross-Service Communication
- **officer-insight-api** → **speech2text-service**: Audio processing
- **admin-ui** → All APIs: Management interface
- All services → **MongoDB**: Shared database
- All AI services → **Ollama**: Model inference

### Standard Response Format
```json
{
  "id": "extraction_id",
  "filename": "uploaded_file.jpg", 
  "model": "gemma3:12b",
  "service": "car-identifier-service",
  "extraction_fields": ["field1", "field2"],
  "processed_output": "Raw AI response",
  "extracted_info": {"field1": "value1", "field2": "value2"}
}
```

## Debugging Essentials

### Service Health Checks
```bash
curl http://localhost:8650/api/public/health     # Officer API
curl http://localhost:8653/api/public/health     # Car Identifier  
curl http://localhost:8654/api/public/health     # Doc Reader
curl http://localhost:8652/api/public/health     # Speech2Text
```

### Container Debugging
```bash
docker logs insight-car-identifier --tail 50
docker logs insight-doc-reader --tail 50
docker logs insight-officer-api --tail 50
```

### Common Issues
- **Ollama connectivity**: Check `host.docker.internal:11434`
- **Model timeouts**: Increase `MODEL_TIMEOUT` for complex processing
- **Auth failures**: Verify JWT token and role='admin'
- **File size limits**: Check `MAX_CONTENT_LENGTH` settings

## React Admin UI Patterns

### DataProvider Pattern
```javascript
// Custom httpClient with JWT auth
const httpClient = (url, options = {}) => {
  const token = localStorage.getItem('token');
  if (token) options.headers.set('Authorization', `Bearer ${token}`);
  return fetchUtils.fetchJson(url, options);
};
```

### Authentication Flow
```javascript
// Login flow stores JWT token
authProvider.login({username, password}) → 
localStorage.setItem('token', response.data.access_token)
```

## Project-Specific Conventions

- **Port allocation**: 865X range (8650-8654)
- **Container naming**: `insight-<service-name>`
- **Model timeouts**: 180s default for vision models
- **File size limits**: 16MB for images, 100MB for audio
- **CORS origins**: Configurable via env for frontend integration
- **Extraction fields**: Fully configurable via environment variables
