# Postman Import and Setup Guide

## Quick Setup Steps

### 1. Import Collection
1. Open Postman
2. Click "Import" button
3. Select "Upload Files"
4. Choose `postman/Insight-API-Test-Collection.json`
5. Click "Import"

### 2. Import Environment
1. Click on "Environments" in left sidebar
2. Click "Import" button
3. Select `postman/Insight-API-Local-Environment.json`
4. Click "Import"
5. Select "Insight API - Local Environment" from dropdown

### 3. Verify Services Are Running
Before testing, ensure all services are started:
```bash
# Start all services
./scripts/start.sh

# Check status
docker-compose ps

# Verify health
curl http://localhost:8650/api/public/health
curl http://localhost:8652/api/health
```

### 4. Run Tests in Order
1. **Authentication** → Admin Login (sets JWT token automatically)
2. **Public APIs** → Test all public endpoints
3. **Admin APIs** → Test admin endpoints (requires JWT)
4. **Speech2Text Service** → Test direct speech service
5. **Error Testing** → Validate error handling

### 5. File Upload Tests
For audio and image tests:
1. Select the request
2. Go to "Body" tab
3. Click "Select Files" for file parameters
4. Choose your test files from test-data directory

## Automated Testing
Use Collection Runner for automated testing:
1. Click "Runner" button
2. Select "Insight API - Complete Test Suite"
3. Choose environment
4. Click "Run Insight API - Complete Test Suite"

## Troubleshooting
- Ensure JWT token is set (run Admin Login first)
- Check that all services are healthy
- Verify file formats are supported
- Check network connectivity to localhost
