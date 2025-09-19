import os
import requests
import base64
from datetime import datetime
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_restx import Api, Resource, fields, Namespace
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import json
from bson import ObjectId
from PIL import Image
import io

# Configure custom JSON encoder
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

def serialize_mongo_doc(doc):
    """Recursively serialize MongoDB document to be JSON serializable"""
    if isinstance(doc, dict):
        return {key: serialize_mongo_doc(value) for key, value in doc.items()}
    elif isinstance(doc, list):
        return [serialize_mongo_doc(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, datetime):
        return doc.isoformat()
    else:
        return doc

# Initialize Flask app
app = Flask(__name__)

# Apply the custom JSON encoder to handle ObjectId and datetime serialization
app.json_encoder = CustomJSONEncoder

# Configuration from environment variables
app.config['MONGO_URI'] = os.getenv('MONGODB_URI', 'mongodb://admin:Apple%40123@mongodb:27017/insight_db?authSource=admin')
app.config['OLLAMA_URL'] = os.getenv('OLLAMA_URL', 'http://host.docker.internal:11434')
app.config['VISION_MODEL'] = os.getenv('VISION_MODEL', 'gemma3:12b')
app.config['MODEL_TIMEOUT'] = int(os.getenv('MODEL_TIMEOUT', '180'))
app.config['ALLOWED_EXTENSIONS'] = set(os.getenv('ALLOWED_EXTENSIONS', 'jpg,jpeg,png,gif,bmp,webp').split(','))
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', str(16 * 1024 * 1024)))  # 16MB default

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens don't expire (optional)

# Initialize JWT
jwt = JWTManager(app)

# Configurable extraction parameters
DEFAULT_EXTRACTION_FIELDS = [
    'vehicle_registration',
    'vehicle_make', 
    'vehicle_color',
    'vehicle_model'
]

CONFIGURABLE_FIELDS = os.getenv('EXTRACTION_FIELDS', ','.join(DEFAULT_EXTRACTION_FIELDS)).split(',')

# Initialize extensions
mongo = PyMongo(app)
CORS(app, origins=os.getenv('CORS_ORIGINS', 'http://localhost:8651,http://localhost:3000').split(','), supports_credentials=True)

# API Documentation
api = Api(app, version='1.0', title='Car Identifier Service API',
          description='AI-powered vehicle identification service using computer vision',
          doc='/docs/')

# Override Flask-RESTX JSON output to use our custom JSON serialization
def custom_output_json(data, code, headers=None):
    """Custom JSON output that handles MongoDB ObjectId and datetime"""
    try:
        # Serialize the data first to handle ObjectId and datetime
        serialized_data = serialize_mongo_doc(data)
        
        # Use our custom encoder for JSON serialization
        dumped = json.dumps(serialized_data, cls=CustomJSONEncoder, ensure_ascii=False, indent=None, separators=(',', ':')) + '\n'
        
        resp = app.response_class(dumped, status=code, mimetype='application/json')
        if headers:
            resp.headers.extend(headers)
        return resp
    except Exception as e:
        print(f"Error in custom_output_json: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to default JSON handling
        fallback = json.dumps({'error': 'Serialization error'}) + '\n'
        return app.response_class(fallback, status=500, mimetype='application/json')

# Override the default JSON representation
api.representations['application/json'] = custom_output_json

# Namespaces
public_ns = Namespace('public', description='Public API operations (health only)')
api.add_namespace(public_ns, path='/api/public')

# Secured namespace for authenticated endpoints
api_ns = Namespace('api', description='Authenticated API operations')
api.add_namespace(api_ns, path='/api')

# Models for Swagger documentation
car_image_model = api.model('CarImage', {
    'image': fields.Raw(required=True, description='Vehicle image file (JPG, PNG, etc.)')
})

def process_image_with_ollama(image_file):
    """Process vehicle image using Ollama vision model for car identification"""
    try:
        # Read and process the image
        image_data = image_file.read()
        image_file.seek(0)  # Reset file pointer
        
        # Convert image to base64 for Ollama vision model
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Create dynamic prompt based on configured fields
        field_descriptions = {
            'vehicle_registration': 'Vehicle Registration: [license plate number if visible]',
            'vehicle_make': 'Vehicle Make: [car manufacturer/brand, e.g., BMW, Toyota, Ford]',
            'vehicle_color': 'Vehicle Color: [primary vehicle color, e.g., Blue, Red, Black]',
            'vehicle_model': 'Vehicle Model: [car model/series, e.g., 320i, Camry, Focus]',
            'vehicle_type': 'Vehicle Type: [car, truck, SUV, motorcycle, etc.]',
            'vehicle_year': 'Vehicle Year: [estimated year of manufacture if identifiable]',
            'vehicle_condition': 'Vehicle Condition: [new, used, damaged, etc.]'
        }
        
        prompt_fields = []
        for field in CONFIGURABLE_FIELDS:
            if field.strip() in field_descriptions:
                prompt_fields.append(f"- {field_descriptions[field.strip()]}")
        
        prompt = f"""
Analyze this vehicle image and extract the following information in this exact format:

{chr(10).join(prompt_fields)}

Only include fields that you can clearly identify from the image. If information is not visible or unclear, omit that field.
Focus on identifying the vehicle details based on what is actually visible in the image.
"""

        response = requests.post(
            f"{app.config['OLLAMA_URL']}/api/generate",
            json={
                "model": app.config['VISION_MODEL'],
                "prompt": prompt,
                "images": [image_base64],
                "stream": False
            },
            timeout=app.config['MODEL_TIMEOUT']
        )
        
        if response.status_code == 200:
            result = response.json()
            processed_text = result.get('response', '').strip()
            
            # Parse the structured response into a dictionary
            extracted_data = {}
            lines = processed_text.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Handle lines with colons (with or without bullet points)
                if ':' in line:
                    content = line
                    
                    # Remove various bullet point prefixes if present
                    if line.startswith('- '):
                        content = line[2:]
                    elif line.startswith('* '):
                        content = line[2:]
                    elif line.startswith('-'):
                        content = line[1:].strip()
                    elif line.startswith('*'):
                        content = line[1:].strip()
                    
                    try:
                        parts = content.split(':', 1)
                        if len(parts) == 2:
                            key, value = parts
                            key = key.strip()
                            value = value.strip()
                            
                            # Clean up value - handle brackets intelligently
                            if '[' in value and ']' in value:
                                bracket_start = value.find('[')
                                bracket_end = value.find(']')
                                
                                if bracket_start == 0:
                                    # Value starts with bracket, extract content from within
                                    bracket_content = value[1:bracket_end].strip()
                                    
                                    # Check if bracket content is meaningful data (not description)
                                    if (bracket_content and 
                                        len(bracket_content) > 2 and
                                        not any(desc in bracket_content.lower() for desc in [
                                            'license plate', 'plate number', 'number in', 'visible', 
                                            'not clear', 'unknown', 'green', 'blue', 'color'
                                        ])):
                                        value = bracket_content
                                    else:
                                        # Check for content after bracket
                                        after_bracket = value[bracket_end + 1:].strip()
                                        if after_bracket:
                                            value = after_bracket
                                        else:
                                            # If bracket contains description, skip this value
                                            continue
                                else:
                                    # Content before bracket, use that
                                    value = value[:bracket_start].strip()
                            
                            # Validate the value is meaningful
                            if (value and 
                                len(value) > 0 and 
                                value.lower() not in ['[not visible]', '[not clear]', '[unknown]', 'n/a', 'none', '', 'unknown'] and
                                not any(desc in value.lower() for desc in [
                                    'license plate number', 'plate number', 'number in green', 
                                    'number in blue', 'visible in', 'not visible', 'not clear'
                                ])):
                                
                                field_name = key.lower().replace(' ', '_')
                                extracted_data[field_name] = value
                    
                    except Exception:
                        # Skip lines that can't be processed
                        continue
            
            return processed_text, extracted_data
        else:
            print(f"Ollama vision API error: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"Image processing error: {e}")
        return None, None

def validate_file_extension(filename):
    """Validate if the file extension is allowed"""
    if '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in app.config['ALLOWED_EXTENSIONS']

# Secured API endpoints (require authentication)
@api_ns.route('/car-identifier')
class CarIdentifier(Resource):
    @jwt_required()
    @api_ns.expect(car_image_model)
    def post(self):
        """Identify vehicle information from image using AI vision model"""
        try:
            # Check if image file is provided
            if 'image' not in request.files:
                return {'message': 'Image file is required'}, 400
            
            image_file = request.files['image']
            if image_file.filename == '':
                return {'message': 'No image file selected'}, 400
            
            # Validate file type
            if not validate_file_extension(image_file.filename):
                return {'message': f'Invalid file type. Supported formats: {", ".join(app.config["ALLOWED_EXTENSIONS"])}'}, 400
            
            # Process image with Ollama vision model
            processed_output, extracted_info = process_image_with_ollama(image_file)
            
            if not processed_output:
                # Log the request
                mongo.db.requests.insert_one({
                    'endpoint': '/api/public/car-identifier',
                    'service': 'car-identifier-service',
                    'status': 'error',
                    'error': 'Failed to process image with AI vision model',
                    'created_at': datetime.utcnow()
                })
                return {'message': 'Failed to process image with AI vision model'}, 500
            
            # Save to database
            result_doc = {
                'image_filename': image_file.filename,
                'processed_output': processed_output,
                'extracted_info': extracted_info,
                'endpoint': 'car-identifier',
                'service': 'car-identifier-service',
                'model': app.config['VISION_MODEL'],
                'extraction_fields': CONFIGURABLE_FIELDS,
                'created_at': datetime.utcnow()
            }
            
            result = mongo.db.extractions.insert_one(result_doc)
            
            # Log the request
            mongo.db.requests.insert_one({
                'endpoint': '/api/public/car-identifier',
                'service': 'car-identifier-service',
                'status': 'success',
                'extraction_id': str(result.inserted_id),
                'created_at': datetime.utcnow()
            })
            
            return {
                'id': str(result.inserted_id),
                'filename': image_file.filename,
                'model': app.config['VISION_MODEL'],
                'service': 'car-identifier-service',
                'extraction_fields': CONFIGURABLE_FIELDS,
                'processed_output': processed_output,
                'extracted_info': extracted_info
            }, 200
            
        except Exception as e:
            # Log the error
            mongo.db.requests.insert_one({
                'endpoint': '/api/public/car-identifier',
                'service': 'car-identifier-service',
                'status': 'error',
                'error': str(e),
                'created_at': datetime.utcnow()
            })
            return {'message': 'Internal server error'}, 500

@public_ns.route('/health')
class Health(Resource):
    def get(self):
        """Health check endpoint"""
        try:
            # Check database connection
            mongo.db.command('ping')
            db_status = 'healthy'
        except:
            db_status = 'unhealthy'
        
        try:
            # Check Ollama service
            response = requests.get(
                f"{app.config['OLLAMA_URL']}/api/version",
                timeout=5
            )
            ollama_status = 'healthy' if response.status_code == 200 else 'unhealthy'
        except:
            ollama_status = 'unhealthy'
        
        overall_status = 'healthy' if db_status == 'healthy' and ollama_status == 'healthy' else 'unhealthy'
        
        return {
            'status': overall_status,
            'service': 'car-identifier-service',
            'model': app.config['VISION_MODEL'],
            'extraction_fields': CONFIGURABLE_FIELDS,
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'database': db_status,
                'ollama': ollama_status
            }
        }, 200

if __name__ == '__main__':
    print("=== Starting Car Identifier Service ===")
    print(f"Vision Model: {app.config['VISION_MODEL']}")
    print(f"Extraction Fields: {CONFIGURABLE_FIELDS}")
    print(f"Model Timeout: {app.config['MODEL_TIMEOUT']}s")
    print(f"Allowed Extensions: {app.config['ALLOWED_EXTENSIONS']}")
    
    print("=== Flask app routes ===")
    for rule in app.url_map.iter_rules():
        print(f"Route: {rule.rule} -> {rule.endpoint}")
    
    app.run(host='0.0.0.0', port=8653, debug=False)
