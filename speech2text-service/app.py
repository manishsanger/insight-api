import os
import uuid
import whisper
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from werkzeug.utils import secure_filename
import tempfile
import shutil

app = Flask(__name__)

# Configuration
app.config['API_TOKEN'] = os.getenv('API_TOKEN', 'insight_speech_token_2024')
app.config['WHISPER_MODEL'] = os.getenv('WHISPER_MODEL', 'turbo')
app.config['AUDIO_UPLOAD_FOLDER'] = '/app/audio_files'
app.config['TEMP_FOLDER'] = '/app/temp'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Initialize extensions
CORS(app)

# API Documentation
api = Api(app, version='1.0', title='Speech2Text Service API',
          description='Audio to text conversion service using OpenAI Whisper',
          doc='/docs/')

# Load Whisper model
print(f"Loading Whisper model: {app.config['WHISPER_MODEL']}")
model = whisper.load_model(app.config['WHISPER_MODEL'])
print("Whisper model loaded successfully")

# Allowed audio file extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'webm', 'flac'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def verify_token():
    """Verify API token from request headers"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False
    
    try:
        token_type, token = auth_header.split(' ', 1)
        if token_type.lower() != 'bearer':
            return False
        return token == app.config['API_TOKEN']
    except ValueError:
        return False

# Models for Swagger documentation
convert_model = api.model('Convert', {
    'audio_file': fields.Raw(required=True, description='Audio file to convert')
})

error_model = api.model('Error', {
    'message': fields.String(description='Error message')
})

success_model = api.model('Success', {
    'text': fields.String(description='Converted text'),
    'file_id': fields.String(description='Stored file ID'),
    'timestamp': fields.String(description='Processing timestamp')
})

@api.route('/api/convert')
class ConvertAudio(Resource):
    @api.expect(convert_model)
    @api.marshal_with(success_model, code=200)
    @api.marshal_with(error_model, code=400)
    @api.marshal_with(error_model, code=401)
    @api.marshal_with(error_model, code=500)
    def post(self):
        """Convert audio file to text using Whisper"""
        # Verify authentication
        if not verify_token():
            return {'message': 'Invalid or missing API token'}, 401
        
        # Check if file is provided
        if 'audio_file' not in request.files:
            return {'message': 'No audio file provided'}, 400
        
        file = request.files['audio_file']
        
        if file.filename == '':
            return {'message': 'No file selected'}, 400
        
        if not allowed_file(file.filename):
            return {'message': f'File type not allowed. Supported types: {", ".join(ALLOWED_EXTENSIONS)}'}, 400
        
        try:
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            
            # Create temporary file for processing
            temp_file_path = os.path.join(app.config['TEMP_FOLDER'], f"{file_id}.{file_extension}")
            file.save(temp_file_path)
            
            # Process audio with Whisper
            print(f"Processing audio file: {filename}")
            result = model.transcribe(temp_file_path)
            text = result["text"].strip()
            
            # Save audio file permanently
            permanent_file_path = os.path.join(app.config['AUDIO_UPLOAD_FOLDER'], f"{file_id}_{filename}")
            shutil.move(temp_file_path, permanent_file_path)
            
            # Log the conversion
            log_entry = {
                'file_id': file_id,
                'original_filename': filename,
                'text_length': len(text),
                'timestamp': datetime.utcnow().isoformat(),
                'file_path': permanent_file_path
            }
            
            print(f"Audio conversion completed: {log_entry}")
            
            return {
                'text': text,
                'file_id': file_id,
                'timestamp': datetime.utcnow().isoformat()
            }, 200
            
        except Exception as e:
            # Clean up temporary file if it exists
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            print(f"Error processing audio: {str(e)}")
            return {'message': f'Error processing audio file: {str(e)}'}, 500

@api.route('/api/health')
class Health(Resource):
    def get(self):
        """Health check endpoint"""
        try:
            # Check if model is loaded
            model_status = 'loaded' if model is not None else 'not_loaded'
            
            # Check disk space for audio storage
            disk_usage = shutil.disk_usage(app.config['AUDIO_UPLOAD_FOLDER'])
            free_space_gb = disk_usage.free / (1024**3)
            
            # Check if directories exist
            audio_dir_exists = os.path.exists(app.config['AUDIO_UPLOAD_FOLDER'])
            temp_dir_exists = os.path.exists(app.config['TEMP_FOLDER'])
            
            overall_status = 'healthy' if (
                model_status == 'loaded' and 
                free_space_gb > 1.0 and  # At least 1GB free
                audio_dir_exists and 
                temp_dir_exists
            ) else 'unhealthy'
            
            return {
                'status': overall_status,
                'timestamp': datetime.utcnow().isoformat(),
                'model': {
                    'name': app.config['WHISPER_MODEL'],
                    'status': model_status
                },
                'storage': {
                    'audio_directory': audio_dir_exists,
                    'temp_directory': temp_dir_exists,
                    'free_space_gb': round(free_space_gb, 2)
                }
            }, 200
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }, 500

@api.route('/api/files')
class FileList(Resource):
    def get(self):
        """List stored audio files (for debugging/monitoring)"""
        # Verify authentication
        if not verify_token():
            return {'message': 'Invalid or missing API token'}, 401
        
        try:
            files = []
            if os.path.exists(app.config['AUDIO_UPLOAD_FOLDER']):
                for filename in os.listdir(app.config['AUDIO_UPLOAD_FOLDER']):
                    file_path = os.path.join(app.config['AUDIO_UPLOAD_FOLDER'], filename)
                    if os.path.isfile(file_path):
                        stat = os.stat(file_path)
                        files.append({
                            'filename': filename,
                            'size_bytes': stat.st_size,
                            'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat()
                        })
            
            return {
                'files': sorted(files, key=lambda x: x['created_at'], reverse=True),
                'total_files': len(files)
            }, 200
            
        except Exception as e:
            return {'message': f'Error listing files: {str(e)}'}, 500

# Create necessary directories on startup
def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        app.config['AUDIO_UPLOAD_FOLDER'],
        app.config['TEMP_FOLDER']
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")

if __name__ == '__main__':
    create_directories()
    app.run(host='0.0.0.0', port=8652, debug=False)
