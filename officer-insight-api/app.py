import os
import bcrypt
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, current_app, make_response
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
from flask_restx import Api, Resource, fields, Namespace
from werkzeug.utils import secure_filename
import re
import json
from bson import ObjectId

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

# Configuration
app.config['JWT_SECRET_KEY'] = 'insight-api-jwt-secret-key-2024'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['MONGO_URI'] = os.getenv('MONGODB_URI', 'mongodb://admin:Apple%40123@mongodb:27017/insight_db?authSource=admin')
app.config['SPEECH2TEXT_API_URL'] = os.getenv('SPEECH2TEXT_API_URL', 'http://speech2text-service:8652')
app.config['SPEECH2TEXT_API_TOKEN'] = os.getenv('SPEECH2TEXT_API_TOKEN', 'insight_speech_token_2024')
app.config['OLLAMA_URL'] = os.getenv('OLLAMA_URL', 'http://host.docker.internal:11434')

# Initialize extensions
mongo = PyMongo(app)
jwt = JWTManager(app)
CORS(app, origins=['http://localhost:8651', 'http://localhost:3000'], supports_credentials=True)

# API Documentation
api = Api(app, version='1.0', title='Officer Insight API',
          description='API for processing audio files and text messages',
          doc='/docs/', prefix='/api')

# Override Flask-RESTX JSON output to use our custom JSON serialization
def custom_output_json(data, code, headers=None):
    """Custom JSON output that handles MongoDB ObjectId and datetime"""
    import json
    
    print(f"=== Custom JSON output called ===")
    print(f"Data type: {type(data)}")
    print(f"Data: {data}")
    
    try:
        # Serialize the data first to handle ObjectId and datetime
        serialized_data = serialize_mongo_doc(data)
        
        # Use our custom encoder for JSON serialization
        dumped = json.dumps(serialized_data, cls=CustomJSONEncoder, ensure_ascii=False, indent=None, separators=(',', ':')) + '\n'
        
        resp = current_app.response_class(dumped, status=code, mimetype='application/json')
        if headers:
            resp.headers.extend(headers)
        return resp
    except Exception as e:
        print(f"Error in custom_output_json: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to default JSON handling
        fallback = json.dumps({'error': 'Serialization error'}) + '\n'
        return current_app.response_class(fallback, status=500, mimetype='application/json')

# Override the default JSON representation
print("=== Setting custom JSON representation ===")
api.representations['application/json'] = custom_output_json
print(f"Current representations: {api.representations}")

# Configure Flask app to use our custom JSON encoder for responses
app.json_encoder = CustomJSONEncoder

# Namespaces
auth_ns = Namespace('auth', description='Authentication operations')
admin_ns = Namespace('admin', description='Admin operations')
public_ns = Namespace('public', description='Public API operations')

api.add_namespace(auth_ns, path='/auth')
api.add_namespace(admin_ns, path='/admin')
api.add_namespace(public_ns, path='/public')

# Models for Swagger documentation
login_model = api.model('Login', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

parameter_model = api.model('Parameter', {
    'name': fields.String(required=True, description='Parameter name'),
    'description': fields.String(description='Parameter description'),
    'active': fields.Boolean(default=True, description='Parameter status')
})

message_model = api.model('Message', {
    'message': fields.String(description='Text message'),
    'audio_message': fields.Raw(description='Audio file')
})

car_image_model = api.model('CarImage', {
    'image': fields.Raw(required=True, description='Vehicle image file (JPG, PNG, etc.)')
})

# Default extraction parameters
DEFAULT_PARAMETERS = [
    {'name': 'person_name', 'description': 'Name of the person involved', 'active': True},
    {'name': 'vehicle_number', 'description': 'Vehicle license plate number', 'active': True},
    {'name': 'vehicle_make', 'description': 'Vehicle manufacturer/brand', 'active': True},
    {'name': 'vehicle_color', 'description': 'Color of the vehicle', 'active': True},
    {'name': 'vehicle_model', 'description': 'Model of the vehicle', 'active': True},
    {'name': 'location', 'description': 'Location where incident occurred', 'active': True},
    {'name': 'event_crime_violation', 'description': 'Type of event, crime or violation', 'active': True}
]

def init_database():
    """Initialize database with default admin user and parameters"""
    try:
        # Create default admin user
        admin_exists = mongo.db.users.find_one({'username': 'admin'})
        if not admin_exists:
            hashed_password = bcrypt.hashpw('Apple@123'.encode('utf-8'), bcrypt.gensalt())
            mongo.db.users.insert_one({
                'username': 'admin',
                'password': hashed_password,
                'role': 'admin',
                'created_at': datetime.utcnow()
            })
            print("Default admin user created")

        # Create default parameters
        params_count = mongo.db.parameters.count_documents({})
        if params_count == 0:
            mongo.db.parameters.insert_many(DEFAULT_PARAMETERS)
            print("Default parameters created")

    except Exception as e:
        print(f"Database initialization error: {e}")

def extract_information_with_ollama(text, parameters):
    """Extract information using Ollama AI"""
    try:
        param_names = [p['name'] for p in parameters if p['active']]
        
        # Enhanced prompt for better extraction
        prompt = f"""
You are an expert at extracting structured information from police reports and incident descriptions.

Parse the following text and extract information in this exact format:

Input text: {text}

Please extract and format the information as follows (only include fields that are mentioned in the text):
- Offence Category: [type of offence]
- Driver Name: [full name] 
- Date of Birth: [DD/MM/YYYY format]
- Gender: [Male/Female/Other]
- Address: [full address]
- Location of Offence: [location where offence occurred]
- Offence Occurred at: [time and date]
- Offence: [specific offence description]
- Vehicle Registration: [registration number]
- Vehicle Make: [car manufacturer/brand only, e.g., BMW, Toyota, Ford]
- Vehicle Color: [vehicle color only, e.g., Blue, Red, Black]
- Vehicle Model: [vehicle model/series only, e.g., 420, Camry, Focus]

IMPORTANT: For vehicle information, extract Vehicle Make, Vehicle Color, and Vehicle Model as separate fields.
- Vehicle Make should only contain the manufacturer/brand name
- Vehicle Color should only contain the color
- Vehicle Model should only contain the model/series number or name

Available parameters to extract: {', '.join(param_names)}

Format the response exactly as shown above with each field on a new line.
If information is not available, omit that field entirely.
Do not include any additional explanations or text.
"""

        response = requests.post(
            f"{app.config['OLLAMA_URL']}/api/generate",
            json={
                "model": "llama3.2:latest",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            processed_text = result.get('response', '').strip()
            
            # Parse the structured response into a dictionary
            extracted_data = {}
            lines = processed_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if ':' in line and line.startswith('- '):
                    key, value = line[2:].split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if value and value.lower() not in ['[not mentioned]', '[not available]', 'n/a', 'none']:
                        extracted_data[key.lower().replace(' ', '_')] = value
            
            return extracted_data
        else:
            print(f"Ollama API error: {response.status_code}")
            return extract_information_with_regex(text, parameters)
            
    except Exception as e:
        print(f"Ollama extraction error: {e}")
        return extract_information_with_regex(text, parameters)

def extract_information_with_regex(text, parameters):
    """Fallback extraction using regex patterns"""
    extracted = {}
    text_lower = text.lower()
    
    for param in parameters:
        if not param['active']:
            continue
            
        param_name = param['name']
        value = None
        
        if param_name == 'person_name':
            # Simple pattern for names
            name_pattern = r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b'
            match = re.search(name_pattern, text)
            value = match.group(1) if match else None
            
        elif param_name == 'vehicle_number':
            # Pattern for license plates
            plate_pattern = r'\b[A-Z0-9]{2,8}\b'
            match = re.search(plate_pattern, text.upper())
            value = match.group(0) if match else None
            
        elif param_name == 'vehicle_color':
            colors = ['red', 'blue', 'green', 'black', 'white', 'silver', 'gray', 'yellow', 'orange']
            for color in colors:
                if color in text_lower:
                    value = color.title()
                    break
                    
        elif param_name == 'vehicle_make':
            makes = ['toyota', 'honda', 'ford', 'bmw', 'mercedes', 'audi', 'nissan', 'hyundai', 'volkswagen', 'subaru']
            for make in makes:
                if make in text_lower:
                    value = make.upper() if make == 'bmw' else make.title()
                    break
                    
        elif param_name == 'vehicle_model':
            # Extract model numbers/names after make
            model_pattern = r'\b(bmw|toyota|honda|ford|mercedes|audi|nissan|hyundai)\s+([a-z0-9]+)\b'
            match = re.search(model_pattern, text_lower)
            if match:
                value = match.group(2).upper() if match.group(2).isdigit() else match.group(2).title()
                    
        elif param_name in ['car_color', 'car_model']:  # Legacy parameter names
            # Handle legacy parameter names for backward compatibility
            if param_name == 'car_color':
                colors = ['red', 'blue', 'green', 'black', 'white', 'silver', 'gray', 'yellow', 'orange']
                for color in colors:
                    if color in text_lower:
                        value = color.title()
                        break
            elif param_name == 'car_model':
                makes = ['toyota', 'honda', 'ford', 'bmw', 'mercedes', 'audi', 'nissan', 'hyundai']
                for make in makes:
                    if make in text_lower:
                        value = make.title()
                        break
                    
        elif param_name == 'location':
            # Simple location extraction
            location_keywords = ['at', 'on', 'near', 'in front of', 'behind']
            for keyword in location_keywords:
                if keyword in text_lower:
                    parts = text_lower.split(keyword)
                    if len(parts) > 1:
                        location_part = parts[1].split('.')[0].split(',')[0].strip()
                        value = location_part[:50] if location_part else None
                        break
                        
        elif param_name == 'event_crime_violation':
            events = ['theft', 'robbery', 'assault', 'speeding', 'parking violation', 'accident', 'vandalism']
            for event in events:
                if event in text_lower:
                    value = event
                    break
        
        extracted[param_name] = value
    
    return extracted

def convert_audio_to_text(audio_file):
    """Convert audio file to text using Speech2Text service with Ollama"""
    try:
        files = {'audio_file': audio_file}
        headers = {'Authorization': f'Bearer {app.config["SPEECH2TEXT_API_TOKEN"]}'}
        
        response = requests.post(
            f"{app.config['SPEECH2TEXT_API_URL']}/api/convert",
            files=files,
            headers=headers,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            # The new service returns both text and processed_output
            return result.get('text', ''), result.get('processed_output', '')
        else:
            print(f"Audio conversion API error: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"Audio conversion error: {e}")
        return None, None

def process_text_with_ollama_service(text):
    """Process text using the speech2text service with Ollama"""
    try:
        headers = {
            'Authorization': f'Bearer {app.config["SPEECH2TEXT_API_TOKEN"]}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{app.config['SPEECH2TEXT_API_URL']}/api/process-text",
            json={'text': text},
            headers=headers,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('processed_output', '')
        else:
            print(f"Text processing API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Text processing error: {e}")
        return None

def process_image_with_ollama(image_file):
    """Process vehicle image using Ollama vision model for car identification"""
    try:
        import base64
        import io
        from PIL import Image
        
        # Read and process the image
        image_data = image_file.read()
        image_file.seek(0)  # Reset file pointer
        
        # Convert image to base64 for Ollama vision model
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Use Ollama vision model (llama3.2-vision:latest or llava)
        prompt = """
Analyze this vehicle image and extract the following information in this exact format:

- Vehicle Registration: [license plate number if visible]
- Vehicle Make: [car manufacturer/brand, e.g., BMW, Toyota, Ford]
- Vehicle Color: [primary vehicle color, e.g., Blue, Red, Black]
- Vehicle Model: [car model/series, e.g., 320i, Camry, Focus]

Only include fields that you can clearly identify from the image. If information is not visible or unclear, omit that field.
Focus on identifying the vehicle make, color, and model even if the license plate is not clearly visible.
"""

        response = requests.post(
            f"{app.config['OLLAMA_URL']}/api/generate",
            json={
                "model": "llava:13b-v1.5-fp16",  # Use LLaVA 13B vision model with FP16 precision
                "prompt": prompt,
                "images": [image_base64],
                "stream": False
            },
            timeout=180  # Longer timeout for larger model processing
        )
        
        if response.status_code == 200:
            result = response.json()
            processed_text = result.get('response', '').strip()
            
            # Parse the structured response into a dictionary
            extracted_data = {}
            lines = processed_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if ':' in line and line.startswith('- '):
                    key, value = line[2:].split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if value and value.lower() not in ['[not visible]', '[not clear]', '[unknown]', 'n/a', 'none']:
                        extracted_data[key.lower().replace(' ', '_')] = value
            
            return processed_text, extracted_data
        else:
            print(f"Ollama vision API error: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"Image processing error: {e}")
        return None, None

def serialize_mongo_doc(doc):
    """Convert MongoDB document to JSON serializable format"""
    if isinstance(doc, list):
        return [serialize_mongo_doc(item) for item in doc]
    elif isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, (dict, list)):
                result[key] = serialize_mongo_doc(value)
            else:
                result[key] = value
        return result
    else:
        return doc

# Authentication endpoints
@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        """Authenticate user and return JWT token"""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return {'message': 'Username and password required'}, 400
        
        user = mongo.db.users.find_one({'username': username})
        
        if user:
            stored_password = user['password']
            # Ensure stored password is bytes for bcrypt comparison
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                access_token = create_access_token(
                    identity=str(user['_id']),
                    additional_claims={'role': user['role'], 'username': username}
                )
                return {'access_token': access_token, 'role': user['role']}, 200
        
        return {'message': 'Invalid credentials'}, 401

# Admin endpoints
@admin_ns.route('/parameters')
class ParameterList(Resource):
    @jwt_required()
    def get(self):
        """Get all extraction parameters"""
        try:
            parameters = list(mongo.db.parameters.find())
            
            # Serialize parameters to handle ObjectId and datetime
            serialized_parameters = []
            for param in parameters:
                serialized_param = serialize_mongo_doc(param)
                # Add 'id' field for React Admin compatibility
                serialized_param['id'] = serialized_param['_id']
                serialized_parameters.append(serialized_param)
            
            return {'data': serialized_parameters}, 200
        except Exception as e:
            print(f"Error in parameters endpoint: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}, 500
    
    @admin_ns.expect(parameter_model)
    @jwt_required()
    def post(self):
        """Create new extraction parameter"""
        try:
            data = request.get_json()
            
            # Check if parameter already exists
            existing = mongo.db.parameters.find_one({'name': data['name']})
            if existing:
                return {'message': 'Parameter already exists'}, 400
            
            creation_time = datetime.utcnow()
            parameter = {
                'name': data['name'],
                'description': data.get('description', ''),
                'active': data.get('active', True),
                'created_at': creation_time
            }
            
            result = mongo.db.parameters.insert_one(parameter)
            
            # Return serialized response
            serialized_parameter = serialize_mongo_doc({
                '_id': result.inserted_id,
                'name': parameter['name'],
                'description': parameter['description'],
                'active': parameter['active'],
                'created_at': parameter['created_at']
            })
            
            return {'data': serialized_parameter}, 201
        except Exception as e:
            print(f"Error in POST parameters endpoint: {e}")
            import traceback
            traceback.print_exc()
            return {'message': 'Internal server error'}, 500

@admin_ns.route('/parameters/<parameter_id>')
class ParameterDetail(Resource):
    @admin_ns.expect(parameter_model)
    @jwt_required()
    def put(self, parameter_id):
        """Update extraction parameter"""
        data = request.get_json()
        
        result = mongo.db.parameters.update_one(
            {'_id': ObjectId(parameter_id)},
            {'$set': {
                'name': data['name'],
                'description': data.get('description', ''),
                'active': data.get('active', True),
                'updated_at': datetime.utcnow()
            }}
        )
        
        if result.matched_count:
            return {'message': 'Parameter updated successfully'}, 200
        
        return {'message': 'Parameter not found'}, 404
    
    @jwt_required()
    def delete(self, parameter_id):
        """Delete extraction parameter"""
        result = mongo.db.parameters.delete_one({'_id': ObjectId(parameter_id)})
        
        if result.deleted_count:
            return {'message': 'Parameter deleted successfully'}, 200
        
        return {'message': 'Parameter not found'}, 404

@admin_ns.route('/requests')
class RequestList(Resource):
    @jwt_required()
    def get(self):
        """Get all API requests with pagination"""
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            query = {}
            if start_date and end_date:
                query['created_at'] = {
                    '$gte': datetime.fromisoformat(start_date),
                    '$lte': datetime.fromisoformat(end_date)
                }
            
            total = mongo.db.requests.count_documents(query)
            requests_data = list(mongo.db.requests.find(query)
                               .sort('created_at', -1)
                               .skip((page - 1) * per_page)
                               .limit(per_page))
            
            # Serialize requests to avoid ObjectId issues
            serialized_requests = []
            for req in requests_data:
                serialized_req = serialize_mongo_doc(req)
                # Add 'id' field for React Admin compatibility
                serialized_req['id'] = serialized_req['_id']
                serialized_requests.append(serialized_req)
            
            result = {
                'data': serialized_requests,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
            return result, 200
        except Exception as e:
            print(f"Error in requests endpoint: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}, 500

@admin_ns.route('/users')
class UserList(Resource):
    @jwt_required()
    def get(self):
        """Get all users"""
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            
            total = mongo.db.users.count_documents({})
            users = list(mongo.db.users.find({}, {'password': 0})  # Exclude password field
                       .sort('created_at', -1)
                       .skip((page - 1) * per_page)
                       .limit(per_page))
            
            # Serialize users to avoid ObjectId issues
            serialized_users = []
            for user in users:
                serialized_user = serialize_mongo_doc(user)
                # Add 'id' field for React Admin compatibility
                serialized_user['id'] = serialized_user['_id']
                serialized_users.append(serialized_user)
            
            result = {
                'data': serialized_users,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
            return result, 200
        except Exception as e:
            print(f"Error in users endpoint: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}, 500
    
    @jwt_required()
    def post(self):
        """Create new user"""
        try:
            data = request.get_json()
            
            # Check if user already exists
            existing = mongo.db.users.find_one({'username': data['username']})
            if existing:
                return {'message': 'User already exists'}, 400
            
            # Hash password
            hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
            
            user = {
                'username': data['username'],
                'password': hashed_password,
                'role': data.get('role', 'user'),
                'created_at': datetime.utcnow()
            }
            
            result = mongo.db.users.insert_one(user)
            
            # Create serialized response (exclude password)
            user_response = {
                '_id': result.inserted_id,
                'username': user['username'],
                'role': user['role'],
                'created_at': user['created_at']
            }
            
            serialized_user = serialize_mongo_doc(user_response)
            serialized_user['id'] = serialized_user['_id']
            
            return {'data': serialized_user}, 201
        except Exception as e:
            print(f"Error in POST users endpoint: {e}")
            import traceback
            traceback.print_exc()
            return {'message': 'Internal server error'}, 500

@admin_ns.route('/users/<user_id>')
class UserDetail(Resource):
    @jwt_required()
    def put(self, user_id):
        """Update user"""
        data = request.get_json()
        
        update_data = {
            'username': data['username'],
            'role': data.get('role', 'user'),
            'updated_at': datetime.utcnow()
        }
        
        # Only update password if provided
        if 'password' in data and data['password']:
            hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
            update_data['password'] = hashed_password
        
        result = mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        
        if result.matched_count:
            return {'message': 'User updated successfully'}, 200
        
        return {'message': 'User not found'}, 404
    
    @jwt_required()
    def delete(self, user_id):
        """Delete user"""
        result = mongo.db.users.delete_one({'_id': ObjectId(user_id)})
        
        if result.deleted_count:
            return {'message': 'User deleted successfully'}, 200
        
        return {'message': 'User not found'}, 404

@admin_ns.route('/dashboard')
class Dashboard(Resource):
    @jwt_required()
    def get(self):
        """Get dashboard statistics"""
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = {}
        if start_date and end_date:
            query['created_at'] = {
                '$gte': datetime.fromisoformat(start_date),
                '$lte': datetime.fromisoformat(end_date)
            }
        
        total_requests = mongo.db.requests.count_documents(query)
        successful_requests = mongo.db.requests.count_documents({**query, 'status': 'success'})
        error_requests = mongo.db.requests.count_documents({**query, 'status': 'error'})
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'error_requests': error_requests,
            'success_rate': (successful_requests / total_requests * 100) if total_requests > 0 else 0
        }, 200

# Public API endpoints
@public_ns.route('/parse-message')
class ParseMessage(Resource):
    @public_ns.expect(message_model)
    def post(self):
        """Parse text message or audio file and extract information"""
        try:
            text_message = request.form.get('message')
            audio_file = request.files.get('audio_message')
            
            if not text_message and not audio_file:
                return {'message': 'Either text message or audio file is required'}, 400
            
            final_text = text_message
            processed_output = None
            
            # Convert audio to text if provided
            if audio_file:
                converted_text, audio_processed_output = convert_audio_to_text(audio_file)
                if converted_text:
                    final_text = converted_text
                    processed_output = audio_processed_output
                else:
                    # Log the request
                    mongo.db.requests.insert_one({
                        'endpoint': '/api/parse-message',
                        'status': 'error',
                        'error': 'Failed to convert audio to text',
                        'created_at': datetime.utcnow()
                    })
                    return {'message': 'Failed to convert audio to text'}, 500
            
            if not final_text:
                return {'message': 'No text to process'}, 400
            
            # If we don't have processed output from audio, process the text
            if not processed_output:
                processed_output = process_text_with_ollama_service(final_text)
                if not processed_output:
                    # Fallback to local Ollama processing
                    parameters = list(mongo.db.parameters.find({'active': True}))
                    extracted_info = extract_information_with_ollama(final_text, parameters)
                    processed_output = self._format_extracted_info(extracted_info)
            
            # Parse the processed output into structured data
            extracted_info = self._parse_processed_output(processed_output)
            
            # Save to database
            result_doc = {
                'original_text': final_text,
                'processed_output': processed_output,
                'extracted_info': extracted_info,
                'has_audio': audio_file is not None,
                'created_at': datetime.utcnow()
            }
            
            result = mongo.db.extractions.insert_one(result_doc)
            
            # Log the request
            mongo.db.requests.insert_one({
                'endpoint': '/api/parse-message',
                'status': 'success',
                'extraction_id': str(result.inserted_id),
                'created_at': datetime.utcnow()
            })
            
            return {
                'id': str(result.inserted_id),
                'text': final_text,
                'processed_output': processed_output,
                'extracted_info': extracted_info
            }, 200
            
        except Exception as e:
            # Log the error
            mongo.db.requests.insert_one({
                'endpoint': '/api/parse-message',
                'status': 'error',
                'error': str(e),
                'created_at': datetime.utcnow()
            })
            return {'message': 'Internal server error'}, 500
    
    def _parse_processed_output(self, processed_output):
        """Parse the structured output into a dictionary"""
        if not processed_output:
            return {}
        
        extracted_info = {}
        lines = processed_output.split('\n')
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                # Handle both "- Field: Value" and "Field: Value" formats
                if line.startswith('- '):
                    line = line[2:]
                
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    if value and value.lower() not in ['[not mentioned]', '[not available]', 'n/a', 'none', '']:
                        extracted_info[key.lower().replace(' ', '_')] = value
        
        return extracted_info
    
    def _format_extracted_info(self, extracted_info):
        """Format extracted info dictionary into structured text"""
        if not extracted_info:
            return ""
        
        formatted_lines = []
        for key, value in extracted_info.items():
            if value:
                formatted_key = key.replace('_', ' ').title()
                formatted_lines.append(f"{formatted_key}: {value}")
        
        return '\n'.join(formatted_lines)

@public_ns.route('/car-identifier')
class CarIdentifier(Resource):
    @public_ns.expect(car_image_model)
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
            allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
            file_extension = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else ''
            
            if file_extension not in allowed_extensions:
                return {'message': f'Invalid file type. Supported formats: {", ".join(allowed_extensions)}'}, 400
            
            # Process image with Ollama vision model
            processed_output, extracted_info = process_image_with_ollama(image_file)
            
            if not processed_output:
                # Log the request
                mongo.db.requests.insert_one({
                    'endpoint': '/api/public/car-identifier',
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
                'created_at': datetime.utcnow()
            }
            
            result = mongo.db.extractions.insert_one(result_doc)
            
            # Log the request
            mongo.db.requests.insert_one({
                'endpoint': '/api/public/car-identifier',
                'status': 'success',
                'extraction_id': str(result.inserted_id),
                'created_at': datetime.utcnow()
            })
            
            return {
                'id': str(result.inserted_id),
                'filename': image_file.filename,
                'processed_output': processed_output,
                'extracted_info': extracted_info
            }, 200
            
        except Exception as e:
            # Log the error
            mongo.db.requests.insert_one({
                'endpoint': '/api/public/car-identifier',
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
            # Check Speech2Text service
            response = requests.get(
                f"{app.config['SPEECH2TEXT_API_URL']}/api/health",
                timeout=5
            )
            speech_status = 'healthy' if response.status_code == 200 else 'unhealthy'
        except:
            speech_status = 'unhealthy'
        
        overall_status = 'healthy' if db_status == 'healthy' and speech_status == 'healthy' else 'unhealthy'
        
        return {
            'status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'database': db_status,
                'speech2text': speech_status
            }
        }, 200

if __name__ == '__main__':
    with app.app_context():
        init_database()
    
    app.run(host='0.0.0.0', port=8650, debug=False)
