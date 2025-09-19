# Postman Collections for Insight API System

This directory contains comprehensive Postman collections for testing all microservices in the Insight API system.

## Collection Organization

### 📁 Service-Specific Collections

#### 1. **Officer-Insight-API-Complete.json**
- **Purpose**: Complete collection for Officer Insight API service
- **Port**: 8650
- **Features**: 
  - Authentication (JWT)
  - Image Management (Upload, List, Delete, Serve)
  - Person Management (CRUD, Search, Soft Delete)
  - Vehicle Management (CRUD, Search, Soft Delete)
  - Text/Audio Processing
  - Health Checks

#### 2. **Car-Identifier-Service.json**
- **Purpose**: Vehicle image analysis service
- **Port**: 8653
- **Features**:
  - Vehicle identification from images
  - Extraction history management
  - Admin operations

#### 3. **Doc-Reader-Service.json**
- **Purpose**: Document parsing service (passports, IDs)
- **Port**: 8654
- **Features**:
  - Document information extraction
  - Extraction history management
  - Admin operations

#### 4. **Speech2Text-Service.json**
- **Purpose**: Audio transcription service
- **Port**: 8652
- **Features**:
  - Audio to text conversion
  - Whisper model integration

### 📁 System Collections

#### 5. **Complete-System-Collection.json**
- **Purpose**: System-wide testing across all services
- **Features**:
  - Health checks for all services
  - Cross-service workflows
  - Integration testing
  - All service endpoints in one collection

#### 6. **Legacy Collections**
- `Insight-API-Test-Collection.json` - Original comprehensive test suite
- `Insight-API-Local-Environment.json` - Environment configuration

## How to Use

### 1. **Import Collections**
1. Open Postman
2. Click "Import" button
3. Select the desired collection JSON file(s)
4. Collections will appear in your Postman workspace

### 2. **Set Up Environment Variables**
Each collection uses variables for easy configuration:

```
officer_api_url: http://localhost:8650/api
car_identifier_url: http://localhost:8653/api
doc_reader_url: http://localhost:8654/api
speech2text_url: http://localhost:8652/api
admin_ui_url: http://localhost:8651
```

### 3. **Authentication Flow**
1. Run "Admin Login" request in any collection
2. Token will be automatically stored in collection variables
3. Subsequent requests will use the stored token

### 4. **Testing Workflow**

#### **Quick System Check**
Use `Complete-System-Collection.json`:
1. Run "System Health Checks" folder
2. Verify all services are running

#### **Service-Specific Testing**
Use individual service collections:
1. Start with health check
2. Test core functionality
3. Verify data operations

#### **Full Integration Testing**
Use `Officer-Insight-API-Complete.json`:
1. Authenticate
2. Upload images
3. Create person/vehicle records
4. Test search functionality
5. Verify data integrity

## Collection Features

### 🔐 **Authentication**
- Automatic token handling
- JWT bearer token authentication
- Token storage in collection variables

### 📝 **Test Scripts**
- Response validation
- Status code checks
- Data extraction and storage

### 🔄 **Environment Management**
- Configurable base URLs
- Environment-specific settings
- Easy switching between environments

### 📊 **Comprehensive Coverage**
- All CRUD operations
- Search functionality
- File uploads
- Error handling
- Health monitoring

## Configuration for Different Environments

### **Local Development**
```json
{
  "officer_api_url": "http://localhost:8650/api",
  "car_identifier_url": "http://localhost:8653/api",
  "doc_reader_url": "http://localhost:8654/api",
  "speech2text_url": "http://localhost:8652/api"
}
```

### **Docker Deployment**
```json
{
  "officer_api_url": "http://docker-host:8650/api",
  "car_identifier_url": "http://docker-host:8653/api",
  "doc_reader_url": "http://docker-host:8654/api",
  "speech2text_url": "http://docker-host:8652/api"
}
```

### **Production Environment**
```json
{
  "officer_api_url": "https://api.insight-system.com/officer/api",
  "car_identifier_url": "https://api.insight-system.com/car-identifier/api",
  "doc_reader_url": "https://api.insight-system.com/doc-reader/api",
  "speech2text_url": "https://api.insight-system.com/speech2text/api"
}
```

## File Structure
```
postman/
├── Officer-Insight-API-Complete.json      # Main service collection
├── Car-Identifier-Service.json            # Vehicle analysis service
├── Doc-Reader-Service.json                # Document parsing service
├── Speech2Text-Service.json               # Audio transcription service
├── Complete-System-Collection.json        # Full system integration
├── Insight-API-Test-Collection.json       # Legacy comprehensive suite
├── Insight-API-Local-Environment.json     # Environment variables
└── README.md                              # This documentation
```

## Testing Best Practices

1. **Start with Health Checks**: Always verify service availability
2. **Authenticate First**: Run login request before protected endpoints
3. **Use Test Data**: Create test records for consistent testing
4. **Clean Up**: Delete test data after testing when appropriate
5. **Monitor Responses**: Check response times and data integrity
6. **Environment Variables**: Use variables for easy environment switching

## Troubleshooting

### Common Issues
- **Authentication Failures**: Ensure login request runs successfully
- **Connection Errors**: Verify services are running on correct ports
- **File Upload Issues**: Check file paths and permissions
- **Token Expiration**: Re-run login request if tokens expire

### Support
For issues or questions:
1. Check service health endpoints
2. Verify Docker containers are running
3. Review service logs for errors
4. Ensure proper environment configuration
