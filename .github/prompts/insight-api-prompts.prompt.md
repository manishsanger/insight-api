# Officer Insight API System - AI Agent Interaction Prompts

## System Overview Context
This is a **law enforcement data processing microservices system** with 5 Docker services:
- **officer-insight-api** (8650): Core Flask API with JWT auth, text/audio processing
- **car-identifier-service** (8653): Vehicle image analysis via Gemma3:12b vision model
- **doc-reader-service** (8654): Document parsing (passports, IDs) via Gemma3:12b vision model  
- **speech2text-service** (8652): Whisper-based audio transcription
- **admin-ui** (8651): React Admin interface

**Critical Dependencies**: All AI services require Ollama running at `host.docker.internal:11434`

## Common Debugging & Development Patterns

### API Issue Investigation Workflow
When investigating API problems:
1. **Check service health**: `curl http://localhost:PORT/api/public/health`
2. **Test with specific data**: Use real test files from `/Users/manishsanger/Downloads/`
3. **Examine logs**: `docker logs insight-<service-name> --tail 50`
4. **Test parsing logic**: Look for debug output like "AI Output length: X characters" and "Parsed fields count: Y"

### LLM Output Parsing Issues
**Pattern**: LLM successfully extracts data but `extracted_info` fields are empty
**Root Cause**: Markdown formatting mismatch (AI returns `**field:**` but parser expects `field:`)
**Solution**: Add `line.replace('**', '')` to strip markdown formatting before field extraction

### Security & Data Privacy (CRITICAL)
- **NEVER commit real personal documents** - system processes sensitive identity documents
- **Always run security check**: `./scripts/security-check.sh` before commits
- **Use synthetic test data only** for development and testing

### Service Development Workflow
```bash
# Standard development pattern
cd SERVICE-NAME-service && python app.py  # Individual service testing
./scripts/build.sh                       # Full system rebuild
python tests/test_deployment.py          # Deployment verification
docker-compose up -d SERVICE-NAME        # Restart specific service
```

### Authentication Testing Pattern
```bash
# Get JWT token first
curl -X POST "http://localhost:8650/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Apple@123"}'

# Use token for admin endpoints  
curl -H "Authorization: Bearer <token>" http://localhost:8650/api/admin/dashboard
```

### Postman Testing Infrastructure
**Comprehensive testing collections available in `postman/` directory:**
- `Officer-Insight-API-Complete.json` - Full Officer API testing suite
- `Car-Identifier-Service.json` - Vehicle analysis testing
- `Doc-Reader-Service.json` - Document parsing testing
- `Speech2Text-Service.json` - Audio transcription testing
- `Complete-System-Collection.json` - System-wide integration tests
- `Insight-API-Local-Environment.json` - Environment configuration
- `TESTING_GUIDE.md` - Step-by-step testing instructions

**Quick Testing**: Import environment + collection, run authentication first, then test endpoints systematically

## AI Model Integration Patterns

### Vision Model Processing (car-identifier, doc-reader)
```python
# Standard Ollama vision API call
response = requests.post(f"{OLLAMA_URL}/api/generate", json={
    "model": "gemma3:12b",
    "prompt": prompt,
    "images": [base64_image],
    "stream": False
}, timeout=180)
```

### Response Parsing Pattern
```python
# Extract structured data from AI output
def parse_ai_response(ai_output):
    extracted_data = {}
    for line in ai_output.split('\n'):
        line = line.replace('**', '').strip()  # Critical: remove markdown formatting
        if ':' in line:
            key, value = line.split(':', 1)
            field_name = key.lower().replace(' ', '_')
            if value.strip() and value not in ['[not visible]', 'unknown']:
                extracted_data[field_name] = value.strip()
    return extracted_data
```

## Docker & Container Management

### Build and Deployment
```bash
# Full system rebuild (preferred method)
./scripts/build.sh

# Individual service rebuild
docker-compose build SERVICE-NAME
docker-compose up -d SERVICE-NAME

# Check container status
docker ps | grep insight
```

### Health Monitoring
```bash
# Service-specific health checks
curl http://localhost:8650/api/public/health  # Officer API
curl http://localhost:8653/api/public/health  # Car Identifier  
curl http://localhost:8654/api/public/health  # Doc Reader
curl http://localhost:8652/api/health         # Speech2Text
```

## Environment Configuration Patterns

### AI Model Setup (Required)
```bash
ollama pull gemma3:12b      # Vision model for car/document analysis
ollama pull llama3.2:latest # Text processing model
```

### Service Configuration Template
```env
MONGODB_URI=mongodb://admin:Apple%40123@mongodb:27017/insight_db?authSource=admin
OLLAMA_URL=http://host.docker.internal:11434
VISION_MODEL=gemma3:12b
MODEL_TIMEOUT=180
EXTRACTION_FIELDS=field1,field2,field3  # Configurable per service
MAX_CONTENT_LENGTH=16777216              # 16MB file limit
```

## Testing & Validation Patterns

### API Testing with Real Data
```bash
# Document processing test
curl -X POST "http://localhost:8654/api/public/doc-reader" \
  -F "file=@/Users/manishsanger/Downloads/passport-bruce-clark.jpeg" \
  -F "extract_person_image=true" \
  -F "extract_text_info=true"

# Vehicle analysis test  
curl -X POST "http://localhost:8653/api/public/car-identifier" \
  -F "image=@/path/to/vehicle/image.jpg"
```

### Deployment Verification
```bash
python tests/test_deployment.py  # Automated deployment test
./scripts/security-check.sh # Security validation
```

## Git & Version Control

### Commit Workflow
```bash
git add MODIFIED-FILES
git commit -m "fix: describe the specific issue resolved"
git tag -a vX.Y.Z -m "version description"
git push && git push --tags
```

### Tagging Convention
- **Patch**: `v2.2.X` for bug fixes (like markdown parsing fix)
- **Minor**: `v2.X.0` for new features
- **Major**: `vX.0.0` for breaking changes

## Common Issues & Solutions

### Ollama Connectivity
- **Symptom**: "Failed to process with AI vision model"
- **Check**: `curl http://host.docker.internal:11434/api/tags`
- **Solution**: Ensure Ollama is running and models are installed

### Markdown Parsing Issues
- **Symptom**: AI extracts data but `extracted_info` is empty
- **Debug**: Check logs for "AI Output length: X" vs "Parsed fields count: 0"
- **Solution**: Strip markdown formatting before parsing

### Authentication Failures
- **Symptom**: 401/403 errors on admin endpoints
- **Check**: Verify JWT token format and role='admin'
- **Solution**: Re-login to get fresh token

### File Upload Issues
- **Symptom**: File not processed or 413 errors
- **Check**: File size and format validation
- **Solution**: Verify `MAX_CONTENT_LENGTH` and `ALLOWED_EXTENSIONS`

## React Admin UI Debugging

### Authentication Issues
```javascript
// Check token storage
console.log('Token:', localStorage.getItem('token'));
console.log('Role:', localStorage.getItem('role'));

// DataProvider debugging
const httpClient = (url, options = {}) => {
  console.log('Making request to:', url);
  const token = localStorage.getItem('token');
  if (token) options.headers.set('Authorization', `Bearer ${token}`);
  return fetchUtils.fetchJson(url, options);
};
```

## Success Criteria for AI Agent Interactions

### Problem Resolution
- **Identify root cause** through systematic debugging
- **Implement targeted fix** without breaking existing functionality  
- **Verify solution** with real test data
- **Document changes** in commit messages and code comments

### Code Quality
- **Follow established patterns** from existing services
- **Maintain security practices** (no sensitive data commits)
- **Include proper error handling** and validation
- **Update documentation** when adding new features

### Deployment Validation
- **Test service health** after changes
- **Verify API responses** match expected format
- **Check container logs** for errors
- **Run deployment tests** before considering complete