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
