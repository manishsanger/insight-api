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
