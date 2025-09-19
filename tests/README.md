# Tests Directory

This directory contains all test files for the Officer Insight API System.

## Test Files

### 🔧 **System Tests**
- **`test_deployment.py`** - Comprehensive deployment verification with JWT authentication
- **`test_security_endpoints.py`** - Security implementation testing across all services

### 🏥 **Service-Specific Tests**
- **`test_doc_reader.py`** - Document Reader Service functionality with authentication
- **`test_person_image_extraction.py`** - Person image extraction from documents
- **`test_simple_auth.py`** - JWT authentication flow testing

### 📄 **Test Data**
- **`test_document.txt`** - Sample document for testing

## Running Tests

All tests now require JWT authentication. The system uses the following credentials:
- **Username**: `admin`
- **Password**: `Apple@123`

### Quick Test Commands

```bash
# Run comprehensive deployment test
python tests/test_deployment.py

# Test security implementation
python tests/test_security_endpoints.py

# Test document processing
python tests/test_doc_reader.py

# Test person image extraction
python tests/test_person_image_extraction.py

# Test authentication only
python tests/test_simple_auth.py
```

### Prerequisites

1. **All services running**: Use `./scripts/build.sh` to start all services
2. **Ollama models loaded**: 
   - `gemma3:12b` (for document/vehicle analysis)
   - `llama3.2:latest` (for text processing)
3. **Authentication credentials**: Default admin credentials must be available

## Test Requirements

### Python Dependencies
```bash
pip install requests pillow
```

### Service Endpoints Tested
- **Officer API**: `http://localhost:8650`
- **Car Identifier**: `http://localhost:8653`
- **Document Reader**: `http://localhost:8654`
- **Speech2Text**: `http://localhost:8652`

## Authentication Model

All tests now use JWT Bearer token authentication:

1. **Public Endpoints** (no authentication required):
   - `/api/public/health` - Service health checks
   - `/api/auth/login` - Authentication endpoint

2. **Secured Endpoints** (JWT required):
   - `/api/parse-message` - Text/audio processing
   - `/api/car-identifier` - Vehicle image analysis
   - `/api/doc-reader` - Document processing
   - `/api/convert` - Speech-to-text conversion
   - `/api/process-text` - Text processing
   - `/api/files` - File management

## Test Structure

Each test file follows this pattern:

```python
def get_auth_token():
    """Get JWT authentication token"""
    response = requests.post("http://localhost:8650/api/auth/login", 
                           json={"username": "admin", "password": "Apple@123"})
    return response.json().get('access_token')

def test_endpoint(token):
    """Test secured endpoint with authentication"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post("http://localhost:XXXX/api/endpoint", 
                           headers=headers, ...)
```

## Migration Notes

**Previous Location**: Root directory (`./test_*.py`)  
**New Location**: `./tests/test_*.py`

**Updated References**:
- Documentation updated to reflect new paths
- All import paths corrected
- Authentication added to all relevant tests
- Public endpoint prefixes removed (`/api/public/` → `/api/`)

## Troubleshooting

### Common Issues

1. **Authentication Failures**:
   - Verify admin credentials are correct
   - Check if officer-insight-api service is running
   - Ensure JWT secret is properly configured

2. **Service Unavailable**:
   - Run `docker ps` to check service status
   - Check service logs: `docker logs insight-SERVICE-NAME`
   - Verify ports are accessible

3. **Test Failures**:
   - Ensure all services are healthy: `curl http://localhost:XXXX/api/public/health`
   - Check Ollama is running with required models
   - Verify network connectivity between services

### Health Check Commands

```bash
# Check all services
curl http://localhost:8650/api/public/health  # Officer API
curl http://localhost:8653/api/public/health  # Car Identifier
curl http://localhost:8654/api/public/health  # Document Reader
curl http://localhost:8652/api/public/health  # Speech2Text
```
