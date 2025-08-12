# Postman Testing Guide - Insight API

This guide provides step-by-step instructions for testing all API endpoints using Postman. The Insight API system includes three main services with various endpoints for authentication, text processing, audio processing, and vehicle image identification.

## 📋 Prerequisites

1. **Postman** installed (Desktop app or web version)
2. **Insight API services running** on your local machine
3. **Sample files** for testing:
   - Audio file (WAV, MP3, MP4, FLAC)
   - Vehicle image (JPG, PNG, GIF, BMP, WebP)

## 🌐 Base URLs

```
Officer Insight API: http://localhost:8650/api
Speech2Text Service: http://localhost:8652/api
Admin UI: http://localhost:8651
```

## 🚀 Getting Started

### 1. Import Environment Variables

Create a new environment in Postman with these variables:

| Variable Name | Value |
|--------------|-------|
| `base_url` | `http://localhost:8650/api` |
| `speech_url` | `http://localhost:8652/api` |
| `jwt_token` | `{{jwt_token}}` (will be set automatically) |
| `speech_token` | `insight_speech_token_2024` |

### 2. Create a New Collection

1. Open Postman
2. Click "New" → "Collection"
3. Name it "Insight API Tests"
4. Add description: "Complete API testing for Insight API system"

## 🔐 Authentication Tests

### Test 1: Admin Login

**Endpoint:** `POST {{base_url}}/auth/login`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "username": "admin",
  "password": "Apple@123"
}
```

**Test Script (Tests tab):**
```javascript
pm.test("Login successful", function () {
    pm.response.to.have.status(200);
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property('access_token');
    
    // Store JWT token for future requests
    pm.environment.set("jwt_token", responseJson.access_token);
});

pm.test("Response contains role", function () {
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property('role');
    pm.expect(responseJson.role).to.eql('admin');
});
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "role": "admin"
}
```

## 🌍 Public API Tests (No Authentication Required)

### Test 2: Health Check

**Endpoint:** `GET {{base_url}}/public/health`

**Headers:** None required

**Test Script:**
```javascript
pm.test("Health check successful", function () {
    pm.response.to.have.status(200);
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property('status');
    pm.expect(responseJson.status).to.eql('healthy');
});

pm.test("Services status included", function () {
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property('services');
    pm.expect(responseJson.services).to.have.property('database');
    pm.expect(responseJson.services).to.have.property('speech2text');
});
```

### Test 3: Parse Text Message

**Endpoint:** `POST {{base_url}}/public/parse-message`

**Headers:**
```
Content-Type: application/x-www-form-urlencoded
```

**Body (x-www-form-urlencoded):**
```
message: Add Traffic Offence Report. Driver name is James Smith, male, DOB 12/02/2000. Vehicle Registration OU18ZFB a blue BMW 420. Offence is No Seat Belt at Oxford Road, Cheltenham.
```

**Test Script:**
```javascript
pm.test("Text parsing successful", function () {
    pm.response.to.have.status(200);
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property('extracted_info');
    pm.expect(responseJson).to.have.property('text');
    pm.expect(responseJson).to.have.property('id');
});

pm.test("Vehicle information extracted", function () {
    const responseJson = pm.response.json();
    const extracted = responseJson.extracted_info;
    pm.expect(extracted).to.have.property('vehicle_make');
    pm.expect(extracted).to.have.property('vehicle_color');
    pm.expect(extracted).to.have.property('vehicle_model');
});

pm.test("Driver information extracted", function () {
    const responseJson = pm.response.json();
    const extracted = responseJson.extracted_info;
    pm.expect(extracted).to.have.property('driver_name');
});
```

### Test 4: Parse Audio Message

**Endpoint:** `POST {{base_url}}/public/parse-message`

**Headers:**
```
Content-Type: multipart/form-data
```

**Body (form-data):**
- Key: `audio_message`
- Type: File
- Value: Select an audio file (WAV, MP3, MP4, FLAC)

**Test Script:**
```javascript
pm.test("Audio parsing successful", function () {
    pm.response.to.have.status(200);
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property('text');
    pm.expect(responseJson).to.have.property('extracted_info');
    pm.expect(responseJson).to.have.property('processed_output');
});

pm.test("Response time is acceptable", function () {
    pm.expect(pm.response.responseTime).to.be.below(120000); // 2 minutes
});
```

### Test 5: Vehicle Image Identification

**Endpoint:** `POST {{base_url}}/public/car-identifier`

**Headers:**
```
Content-Type: multipart/form-data
```

**Body (form-data):**
- Key: `image`
- Type: File
- Value: Select a vehicle image file (JPG, PNG, GIF, BMP, WebP)

**Test Script:**
```javascript
pm.test("Image processing successful", function () {
    pm.response.to.have.status(200);
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property('extracted_info');
    pm.expect(responseJson).to.have.property('filename');
    pm.expect(responseJson).to.have.property('processed_output');
});

pm.test("Vehicle details extracted", function () {
    const responseJson = pm.response.json();
    const extracted = responseJson.extracted_info;
    
    // At least one vehicle detail should be extracted
    const hasVehicleInfo = 
        extracted.hasOwnProperty('vehicle_make') ||
        extracted.hasOwnProperty('vehicle_color') ||
        extracted.hasOwnProperty('vehicle_model') ||
        extracted.hasOwnProperty('vehicle_registration');
    
    pm.expect(hasVehicleInfo).to.be.true;
});

pm.test("Processing time acceptable for vision model", function () {
    pm.expect(pm.response.responseTime).to.be.below(180000); // 3 minutes for LLaVA 13B
});
```

## 🔒 Admin API Tests (Requires JWT Token)

### Test 6: Dashboard Statistics

**Endpoint:** `GET {{base_url}}/admin/dashboard`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
```

**Test Script:**
```javascript
pm.test("Dashboard access successful", function () {
    pm.response.to.have.status(200);
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property('total_requests');
    pm.expect(responseJson).to.have.property('successful_requests');
    pm.expect(responseJson).to.have.property('success_rate');
});
```

### Test 7: List Parameters

**Endpoint:** `GET {{base_url}}/admin/parameters`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
```

**Test Script:**
```javascript
pm.test("Parameters list retrieved", function () {
    pm.response.to.have.status(200);
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property('data');
    pm.expect(responseJson.data).to.be.an('array');
});
```

### Test 8: Create Parameter

**Endpoint:** `POST {{base_url}}/admin/parameters`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "name": "test_parameter",
  "description": "Test parameter for API testing",
  "active": true
}
```

**Test Script:**
```javascript
pm.test("Parameter created successfully", function () {
    pm.response.to.have.status(201);
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property('data');
    pm.expect(responseJson.data.name).to.eql('test_parameter');
    
    // Store parameter ID for cleanup
    pm.environment.set("test_parameter_id", responseJson.data._id);
});
```

### Test 9: List Requests

**Endpoint:** `GET {{base_url}}/admin/requests`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
```

**Query Parameters:**
- `page`: 1
- `per_page`: 10

**Test Script:**
```javascript
pm.test("Requests list retrieved", function () {
    pm.response.to.have.status(200);
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property('data');
    pm.expect(responseJson).to.have.property('total');
    pm.expect(responseJson).to.have.property('page');
});
```

### Test 10: List Users

**Endpoint:** `GET {{base_url}}/admin/users`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
```

**Test Script:**
```javascript
pm.test("Users list retrieved", function () {
    pm.response.to.have.status(200);
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property('data');
    pm.expect(responseJson.data).to.be.an('array');
});
```

## 🎤 Speech2Text Service Tests

### Test 11: Speech2Text Health Check

**Endpoint:** `GET {{speech_url}}/health`

**Headers:** None required

**Test Script:**
```javascript
pm.test("Speech2Text service healthy", function () {
    pm.response.to.have.status(200);
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property('status');
    pm.expect(responseJson.status).to.eql('healthy');
});

pm.test("Ollama status included", function () {
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property('ollama');
    pm.expect(responseJson.ollama).to.have.property('status');
});
```

### Test 12: Direct Audio Conversion

**Endpoint:** `POST {{speech_url}}/convert`

**Headers:**
```
Authorization: Bearer {{speech_token}}
Content-Type: multipart/form-data
```

**Body (form-data):**
- Key: `audio_file`
- Type: File
- Value: Select an audio file

**Test Script:**
```javascript
pm.test("Audio conversion successful", function () {
    pm.response.to.have.status(200);
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property('text');
    pm.expect(responseJson).to.have.property('processed_output');
});
```

### Test 13: Direct Text Processing

**Endpoint:** `POST {{speech_url}}/process-text`

**Headers:**
```
Authorization: Bearer {{speech_token}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "text": "Officer Smith observed a white BMW speeding at 70 mph in a 55 mph zone on Highway 101"
}
```

**Test Script:**
```javascript
pm.test("Text processing successful", function () {
    pm.response.to.have.status(200);
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property('text');
    pm.expect(responseJson).to.have.property('processed_output');
});
```

## 🧪 Error Testing

### Test 14: Invalid Authentication

**Endpoint:** `GET {{base_url}}/admin/dashboard`

**Headers:**
```
Authorization: Bearer invalid_token
```

**Test Script:**
```javascript
pm.test("Invalid token rejected", function () {
    pm.response.to.have.status(401);
});
```

### Test 15: Missing Required Field

**Endpoint:** `POST {{base_url}}/public/car-identifier`

**Headers:**
```
Content-Type: multipart/form-data
```

**Body:** Empty (no image file)

**Test Script:**
```javascript
pm.test("Missing image file error", function () {
    pm.response.to.have.status(400);
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property('message');
});
```

## 🔄 Collection Runner Tests

### Pre-request Script (Collection Level)

Add this to your collection's Pre-request Script tab:

```javascript
// Set up common variables
pm.globals.set("timestamp", new Date().toISOString());

// Log the request
console.log(`🚀 Running: ${pm.info.requestName}`);
console.log(`📍 URL: ${pm.request.url}`);
```

### Test Script (Collection Level)

Add this to your collection's Tests tab:

```javascript
// Common assertions for all requests
pm.test("Response time is reasonable", function () {
    pm.expect(pm.response.responseTime).to.be.below(30000); // 30 seconds default
});

pm.test("Response has proper headers", function () {
    pm.expect(pm.response.headers.get("Content-Type")).to.include("application/json");
});

// Log response for debugging
console.log(`✅ Response Status: ${pm.response.status}`);
console.log(`⏱️ Response Time: ${pm.response.responseTime}ms`);
```

## 📊 Running the Complete Test Suite

### Option 1: Manual Testing
1. Run tests individually in the order listed above
2. Verify each response manually
3. Check the Test Results tab for pass/fail status

### Option 2: Collection Runner
1. Click "Runner" in Postman
2. Select your "Insight API Tests" collection
3. Choose your environment
4. Set iterations to 1
5. Click "Run Insight API Tests"

### Option 3: Newman (Command Line)
```bash
# Install Newman
npm install -g newman

# Export your collection and environment from Postman
# Then run:
newman run insight-api-tests.json -e insight-api-environment.json
```

## 📝 Sample Test Data

### Text Messages for Testing
```
1. "Officer Johnson stopped red Honda Civic plate ABC123 for speeding 65 in 45 zone on Main Street"
2. "Traffic incident involving blue BMW X5 registration XYZ789, driver Sarah Wilson, hit and run at Park Avenue"
3. "Parking violation white Toyota Camry plate DEF456 parked in handicap space without permit"
```

### Expected Fields in Responses
- `driver_name` / `person_name`
- `vehicle_registration` / `vehicle_number`
- `vehicle_make`
- `vehicle_color`
- `vehicle_model`
- `location` / `location_of_offence`
- `offence` / `event_crime_violation`

## 🚨 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure all services are running: `docker-compose ps`
   - Check ports are accessible: `curl http://localhost:8650/api/public/health`

2. **Authentication Errors**
   - Verify JWT token is valid and not expired
   - Check Bearer token format: `Bearer <token>`

3. **File Upload Issues**
   - Verify file size is under limits (100MB for audio)
   - Check file format is supported
   - Ensure Content-Type is multipart/form-data

4. **Timeout Errors**
   - Increase timeout in Postman settings
   - Check Ollama service is responding
   - Verify sufficient system resources

### Debug Commands
```bash
# Check service logs
docker logs insight-api-officer-insight-api-1
docker logs insight-api-speech2text-service-1

# Check service health
curl http://localhost:8650/api/public/health
curl http://localhost:8652/api/health
```

## 📈 Performance Benchmarks

### Expected Response Times
- Health checks: < 1 second
- Text processing: 5-15 seconds
- Audio processing: 30-120 seconds
- Image processing: 60-180 seconds (LLaVA 13B)
- Admin operations: < 5 seconds

### Resource Usage
- Monitor CPU and memory during testing
- Large model processing (LLaVA 13B) requires more resources
- Audio files increase processing time based on duration

This comprehensive testing guide covers all aspects of the Insight API system. Use it to validate functionality, performance, and reliability of your API endpoints.
