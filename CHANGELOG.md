# Changelog - Insight API

All notable changes to this project will be documented in this file.

## [2.4.0] - 2025-08-22 - Microservices Architecture Refactoring

### 🚀 Major Architectural Changes
- **BREAKING CHANGE**: Refactored system into microservices architecture
- **NEW SERVICE**: Created dedicated Car Identifier Service (Port 8653)
- **ENHANCED**: Separated vehicle analysis into independent microservice
- **IMPROVED**: Configurable extraction fields and AI model parameters

### ✨ New Features

#### Car Identifier Service
- **Independent Service**: Dedicated microservice for vehicle image analysis
- **Configurable Parameters**: Environment-based configuration for extraction fields
- **Enhanced Performance**: Specialized service with optimized resource usage
- **API Compatibility**: Maintains same `/api/public/car-identifier` endpoint

#### Configuration System
- **Environment Variables**: Full configuration through .env files
- **Flexible Fields**: Configurable extraction parameters
- **Model Settings**: Adjustable AI model timeouts and parameters
- **Service Limits**: Configurable file size and format restrictions

#### Enhanced Documentation
- **Service Documentation**: Comprehensive README for car-identifier-service
- **API Updates**: Updated API documentation for all services
- **Deployment Guides**: Enhanced deployment and configuration guides
- **Architecture Diagrams**: Updated system architecture documentation

### 🔧 Technical Improvements

#### Service Configuration
```bash
VISION_MODEL=gemma3:12b                    # AI model for vehicle analysis
EXTRACTION_FIELDS=vehicle_registration,vehicle_make,vehicle_color,vehicle_model
MODEL_TIMEOUT=180                          # Processing timeout in seconds
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,bmp,webp
MAX_CONTENT_LENGTH=16777216               # 16MB file size limit
```

#### Deployment Updates
- **Docker Compose**: Updated configuration with car-identifier-service
- **Build Scripts**: Enhanced build process for all services
- **Health Checks**: Improved monitoring for all services
- **Service Dependencies**: Proper dependency management

### 📚 Documentation Updates
- **README.md**: Complete overhaul reflecting microservices architecture
- **API_DOCUMENTATION.md**: Updated with all service endpoints
- **Car Identifier Service**: New comprehensive service documentation
- **Deployment Guides**: Updated for new architecture

### 🔄 Migration Guide

#### For Existing Users
1. **API Compatibility**: All existing endpoints remain functional
2. **Service Access**: Car identifier available at both ports 8650 and 8653
3. **Configuration**: New environment variables for enhanced customization
4. **Deployment**: Use updated docker-compose.yml

#### Breaking Changes
- System now requires four services instead of three
- New environment variables for car-identifier-service
- Enhanced resource requirements for additional service

### 🚀 Performance Improvements
- **Service Isolation**: Independent scaling of vehicle analysis
- **Resource Optimization**: Better resource allocation per service
- **Concurrent Processing**: Enhanced parallel processing capabilities
- **Error Isolation**: Service-specific error handling and recovery

## [2.3.0] - 2025-08-22 - Gemma3 Vision Model & Enhanced Response

### 🚀 Major Changes
- **BREAKING CHANGE**: Upgraded from LLaVA to Gemma3:12b vision model for vehicle identification
- **NEW FEATURE**: Enhanced API response format includes model name for transparency
- **IMPROVED**: Better vision processing capabilities with Gemma3 model

### ✨ Features Added
- **Enhanced Vehicle Image Identification**:
  - Upgraded to Gemma3:12b vision model for superior accuracy
  - Model name included in API response: `"model": "gemma3:12b"`
  - Improved vehicle recognition capabilities
  - Better license plate detection and reading

- **Transparent AI Processing**:
  - API responses now show which model processed the request
  - Enhanced debugging and audit capabilities
  - Better tracking of AI model performance

### 🔧 Technical Improvements
- **Model Configuration**: Updated `process_image_with_ollama` function to use Gemma3:12b
- **Response Enhancement**: Added model field to car-identifier API response
- **Extended Timeout**: Increased processing timeout to 180 seconds for model processing
- **Container Optimization**: Proper deployment with fresh container rebuild

### 🔄 Migration Changes
- **Model Update**: Changed from `llava:13b-v1.5-fp16` to `gemma3:12b`
- **API Response**: Added `model` field to car-identifier endpoint response
- **Documentation**: Updated all setup guides to use Gemma3 model

### 📚 Documentation Updates
- Updated README.md with Gemma3 setup instructions
- Enhanced API documentation with new response format
- Updated all examples to reflect model name inclusion
- Modified installation guides for Gemma3 model

### 🛠️ Developer Experience
- **Deployment Verification**: Enhanced container rebuild and restart procedures
- **Testing Improvements**: Better validation of deployed changes
- **Monitoring**: Model name tracking for better system observability

### 📋 Migration Notes
1. **Required Action**: Update Ollama installation to use `ollama pull gemma3:12b`
2. **API Changes**: Car-identifier responses now include model field
3. **Backward Compatibility**: Existing API structure maintained, only enhanced
4. **Performance**: Similar or improved processing times with Gemma3 model

## [2.2.1] - 2025-08-12 - Enhanced Vision Model

### 🔧 Technical Improvements
- **Upgraded Vision Model**: Updated from `llava` to `llava:13b-v1.5-fp16` for better accuracy
- **Enhanced Processing**: Improved vehicle identification with larger 13B parameter model
- **FP16 Precision**: Better memory efficiency while maintaining high accuracy
- **Extended Timeout**: Increased processing timeout to 180 seconds for larger model

### 📚 Documentation Updates
- Updated setup instructions for LLaVA 13B model installation
- Enhanced README.md with new model requirements
- Updated API documentation with improved model specifications

## [2.2.0] - 2025-08-12 - Vehicle Image Identification

### 🚀 Major Features Added
- **NEW API Endpoint**: `/api/public/car-identifier` for vehicle image identification
- **AI Vision Integration**: Uses Ollama LLaVA vision model for image analysis
- **Vehicle Recognition**: Automatic identification of vehicle make, color, model, and license plate
- **Image Processing**: Support for multiple image formats (JPG, PNG, GIF, BMP, WebP)

### ✨ Features Added
- **Vehicle Image Identification API**:
  - New `/api/public/car-identifier` endpoint
  - AI-powered license plate recognition
  - Vehicle make, color, and model identification
  - Support for multiple image formats
  - Comprehensive error handling and validation

- **Enhanced AI Capabilities**:
  - Integration with Ollama LLaVA vision model
  - Advanced prompt engineering for vehicle identification
  - Structured data extraction from vehicle images
  - Base64 image encoding for AI processing

### 🔧 Technical Improvements
- Added Pillow (PIL) dependency for image processing
- Enhanced API documentation with image endpoint examples
- Updated Swagger documentation with new car-identifier model
- Improved error handling for image processing workflows

### 📚 Documentation Updates
- Updated README.md with vehicle image identification examples
- Enhanced API_DOCUMENTATION.md with complete endpoint specification
- Added supported image formats documentation
- Updated feature descriptions to include vision capabilities

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
