#!/bin/bash

# Postman Test Setup Script
# This script helps set up sample files for testing the Insight API with Postman

set -e

echo "🚀 Setting up Postman testing environment for Insight API..."

# Create test data directory
TEST_DIR="./test-data"
mkdir -p "$TEST_DIR"

echo "📁 Created test data directory: $TEST_DIR"

# Create sample text files with test messages
cat > "$TEST_DIR/sample-text-messages.txt" << 'EOF'
# Sample Text Messages for API Testing

## Traffic Violations
1. "Officer Johnson stopped red Honda Civic plate ABC123 for speeding 65 in 45 zone on Main Street at 2:30 PM"

2. "Add Traffic Offence Report. Driver name is James Smith, male, DOB 12/02/2000. Vehicle Registration OU18ZFB a blue BMW 420. Offence is No Seat Belt at Oxford Road, Cheltenham."

3. "Traffic incident involving blue BMW X5 registration XYZ789, driver Sarah Wilson, hit and run at Park Avenue"

4. "Parking violation white Toyota Camry plate DEF456 parked in handicap space without permit at Downtown Mall"

5. "Officer Martinez observed black Mercedes E-Class license WER234 running red light at 5th Avenue intersection"

## Vehicle Incidents
6. "Silver Nissan Altima registration QWE567 involved in rear-end collision, driver Michael Brown, no injuries reported"

7. "Green Ford F-150 truck plate RTY890 illegally parked in fire lane at Shopping Center Plaza"

8. "Yellow school bus number 45 speeding in residential zone, driver reported by multiple witnesses"

## Complex Reports
9. "Multiple vehicle accident: Red Toyota Corolla ABC123, Blue Honda Accord DEF456, and White Ford Explorer GHI789 collision at Highway 101 and Oak Street. Driver of Toyota identified as Jennifer Davis, DOB 08/15/1992. No serious injuries. Traffic backup for 2 hours."

10. "DUI checkpoint stop: Black Audi A4 license UIO123 driver Robert Johnson failed sobriety test. Vehicle impounded. Driver arrested and taken to county jail."
EOF

echo "📝 Created sample text messages file"

# Create a simple test audio message (requires text-to-speech or manual recording)
cat > "$TEST_DIR/audio-test-instructions.md" << 'EOF'
# Audio File Testing Instructions

For testing audio endpoints, you need actual audio files. Here are options:

## Option 1: Record Your Own Audio
Use your phone or computer to record these messages:

1. "Officer Johnson reporting. Red Honda Civic license plate ABC one two three stopped for speeding on Main Street."

2. "Traffic violation report. Blue BMW four twenty registration OU eighteen ZFB. Driver James Smith. No seat belt violation."

3. "Vehicle identification needed. White Toyota Camry parked illegally in handicap space."

## Option 2: Use Text-to-Speech Tools
1. Go to online TTS services like Google Text-to-Speech, Amazon Polly, or others
2. Convert the sample messages above to audio files
3. Save as WAV, MP3, or MP4 format
4. Place files in this test-data directory

## Option 3: Download Sample Files
Visit these sites for free audio samples:
- https://freesound.org/ (requires account)
- https://archive.org/ (public domain audio)
- Record short voice memos on your device

## Supported Formats
- WAV (recommended)
- MP3
- MP4
- FLAC
- File size limit: 100MB
EOF

echo "🎤 Created audio testing instructions"

# Create sample vehicle image instructions
cat > "$TEST_DIR/image-test-instructions.md" << 'EOF'
# Vehicle Image Testing Instructions

For testing the car-identifier API endpoint, you need vehicle images. Here are options:

## Image Requirements
- **Formats**: JPG, PNG, GIF, BMP, WebP
- **Content**: Clear photos of vehicles
- **Quality**: Higher resolution gives better results
- **Angle**: Front, side, or rear views work best

## Sample Image Sources
1. **Take Your Own Photos**: Use your phone to photograph vehicles (ensure privacy)
2. **Stock Photo Sites**: 
   - Unsplash.com (free stock photos)
   - Pexels.com (free vehicle photos)
   - Pixabay.com (free images)
3. **Search Terms**: "car front view", "vehicle license plate", "BMW sedan", etc.

## Best Practices for Testing
- Include license plates when possible
- Clear lighting conditions
- Avoid heavily cropped images
- Test with different vehicle makes/models
- Try various colors and angles

## Test Scenarios
1. **Clear License Plate**: Front view with visible registration
2. **Side View**: Profile shot showing make/model
3. **Multiple Vehicles**: Test with different car types
4. **Various Lighting**: Daylight, overcast, parking lot lighting
5. **Different Angles**: Front, rear, 3/4 view

## Expected Results
The API should identify:
- Vehicle Make (BMW, Toyota, Ford, etc.)
- Vehicle Color (Blue, Red, Black, etc.)
- Vehicle Model (320i, Camry, Focus, etc.)
- Vehicle Registration (if clearly visible)
EOF

echo "📸 Created vehicle image testing instructions"

# Create Postman import instructions
cat > "$TEST_DIR/postman-import-guide.md" << 'EOF'
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
EOF

echo "📋 Created Postman import guide"

# Create a comprehensive test checklist
cat > "$TEST_DIR/testing-checklist.md" << 'EOF'
# API Testing Checklist

Use this checklist to ensure comprehensive testing of the Insight API system.

## Pre-Testing Setup
- [ ] All Docker services are running (`docker-compose ps`)
- [ ] Health checks pass (8650/api/public/health, 8652/api/health)
- [ ] Postman collection and environment imported
- [ ] Test files prepared (audio files, vehicle images)
- [ ] LLaVA 13B model pulled (`ollama list` shows llava:13b-v1.5-fp16)

## Authentication Testing
- [ ] Admin login successful (returns JWT token)
- [ ] JWT token automatically stored in environment
- [ ] Invalid credentials rejected (401 error)
- [ ] Token expiration handling

## Public API Testing
- [ ] Health check returns healthy status
- [ ] Text message parsing with vehicle information
- [ ] Text message parsing with driver information
- [ ] Audio file processing (if audio files available)
- [ ] Vehicle image identification (if images available)
- [ ] Error handling for missing parameters
- [ ] Error handling for invalid file formats

## Admin API Testing (Requires JWT)
- [ ] Dashboard statistics retrieval
- [ ] Parameters list retrieval
- [ ] Parameter creation
- [ ] Parameter updates (optional)
- [ ] Requests monitoring list
- [ ] Users list retrieval
- [ ] User creation (optional)

## Speech2Text Service Testing
- [ ] Health check with Ollama status
- [ ] Direct audio conversion (if audio available)
- [ ] Direct text processing
- [ ] Authentication with Bearer token
- [ ] Error handling for missing auth

## Vehicle Image Testing (LLaVA 13B)
- [ ] Image upload successful
- [ ] Vehicle make identification
- [ ] Vehicle color identification
- [ ] Vehicle model identification
- [ ] License plate recognition (if visible)
- [ ] Processing time under 3 minutes
- [ ] Multiple image format support
- [ ] Error handling for missing image

## Performance Testing
- [ ] Text processing under 30 seconds
- [ ] Audio processing under 2 minutes
- [ ] Image processing under 3 minutes
- [ ] Concurrent request handling
- [ ] Memory usage reasonable during processing

## Error Handling Testing
- [ ] Invalid authentication tokens
- [ ] Missing required parameters
- [ ] Unsupported file formats
- [ ] Network connectivity issues
- [ ] Service unavailability scenarios

## Data Validation Testing
- [ ] Extracted vehicle make is reasonable
- [ ] Extracted vehicle color is accurate
- [ ] Extracted vehicle model is specific
- [ ] License plate format validation
- [ ] Driver information extraction
- [ ] Location information parsing

## Integration Testing
- [ ] Officer Insight API → Speech2Text integration
- [ ] Officer Insight API → Ollama integration
- [ ] Database persistence working
- [ ] Request logging functional
- [ ] Admin UI connectivity (manual check)

## Cleanup Testing
- [ ] Remove test parameters created
- [ ] Verify no test data persists
- [ ] Clean environment state

## Documentation Verification
- [ ] API responses match documentation
- [ ] Error messages are helpful
- [ ] Response times documented accurately
- [ ] All endpoints documented work as described

## Success Criteria
✅ All health checks pass
✅ Authentication works properly
✅ Text processing extracts vehicle info correctly
✅ Image processing identifies vehicles accurately
✅ Admin functions work with proper authorization
✅ Error handling is graceful and informative
✅ Performance meets documented expectations
EOF

echo "✅ Created comprehensive testing checklist"

echo ""
echo "🎉 Postman testing setup complete!"
echo ""
echo "📁 Files created in $TEST_DIR:"
echo "   - sample-text-messages.txt (ready-to-use test messages)"
echo "   - audio-test-instructions.md (guide for audio file setup)"
echo "   - image-test-instructions.md (guide for vehicle image setup)"
echo "   - postman-import-guide.md (step-by-step Postman setup)"
echo "   - testing-checklist.md (comprehensive testing checklist)"
echo ""
echo "🚀 Next steps:"
echo "   1. Import postman/Insight-API-Test-Collection.json into Postman"
echo "   2. Import postman/Insight-API-Local-Environment.json into Postman"
echo "   3. Ensure all services are running: ./scripts/start.sh"
echo "   4. Follow the testing checklist in test-data/testing-checklist.md"
echo ""
echo "📖 For detailed instructions, see: POSTMAN_TESTING_GUIDE.md"
echo ""
