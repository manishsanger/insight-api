# Changelog - Insight API

All notable changes to this project will be documented in this file.

## [2.1.0] - 2025-08-12 - Enhanced Vehicle Field Separation

### ✨ Features Added
- **Enhanced Vehicle Information Extraction**: Vehicle data now separated into distinct fields
  - **Vehicle Make**: Car manufacturer/brand only (e.g., BMW, Toyota, Ford)
  - **Vehicle Color**: Vehicle color only (e.g., Blue, Red, Black)
  - **Vehicle Model**: Vehicle model/series only (e.g., 420, Camry, Focus)
- **Improved Prompt Engineering**: Updated Ollama prompts for better field separation
- **Updated Default Parameters**: Modified extraction parameters to use new vehicle fields
- **Backward Compatibility**: Legacy parameter names still supported for existing integrations

### 🔧 Technical Improvements
- Enhanced Ollama prompt templates for more precise vehicle information extraction
- Updated API documentation with new field examples
- Improved regex fallback patterns for vehicle field extraction
- Better field naming consistency across all services

### 📚 Documentation Updates
- Updated README.md with new vehicle field examples
- Enhanced API_DOCUMENTATION.md with separated vehicle field specifications
- Updated example responses to reflect new field structure

## [2.0.0] - 2025-08-12 - Ollama AI Integration

### 🚀 Major Changes
- **BREAKING CHANGE**: Replaced OpenAI Whisper with Ollama AI for text processing
- **NEW**: Enhanced AI-powered structured data extraction using llama3.2:latest model
- **NEW**: Advanced prompt engineering for traffic offense report parsing
- **NEW**: Direct text processing endpoint for immediate AI analysis

### ✨ Features Added
- **Ollama Integration**: Complete migration from Whisper to Ollama AI
  - Uses llama3.2:latest model for superior text processing
  - Enhanced prompt engineering for structured data extraction
  - Optimized for traffic offense report parsing
  - No authentication required for Ollama service

- **Enhanced Speech2Text Service**:
  - New `/api/process-text` endpoint for direct text processing
  - Improved `/api/convert` endpoint with AI-powered analysis
  - Enhanced health checks with Ollama connectivity monitoring
  - Better error handling and response formatting

- **Improved API Responses**:
  - Structured data extraction with consistent field formatting
  - Enhanced `processed_output` with organized information
  - Better `extracted_info` parsing with key-value pairs
  - Standardized date formats and field naming

- **Documentation Overhaul**:
  - Complete API documentation with integration examples
  - Updated service-specific README files
  - Enhanced deployment guide with Ollama requirements
  - New troubleshooting sections for Ollama connectivity

### 🔧 Technical Improvements
- **Container Architecture**:
  - Removed Whisper, torch, and torchaudio dependencies
  - Streamlined Python requirements for better performance
  - Maintained FFmpeg for audio preprocessing
  - Optimized Docker images for faster builds

- **AI Processing Pipeline**:
  - Enhanced prompt templates for consistent output format
  - Improved error handling for AI service failures
  - Better timeout management for long-running requests
  - Structured response parsing and validation

- **Health Monitoring**:
  - Enhanced health checks with Ollama service status
  - Model availability verification
  - Network connectivity testing
  - Storage and dependency monitoring

### 🔄 Migration Changes
- **Removed Dependencies**:
  - `openai-whisper==20231117`
  - `torch==2.0.1`
  - `torchaudio==2.0.2`
  - `numpy` (Whisper dependency)

- **Added Dependencies**:
  - Enhanced `requests` integration for Ollama API
  - Improved JSON processing for structured responses

- **Configuration Updates**:
  - New environment variables: `OLLAMA_URL`, `OLLAMA_MODEL`
  - Updated Docker Compose with Ollama service configuration
  - Enhanced network configuration for container communication

### 📊 Performance Improvements
- **Reduced Resource Usage**:
  - Smaller container images without ML model dependencies
  - Lower memory requirements for audio processing
  - Faster container startup times

- **Enhanced Processing**:
  - More accurate structured data extraction
  - Better handling of various text formats
  - Improved response consistency and reliability

### 🛠️ Developer Experience
- **Enhanced APIs**:
  - Better error messages and response codes
  - Improved API documentation with examples
  - More consistent endpoint behavior

- **Testing Improvements**:
  - Updated test suites for Ollama integration
  - Enhanced health check validation
  - Better integration testing coverage

### 🔒 Security & Stability
- **Maintained Security**:
  - Same authentication mechanisms
  - Preserved token-based access control
  - Continued input validation and sanitization

- **Improved Reliability**:
  - Better error handling for AI service failures
  - Enhanced timeout management
  - Improved service health monitoring

### 📋 Migration Notes

#### For Existing Users
1. **Service Restart Required**: All containers must be rebuilt and restarted
2. **API Compatibility**: Public API endpoints remain the same, only response format enhanced
3. **Configuration**: No changes to existing environment variables, new ones are optional
4. **Data Preservation**: All existing data in MongoDB is preserved

#### For Developers
1. **Dependencies**: Update local development environments to remove Whisper dependencies
2. **Testing**: Update test cases to work with new Ollama-based responses
3. **Integration**: API contracts remain the same, enhanced with new fields

#### Breaking Changes
- Response format for `/api/convert` now includes `processed_output` field
- Health check responses include Ollama service status
- Some internal processing timeouts may vary due to AI processing

### 🎯 Use Case Enhancements

#### Traffic Offense Reports
- **Enhanced Extraction**: Better recognition of vehicle information, driver details, and offense specifics
- **Standardized Format**: Consistent field naming and date formats across all extractions
- **Improved Accuracy**: More reliable extraction of license plates, locations, and violation types

#### Law Enforcement Integration
- **Structured Output**: Easy integration with law enforcement databases and systems
- **Configurable Fields**: Maintain existing parameter management for custom extraction needs
- **Audit Trail**: Complete request logging and monitoring capabilities preserved

### 🔮 Future Roadmap
- **Model Flexibility**: Support for additional Ollama models based on use case requirements
- **Enhanced Prompts**: Continued optimization of prompt engineering for specific domains
- **API Extensions**: Additional endpoints for specialized processing needs
- **Performance Scaling**: Container orchestration optimizations for high-volume usage

### 🙏 Acknowledgments
- Ollama team for providing the excellent AI model infrastructure
- Community feedback for identifying areas of improvement in structured data extraction
- Testing teams for validating the migration and ensuring system stability

---

## [1.0.0] - 2024-07-25 - Initial Release

### ✨ Initial Features
- **Officer Insight API**: Complete REST API with JWT authentication
- **Speech2Text Service**: OpenAI Whisper integration for audio transcription
- **Admin UI**: React-based administrative interface
- **MongoDB Integration**: Persistent data storage and management
- **Docker Orchestration**: Complete containerized deployment
- **Management Scripts**: Automated startup, shutdown, and maintenance tools

### 🔧 Core Functionality
- Audio file to text conversion using Whisper
- Text message processing and information extraction
- Parameter management for customizable extraction
- User management with role-based access control
- Dashboard with statistics and monitoring
- Health check endpoints for all services

### 📚 Documentation
- Comprehensive README files for all services
- Deployment guide with production considerations
- API documentation with Swagger integration
- Troubleshooting guides and examples

### 🏗️ Architecture
- Microservices-based design
- Docker Compose orchestration
- Persistent volume mounting
- Network isolation and security
- Scalable container architecture

---

## Version History Summary

| Version | Date | Major Changes |
|---------|------|---------------|
| 2.0.0 | 2025-08-12 | Ollama AI Integration, Enhanced Processing |
| 1.0.0 | 2024-07-25 | Initial Release with Whisper Integration |

---

For detailed migration instructions and technical specifications, see:
- `DEPLOYMENT.md` - Deployment and configuration guide
- `API_DOCUMENTATION.md` - Complete API reference
- Service-specific README files for detailed implementation notes
