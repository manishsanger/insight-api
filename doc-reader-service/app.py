import os
import json
import base64
import uuid
from datetime import datetime, timedelta
from functools import wraps
import logging
from pathlib import Path
import shutil
import fitz  # PyMuPDF for PDF processing
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
import io
import cv2
import numpy as np

from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields, Namespace
from flask_pymongo import PyMongo
from flask_cors import CORS
from dotenv import load_dotenv
import requests
import jwt
from werkzeug.utils import secure_filename
from bson import ObjectId
from bson.errors import InvalidId

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config['MONGO_URI'] = os.getenv('MONGODB_URI', 'mongodb://admin:Apple%40123@mongodb:27017/insight_db?authSource=admin')
app.config['OLLAMA_URL'] = os.getenv('OLLAMA_URL', 'http://host.docker.internal:11434')
app.config['VISION_MODEL'] = os.getenv('VISION_MODEL', 'gemma3:12b')
app.config['MODEL_TIMEOUT'] = int(os.getenv('MODEL_TIMEOUT', '180'))
app.config['PORT'] = int(os.getenv('PORT', '8654'))
app.config['CORS_ORIGINS'] = os.getenv('CORS_ORIGINS', 'http://localhost:8651,http://localhost:3000').split(',')
app.config['ALLOWED_EXTENSIONS'] = os.getenv('ALLOWED_EXTENSIONS', 'jpg,jpeg,png,gif,bmp,webp,pdf').split(',')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
app.config['STORAGE_PATH'] = os.getenv('STORAGE_PATH', '/app/data/uploads')
app.config['PERSISTENT_STORAGE'] = os.getenv('PERSISTENT_STORAGE', '/Users/manishsanger/docker-data/doc-reader-service')
app.config['EXTRACTION_FIELDS'] = os.getenv('EXTRACTION_FIELDS', 'document_type,name,date_of_birth,country,date_of_issue,expiry_date,address,gender,place_of_birth,issuing_authority,nationality,pin_code').split(',')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))

# Initialize extensions
mongo = PyMongo(app)
CORS(app, origins=app.config['CORS_ORIGINS'])

# Create upload directories
os.makedirs(app.config['STORAGE_PATH'], exist_ok=True)
os.makedirs(app.config['PERSISTENT_STORAGE'], exist_ok=True)

# Initialize Flask-RESTX
authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Type 'Bearer' followed by a space and JWT token"
    },
}

api = Api(
    app,
    version='1.0',
    title='Document Reader Service API',
    description='AI-powered document parsing and information extraction service',
    doc='/docs/',
    authorizations=authorizations,
    security='Bearer Auth'
)

# Namespaces
ns_public = Namespace('public', description='Public document reading operations')
ns_admin = Namespace('admin', description='Admin operations (authentication required)')
api.add_namespace(ns_public, path='/api/public')
api.add_namespace(ns_admin, path='/api/admin')

# Models for API documentation
doc_reader_model = api.model('DocumentReader', {
    'document_type': fields.String(description='Type of document (e.g., driving_license, passport)'),
    'name': fields.String(description='Full name'),
    'date_of_birth': fields.String(description='Date of birth'),
    'country': fields.String(description='Country'),
    'date_of_issue': fields.String(description='Date of issue'),
    'expiry_date': fields.String(description='Expiry date'),
    'address': fields.String(description='Address'),
    'gender': fields.String(description='Gender'),
    'place_of_birth': fields.String(description='Place of birth'),
    'issuing_authority': fields.String(description='Issuing authority'),
    'nationality': fields.String(description='Nationality'),
    'pin_code': fields.String(description='PIN code'),
    'person_image': fields.String(description='Base64 encoded person image extracted from document')
})

doc_reader_response = api.model('DocumentReaderResponse', {
    'id': fields.String(description='Document ID'),
    'filename': fields.String(description='Original filename'),
    'file_path': fields.String(description='Stored file path'),
    'model': fields.String(description='AI model used'),
    'service': fields.String(description='Service name'),
    'extraction_fields': fields.List(fields.String, description='Configured extraction fields'),
    'processed_output': fields.String(description='Raw AI model output'),
    'extracted_info': fields.Nested(doc_reader_model, description='Extracted information'),
    'extract_person_image': fields.Boolean(description='Whether person image extraction was requested'),
    'extract_text_info': fields.Boolean(description='Whether text information extraction was requested'),
    'timestamp': fields.String(description='Processing timestamp')
})

# Helper functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_file(file, filename):
    """Save file to both temporary and persistent storage"""
    secure_name = secure_filename(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{timestamp}_{secure_name}"
    
    # Save to temporary storage (for processing)
    temp_path = os.path.join(app.config['STORAGE_PATH'], unique_filename)
    file.save(temp_path)
    
    # Copy to persistent storage
    persistent_path = os.path.join(app.config['PERSISTENT_STORAGE'], unique_filename)
    shutil.copy2(temp_path, persistent_path)
    
    return temp_path, persistent_path, unique_filename

def convert_pdf_to_image(pdf_path):
    """Convert PDF to image for processing"""
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        if images:
            # Convert PIL image to base64
            img_byte_arr = io.BytesIO()
            images[0].save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            return base64.b64encode(img_byte_arr).decode('utf-8')
    except Exception as e:
        logger.error(f"Error converting PDF to image: {str(e)}")
    return None

def image_to_base64(image_path):
    """Convert image file to base64"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error converting image to base64: {str(e)}")
        return None

def extract_person_image_opencv(file_path, filename):
    """Extract person's image from document using OpenCV only"""
    try:
        # Determine if file is PDF or image
        file_extension = filename.lower().split('.')[-1]
        
        if file_extension == 'pdf':
            # Convert PDF to image first
            images = convert_from_path(file_path, first_page=1, last_page=1)
            if not images:
                return None
            # Convert PIL image to OpenCV format
            pil_image = images[0]
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        else:
            # Load image directly
            opencv_image = cv2.imread(file_path)
            if opencv_image is None:
                return None
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Use Haar cascade for face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) > 0:
            # Take the largest face (likely the main person photo)
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = largest_face
            
            # Add some padding around the face
            padding = 20
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(opencv_image.shape[1] - x, w + 2 * padding)
            h = min(opencv_image.shape[0] - y, h + 2 * padding)
            
            # Extract the person's image
            person_image = opencv_image[y:y+h, x:x+w]
            
            # Convert back to PIL Image
            person_pil = Image.fromarray(cv2.cvtColor(person_image, cv2.COLOR_BGR2RGB))
            
            # Convert to base64
            img_byte_arr = io.BytesIO()
            person_pil.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            return base64.b64encode(img_byte_arr).decode('utf-8')
        
        # No faces detected
        logger.info("No faces detected in document using OpenCV")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting person image with OpenCV: {str(e)}")
        return None

def extract_text_info_with_llm(file_path, filename):
    """Extract text information from document using LLM only"""
    try:
        # Determine if file is PDF or image
        file_extension = filename.lower().split('.')[-1]
        
        if file_extension == 'pdf':
            # Convert PDF to image
            image_base64 = convert_pdf_to_image(file_path)
        else:
            # Process as image
            image_base64 = image_to_base64(file_path)
        
        if not image_base64:
            raise Exception("Failed to convert file to processable format")
        
        # Prepare extraction fields prompt
        fields_prompt = ", ".join(app.config['EXTRACTION_FIELDS'])
        
        # Create improved prompt based on successful testing with direct Ollama calls
        prompt = f"Extract type of document (driving license/Passport), name, date of birth, country, date of issue, expiry date, address, gender, place of birth, issuing authority, nationality, pin code, person image from this document image. Use 'Not available' if any field cannot be determined from the image. Focus on extracting these specific fields: {fields_prompt}"

        # Make request to Ollama
        ollama_url = f"{app.config['OLLAMA_URL']}/api/generate"
        payload = {
            "model": app.config['VISION_MODEL'],
            "prompt": prompt,
            "images": [image_base64],
            "stream": False
        }
        
        response = requests.post(
            ollama_url, 
            json=payload, 
            timeout=app.config['MODEL_TIMEOUT']
        )
        response.raise_for_status()
        
        result = response.json()
        ai_output = result.get('response', '')
        
        # Parse the AI output to extract structured information
        extracted_info = parse_document_info(ai_output)
        
        # Add debugging to see the AI output and parsed result
        logger.info(f"AI Output length: {len(ai_output)} characters")
        logger.info(f"Parsed fields count: {len([k for k, v in extracted_info.items() if v])}")
        
        return ai_output, extracted_info
        
    except Exception as e:
        logger.error(f"Error extracting text info with LLM: {str(e)}")
        raise

def process_document_with_selective_extraction(file_path, filename, extract_person_image=True, extract_text_info=True):
    """Process document using separated OpenCV (person image) and LLM (text info) approaches with selective extraction"""
    try:
        processed_output = ""
        extracted_info = {}
        
        # Initialize all fields as empty first
        for field in app.config['EXTRACTION_FIELDS']:
            if field != 'person_image':
                extracted_info[field] = ""
        
        # Handle case when both extractions are disabled
        if not extract_person_image and not extract_text_info:
            extracted_info['person_image'] = ""
            processed_output = "Both extractions skipped"
            logger.info("Both extractions skipped - minimal processing")
            return processed_output, extracted_info
        
        # Step 1: Extract person image using OpenCV (if requested)
        if extract_person_image:
            logger.info("Extracting person image using OpenCV...")
            person_image_base64 = extract_person_image_opencv(file_path, filename)
            
            if person_image_base64:
                extracted_info['person_image'] = person_image_base64
                logger.info("Person image extraction completed")
            else:
                extracted_info['person_image'] = ""
                logger.info("No person image detected")
        else:
            extracted_info['person_image'] = ""
            logger.info("Person image extraction skipped")
        
        # Step 2: Extract text information using LLM (if requested)
        if extract_text_info:
            logger.info("Extracting text information using LLM...")
            ai_output, text_extracted_info = extract_text_info_with_llm(file_path, filename)
            processed_output = ai_output
            
            # Merge text extraction results
            for field in text_extracted_info:
                if field != 'person_image':  # Don't override person_image from OpenCV
                    extracted_info[field] = text_extracted_info[field]
            
            logger.info("Text information extraction completed")
        else:
            processed_output = "Text extraction skipped"
            logger.info("Text information extraction skipped")
        
        return processed_output, extracted_info
        
    except Exception as e:
        logger.error(f"Error processing document with selective extraction: {str(e)}")
        raise

def process_document_with_ollama(file_path, filename):
    """Process document using separated OpenCV (person image) and LLM (text info) approaches"""
    # Call the new selective extraction function with both extractions enabled
    return process_document_with_selective_extraction(file_path, filename, True, True)

def parse_document_info(ai_output):
    """Parse AI output to extract structured text information only"""
    extracted_info = {}
    
    # Initialize all fields as empty (excluding person_image as it's handled by OpenCV)
    for field in app.config['EXTRACTION_FIELDS']:
        if field != 'person_image':  # Skip person_image as OpenCV handles this
            extracted_info[field] = ""
    
    # Simple parsing logic - look for patterns in the AI output
    lines = ai_output.split('\n')
    
    field_mappings = {
        'document type': 'document_type',
        'document_type': 'document_type',
        'type of document': 'document_type',
        'name': 'name',
        'full name': 'name',
        'driver name': 'name',
        'date of birth': 'date_of_birth',
        'birth date': 'date_of_birth',
        'dob': 'date_of_birth',
        'country': 'country',
        'date of issue': 'date_of_issue',
        'issue date': 'date_of_issue',
        'issued': 'date_of_issue',
        'expiry date': 'expiry_date',
        'expiration date': 'expiry_date',
        'expires': 'expiry_date',
        'address': 'address',
        'gender': 'gender',
        'sex': 'gender',
        'place of birth': 'place_of_birth',
        'birth place': 'place_of_birth',
        'issuing authority': 'issuing_authority',
        'issued by': 'issuing_authority',
        'authority': 'issuing_authority',
        'nationality': 'nationality',
        'pin code': 'pin_code',
        'postal code': 'pin_code',
        'zip code': 'pin_code',
        'postcode': 'pin_code'
    }
    
    for line in lines:
        line = line.strip()
        if ':' in line:
            # Handle both bullet points and regular lines
            if line.startswith('*') or line.startswith('-'):
                line = line[1:].strip()
            
            # Remove markdown bold formatting if present
            if '**' in line:
                # Handle format like: **field:** value
                line = line.replace('**', '')
            
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            
            # Map the key to our standard field name and set value if meaningful
            if key in field_mappings:
                field_name = field_mappings[key]
                if field_name in extracted_info:
                    # Only set if value is meaningful (not "Not available", etc.)
                    if value and value.lower() not in ['not available', 'n/a', 'na', 'not provided', 'not visible', 'none', '[not mentioned]', '[not available]']:
                        extracted_info[field_name] = value
    
    return extracted_info

def token_required(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return {'message': 'Invalid token format'}, 401
        
        if not token:
            return {'message': 'Token is missing'}, 401
        
        try:
            # Decode the token
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            current_user_role = data.get('role')
            
            # Check if user has admin role
            if current_user_role != 'admin':
                return {'message': 'Admin privileges required'}, 403
                
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Token is invalid'}, 401
        
        return f(*args, **kwargs)
    
    return decorated

# Public API Routes
@ns_public.route('/health')
class Health(Resource):
    def get(self):
        """Health check endpoint"""
        try:
            # Check database connection
            db_status = "healthy"
            try:
                mongo.db.command('ping')
            except Exception:
                db_status = "unhealthy"
            
            # Check Ollama connection
            ollama_status = "healthy"
            try:
                response = requests.get(f"{app.config['OLLAMA_URL']}/api/tags", timeout=5)
                if response.status_code != 200:
                    ollama_status = "unhealthy"
            except Exception:
                ollama_status = "unhealthy"
            
            return {
                "status": "healthy",
                "service": "doc-reader-service",
                "model": app.config['VISION_MODEL'],
                "extraction_fields": app.config['EXTRACTION_FIELDS'],
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "database": db_status,
                    "ollama": ollama_status
                }
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}, 500

@ns_public.route('/doc-reader')
class DocumentReader(Resource):
    @api.expect(api.parser()
                .add_argument('file', location='files', type='file', required=True, help='Document file (image or PDF)')
                .add_argument('extract_person_image', location='form', type=str, required=False, default='true', help='Extract person image from document (true/false, default: true)')
                .add_argument('extract_text_info', location='form', type=str, required=False, default='true', help='Extract text information from document (true/false, default: true)'))
    @api.marshal_with(doc_reader_response)
    def post(self):
        """Process document and extract information with optional parameters"""
        try:
            # Check if file is present
            if 'file' not in request.files:
                return {'message': 'No file provided'}, 400
            
            file = request.files['file']
            if file.filename == '':
                return {'message': 'No file selected'}, 400
            
            # Get optional parameters with default values
            extract_person_image = request.form.get('extract_person_image', 'true').lower() == 'true'
            extract_text_info = request.form.get('extract_text_info', 'true').lower() == 'true'
            
            # Validate that at least one extraction type is requested
            if not extract_person_image and not extract_text_info:
                return {'message': 'At least one extraction type must be enabled (extract_person_image or extract_text_info)'}, 400
            
            # Validate file type
            if not allowed_file(file.filename):
                return {
                    'message': f'Invalid file type. Supported formats: {", ".join(app.config["ALLOWED_EXTENSIONS"])}'
                }, 400
            
            # Save file
            temp_path, persistent_path, unique_filename = save_file(file, file.filename)
            
            try:
                # Process document with selective extraction
                processed_output, extracted_info = process_document_with_selective_extraction(
                    temp_path, file.filename, extract_person_image, extract_text_info
                )
                
                # Save to database
                doc_data = {
                    'filename': file.filename,
                    'stored_filename': unique_filename,
                    'file_path': persistent_path,
                    'model': app.config['VISION_MODEL'],
                    'service': 'doc-reader-service',
                    'extraction_fields': app.config['EXTRACTION_FIELDS'],
                    'processed_output': processed_output,
                    'extracted_info': extracted_info,
                    'extract_person_image': extract_person_image,
                    'extract_text_info': extract_text_info,
                    'timestamp': datetime.now(),
                    'file_size': os.path.getsize(persistent_path)
                }
                
                result = mongo.db.doc_reader.insert_one(doc_data)
                
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                return {
                    'id': str(result.inserted_id),
                    'filename': file.filename,
                    'file_path': persistent_path,
                    'model': app.config['VISION_MODEL'],
                    'service': 'doc-reader-service',
                    'extraction_fields': app.config['EXTRACTION_FIELDS'],
                    'processed_output': processed_output,
                    'extracted_info': extracted_info,
                    'extract_person_image': extract_person_image,
                    'extract_text_info': extract_text_info,
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                # Clean up files on error
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                if os.path.exists(persistent_path):
                    os.remove(persistent_path)
                raise e
                
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return {'message': f'Error processing document: {str(e)}'}, 500

# Admin API Routes
@ns_admin.route('/doc-reader')
class AdminDocumentList(Resource):
    @api.doc(security='Bearer Auth')
    @token_required
    def get(self):
        """Get paginated list of processed documents (Admin only)"""
        try:
            # Get pagination parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            
            # Calculate skip value
            skip = (page - 1) * per_page
            
            # Get total count
            total = mongo.db.doc_reader.count_documents({})
            
            # Get documents with pagination
            documents = list(mongo.db.doc_reader.find({})
                           .sort('timestamp', -1)
                           .skip(skip)
                           .limit(per_page))
            
            # Convert ObjectId to string
            for doc in documents:
                doc['_id'] = str(doc['_id'])
                if 'timestamp' in doc:
                    doc['timestamp'] = doc['timestamp'].isoformat()
            
            return {
                'data': documents,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting document list: {str(e)}")
            return {'message': f'Error getting document list: {str(e)}'}, 500

@ns_admin.route('/doc-reader/<string:doc_id>')
class AdminDocumentDetail(Resource):
    @api.doc(security='Bearer Auth')
    @token_required
    def get(self, doc_id):
        """Get individual document details (Admin only)"""
        try:
            # Validate ObjectId
            try:
                object_id = ObjectId(doc_id)
            except InvalidId:
                return {'message': 'Invalid document ID'}, 400
            
            # Get document from database
            document = mongo.db.doc_reader.find_one({'_id': object_id})
            
            if not document:
                return {'message': 'Document not found'}, 404
            
            # Convert ObjectId to string and format timestamp
            document['_id'] = str(document['_id'])
            if 'timestamp' in document:
                document['timestamp'] = document['timestamp'].isoformat()
            
            return {'data': document}
            
        except Exception as e:
            logger.error(f"Error getting document details: {str(e)}")
            return {'message': f'Error getting document details: {str(e)}'}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=False)
