import os
import uuid
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from werkzeug.utils import secure_filename
import tempfile
import shutil
import subprocess

app = Flask(__name__)

# Configuration
app.config['API_TOKEN'] = os.getenv('API_TOKEN', 'insight_speech_token_2024')
app.config['OLLAMA_URL'] = os.getenv('OLLAMA_URL', 'http://host.docker.internal:11434')
app.config['OLLAMA_MODEL'] = os.getenv('OLLAMA_MODEL', 'llama3.2:latest')
app.config['AUDIO_UPLOAD_FOLDER'] = '/app/audio_files'
app.config['TEMP_FOLDER'] = '/app/temp'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Initialize extensions
CORS(app)

# API Documentation
api = Api(app, version='1.0', title='Ollama Text and Audio Processing Service',
          description='Text and audio processing service using Ollama AI',
          doc='/docs/')

print(f"Using Ollama at: {app.config['OLLAMA_URL']}")
print(f"Using Ollama model: {app.config['OLLAMA_MODEL']}")

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

def convert_audio_to_text_with_ollama(audio_file_path):
    """Convert audio to text using a simple approach and then process with Ollama"""
    try:
        # For now, since Ollama doesn't directly support audio transcription,
        # we'll return a message asking for text input instead
        # In a production environment, you would integrate with a proper
        # speech-to-text service like OpenAI Whisper API, Google Speech-to-Text, etc.
        
        # Convert audio to a standard format for potential future integration
        temp_wav_path = audio_file_path.replace(audio_file_path.split('.')[-1], 'wav')
        
        # Use ffmpeg to convert audio to optimal format
        ffmpeg_command = [
            'ffmpeg', '-i', audio_file_path,
            '-ar', '16000',  # Sample rate
            '-ac', '1',      # Mono channel
            '-y',            # Overwrite output file
            temp_wav_path
        ]
        
        result = subprocess.run(ffmpeg_command, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            return "Error: Could not process audio file. Please ensure the audio file is in a supported format."
        
        # Since we don't have direct audio transcription with Ollama,
        # return a helpful message for now
        return f"Audio file processed and converted to WAV format. " \
               f"However, direct audio-to-text conversion with Ollama is not yet implemented. " \
               f"Please provide the text content of your audio message for processing."
        
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg processing error: {e}")
        return "Error processing audio file with FFmpeg."
    except Exception as e:
        print(f"Audio conversion error: {e}")
        return None
    finally:
        # Clean up temporary files
        if 'temp_wav_path' in locals() and os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)

def process_text_with_ollama(text):
    """Process text using Ollama to extract structured information"""
    try:
        prompt = f"""
You are an expert at extracting structured information from police reports and incident descriptions.

Parse the following text and extract information in the exact format shown in the example:

Input text: {text}

Please extract and format the information as follows:
- Offence Category: [type of offence]
- Driver Name: [full name]
- Date of Birth: [DD/MM/YYYY format]
- Gender: [Male/Female/Other]
- Address: [full address]
- Location of Offence: [location where offence occurred]
- Offence Occurred at: [time and date]
- Offence: [specific offence description]
- Vehicle Registration: [registration number]
- Vehicle Manufacturer: [car manufacturer]
- Vehicle Model: [car model and color]

Only include fields that are mentioned in the text. If information is not available, omit that field.
Format the response exactly as shown above with each field on a new line.
"""

        response = requests.post(
            f"{app.config['OLLAMA_URL']}/api/generate",
            json={
                "model": app.config['OLLAMA_MODEL'],
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            processed_text = result.get('response', '').strip()
            return processed_text
        else:
            print(f"Ollama API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Ollama text processing error: {e}")
        return None

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
    'audio_file': fields.Raw(description='Audio file to convert (optional)'),
    'text_message': fields.String(description='Text message to process (optional)')
})

process_text_model = api.model('ProcessText', {
    'text': fields.String(required=True, description='Text to process with Ollama')
})

error_model = api.model('Error', {
    'message': fields.String(description='Error message')
})

success_model = api.model('Success', {
    'text': fields.String(description='Converted/processed text'),
    'processed_output': fields.String(description='Structured output from Ollama'),
    'file_id': fields.String(description='Stored file ID (if audio file provided)'),
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
        """Convert audio file to text or process text message using Ollama"""
        # Verify authentication
        if not verify_token():
            return {'message': 'Invalid or missing API token'}, 401
        
        # Check if we have either audio file or text
        has_audio = 'audio_file' in request.files and request.files['audio_file'].filename != ''
        has_text = 'text_message' in request.form and request.form['text_message'].strip()
        
        if not has_audio and not has_text:
            return {'message': 'Either audio file or text message must be provided'}, 400
        
        try:
            final_text = ""
            file_id = None
            
            # Process audio file if provided
            if has_audio:
                file = request.files['audio_file']
                
                if not allowed_file(file.filename):
                    return {'message': f'File type not allowed. Supported types: {", ".join(ALLOWED_EXTENSIONS)}'}, 400
                
                # Generate unique file ID
                file_id = str(uuid.uuid4())
                filename = secure_filename(file.filename)
                file_extension = filename.rsplit('.', 1)[1].lower()
                
                # Create temporary file for processing
                temp_file_path = os.path.join(app.config['TEMP_FOLDER'], f"{file_id}.{file_extension}")
                file.save(temp_file_path)
                
                # Convert audio to text using Ollama approach
                print(f"Processing audio file: {filename}")
                audio_text = convert_audio_to_text_with_ollama(temp_file_path)
                
                if audio_text:
                    final_text = audio_text
                else:
                    return {'message': 'Failed to process audio file'}, 500
                
                # Save audio file permanently
                permanent_file_path = os.path.join(app.config['AUDIO_UPLOAD_FOLDER'], f"{file_id}_{filename}")
                shutil.move(temp_file_path, permanent_file_path)
            
            # Process text message if provided
            if has_text:
                text_message = request.form['text_message'].strip()
                if final_text:
                    final_text += "\n" + text_message
                else:
                    final_text = text_message
            
            # Process the final text with Ollama to extract structured information
            processed_output = process_text_with_ollama(final_text)
            
            if not processed_output:
                return {'message': 'Failed to process text with Ollama'}, 500
            
            # Log the processing
            log_entry = {
                'file_id': file_id,
                'text_length': len(final_text),
                'has_audio': has_audio,
                'has_text': has_text,
                'timestamp': datetime.utcnow().isoformat(),
            }
            
            print(f"Text processing completed: {log_entry}")
            
            return {
                'text': final_text,
                'processed_output': processed_output,
                'file_id': file_id,
                'timestamp': datetime.utcnow().isoformat()
            }, 200
            
        except Exception as e:
            # Clean up temporary file if it exists
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            print(f"Error processing request: {str(e)}")
            return {'message': f'Error processing request: {str(e)}'}, 500

@api.route('/api/process-text')
class ProcessText(Resource):
    @api.expect(process_text_model)
    def post(self):
        """Process text message using Ollama AI for structured information extraction"""
        # Verify authentication
        if not verify_token():
            return {'message': 'Invalid or missing API token'}, 401
        
        data = request.get_json()
        if not data or 'text' not in data:
            return {'message': 'Text field is required'}, 400
        
        text = data['text'].strip()
        if not text:
            return {'message': 'Text cannot be empty'}, 400
        
        try:
            # Process the text with Ollama
            processed_output = process_text_with_ollama(text)
            
            print(f"DEBUG: processed_output = {processed_output}")
            print(f"DEBUG: processed_output type = {type(processed_output)}")
            
            if not processed_output:
                print(f"DEBUG: processed_output is falsy, returning error")
                return {'message': 'Failed to process text with Ollama'}, 500
            
            print(f"DEBUG: About to return successful response")
            return {
                'text': text,
                'processed_output': processed_output,
                'file_id': None,
                'timestamp': datetime.utcnow().isoformat()
            }, 200
            
        except Exception as e:
            print(f"Error processing text: {str(e)}")
            return {'message': f'Error processing text: {str(e)}'}, 500

@api.route('/api/health')
class Health(Resource):
    def get(self):
        """Health check endpoint"""
        try:
            # Check if Ollama is accessible
            ollama_status = 'unhealthy'
            try:
                health_response = requests.get(
                    f"{app.config['OLLAMA_URL']}/api/tags",
                    timeout=5
                )
                if health_response.status_code == 200:
                    models = health_response.json().get('models', [])
                    model_names = [model.get('name', '') for model in models]
                    if app.config['OLLAMA_MODEL'] in model_names:
                        ollama_status = 'healthy'
                    else:
                        ollama_status = f'model_not_found_{app.config["OLLAMA_MODEL"]}'
                else:
                    ollama_status = f'api_error_{health_response.status_code}'
            except Exception as e:
                ollama_status = f'connection_error_{str(e)[:50]}'
            
            # Check disk space for audio storage
            disk_usage = shutil.disk_usage(app.config['AUDIO_UPLOAD_FOLDER'])
            free_space_gb = disk_usage.free / (1024**3)
            
            # Check if directories exist
            audio_dir_exists = os.path.exists(app.config['AUDIO_UPLOAD_FOLDER'])
            temp_dir_exists = os.path.exists(app.config['TEMP_FOLDER'])
            
            # Check if ffmpeg is available
            ffmpeg_available = False
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
                ffmpeg_available = True
            except:
                pass
            
            overall_status = 'healthy' if (
                ollama_status == 'healthy' and 
                free_space_gb > 1.0 and  # At least 1GB free
                audio_dir_exists and 
                temp_dir_exists and
                ffmpeg_available
            ) else 'unhealthy'
            
            return {
                'status': overall_status,
                'timestamp': datetime.utcnow().isoformat(),
                'ollama': {
                    'url': app.config['OLLAMA_URL'],
                    'model': app.config['OLLAMA_MODEL'],
                    'status': ollama_status
                },
                'storage': {
                    'audio_directory': audio_dir_exists,
                    'temp_directory': temp_dir_exists,
                    'free_space_gb': round(free_space_gb, 2)
                },
                'dependencies': {
                    'ffmpeg': ffmpeg_available
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
