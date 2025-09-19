"""
Images API Module for Officer Insight API
Handles image upload, storage, retrieval and management
"""

import os
import uuid
from datetime import datetime
from flask import request, send_file, current_app
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from bson import ObjectId
import shutil

# Create namespace
images_ns = Namespace('images', description='Image management operations')

# Swagger models
image_upload_model = images_ns.model('ImageUpload', {
    'user_id': fields.String(required=True, description='User ID who is uploading'),
    'username': fields.String(required=True, description='Username who is uploading')
})

image_response_model = images_ns.model('ImageResponse', {
    'id': fields.String(description='Image ID'),
    'storage_path': fields.String(description='File storage path'),
    'image_url': fields.String(description='Image access URL'),
    'filename': fields.String(description='Original filename'),
    'upload_date': fields.DateTime(description='Upload timestamp'),
    'uploaded_by': fields.String(description='User ID who uploaded'),
    'username': fields.String(description='Username who uploaded'),
    'file_size': fields.Integer(description='File size in bytes'),
    'file_type': fields.String(description='File MIME type')
})

# Configurable parameters with environment variable overrides
def get_allowed_extensions():
    """Get allowed file extensions from environment or default"""
    env_extensions = os.getenv('IMAGES_ALLOWED_EXTENSIONS', 'jpg,jpeg,png,gif,bmp,tiff')
    return set(ext.strip().lower() for ext in env_extensions.split(','))

def get_max_file_size():
    """Get maximum file size from environment or default (16MB)"""
    try:
        return int(os.getenv('IMAGES_MAX_FILE_SIZE', 16 * 1024 * 1024))
    except ValueError:
        return 16 * 1024 * 1024

def get_upload_base_path():
    """Get upload base path from environment or default"""
    return os.getenv('IMAGES_UPLOAD_BASE_PATH', '/app/data/images')

# Configuration
ALLOWED_EXTENSIONS = get_allowed_extensions()
MAX_FILE_SIZE = get_max_file_size()
UPLOAD_BASE_PATH = get_upload_base_path()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_directory(date_path):
    """Ensure upload directory exists"""
    full_path = os.path.join(UPLOAD_BASE_PATH, date_path)
    os.makedirs(full_path, exist_ok=True)
    return full_path

def generate_unique_filename(original_filename):
    """Generate unique filename while preserving extension"""
    filename, ext = os.path.splitext(original_filename)
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{ext}"

def save_uploaded_file(file, date_path, unique_filename):
    """Save uploaded file to disk"""
    directory = ensure_upload_directory(date_path)
    file_path = os.path.join(directory, unique_filename)
    file.save(file_path)
    return file_path

def get_mongo_db():
    """Get MongoDB database instance"""
    from app import mongo
    return mongo.db

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

@images_ns.route('/upload')
class ImageUpload(Resource):
    @jwt_required()
    @images_ns.expect(image_upload_model)
    def post(self):
        """Upload single or multiple images"""
        try:
            # Get form data
            user_id = request.form.get('user_id')
            username = request.form.get('username')
            
            if not user_id or not username:
                return {'message': 'user_id and username are required'}, 400
            
            # Get uploaded files
            uploaded_files = request.files.getlist('images')
            if not uploaded_files or all(f.filename == '' for f in uploaded_files):
                return {'message': 'No images provided'}, 400
            
            # Process each file
            uploaded_images = []
            upload_date = datetime.utcnow()
            date_path = upload_date.strftime('%Y-%m-%d')
            
            db = get_mongo_db()
            
            for file in uploaded_files:
                if file.filename == '':
                    continue
                
                # Validate file
                if not allowed_file(file.filename):
                    return {'message': f'File type not allowed: {file.filename}'}, 400
                
                # Check file size
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
                
                if file_size > MAX_FILE_SIZE:
                    return {'message': f'File too large: {file.filename}. Max size: 16MB'}, 400
                
                # Generate unique filename and save
                secure_original = secure_filename(file.filename)
                unique_filename = generate_unique_filename(secure_original)
                storage_path = save_uploaded_file(file, date_path, unique_filename)
                
                # Create image URL
                image_url = f"http://localhost:8650/api/images/serve/{date_path}/{unique_filename}"
                
                # Create image document
                image_doc = {
                    'storage_path': storage_path,
                    'image_url': image_url,
                    'filename': secure_original,
                    'unique_filename': unique_filename,
                    'upload_date': upload_date,
                    'uploaded_by': user_id,
                    'username': username,
                    'file_size': file_size,
                    'file_type': file.content_type or 'application/octet-stream',
                    'date_path': date_path,
                    'created_at': upload_date,
                    'updated_at': upload_date
                }
                
                # Save to database
                result = db.images.insert_one(image_doc)
                image_doc['_id'] = result.inserted_id
                image_doc['id'] = str(result.inserted_id)
                
                uploaded_images.append(serialize_mongo_doc(image_doc))
            
            return {
                'message': f'Successfully uploaded {len(uploaded_images)} images',
                'images': uploaded_images
            }, 201
            
        except Exception as e:
            print(f"Error uploading images: {e}")
            return {'message': 'Internal server error'}, 500

@images_ns.route('/list')
class ImageList(Resource):
    @jwt_required()
    def get(self):
        """Get list of images with pagination"""
        try:
            # Get query parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            user_id = request.args.get('user_id')
            username = request.args.get('username')
            
            # Build query
            query = {}
            if user_id:
                query['uploaded_by'] = user_id
            if username:
                query['username'] = username
            
            db = get_mongo_db()
            
            # Get total count
            total = db.images.count_documents(query)
            
            # Get paginated results
            images = list(db.images.find(query)
                         .sort('upload_date', -1)
                         .skip((page - 1) * per_page)
                         .limit(per_page))
            
            # Serialize results
            serialized_images = []
            for image in images:
                serialized_image = serialize_mongo_doc(image)
                serialized_image['id'] = serialized_image['_id']
                serialized_images.append(serialized_image)
            
            return {
                'images': serialized_images,
                'pagination': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'pages': (total + per_page - 1) // per_page
                }
            }, 200
            
        except Exception as e:
            print(f"Error getting image list: {e}")
            return {'message': 'Internal server error'}, 500

@images_ns.route('/get-by-ids')
class ImagesByIds(Resource):
    @jwt_required()
    def post(self):
        """Get images by list of image IDs"""
        try:
            data = request.get_json()
            image_ids = data.get('image_ids', [])
            
            if not image_ids:
                return {'message': 'image_ids list is required'}, 400
            
            # Convert string IDs to ObjectIds
            object_ids = []
            for img_id in image_ids:
                try:
                    object_ids.append(ObjectId(img_id))
                except:
                    return {'message': f'Invalid image ID: {img_id}'}, 400
            
            db = get_mongo_db()
            
            # Find images
            images = list(db.images.find({'_id': {'$in': object_ids}}))
            
            # Serialize results
            serialized_images = []
            for image in images:
                serialized_image = serialize_mongo_doc(image)
                serialized_image['id'] = serialized_image['_id']
                serialized_images.append(serialized_image)
            
            return {
                'images': serialized_images,
                'found_count': len(serialized_images),
                'requested_count': len(image_ids)
            }, 200
            
        except Exception as e:
            print(f"Error getting images by IDs: {e}")
            return {'message': 'Internal server error'}, 500

@images_ns.route('/<image_id>')
class ImageDetail(Resource):
    @jwt_required()
    def get(self, image_id):
        """Get single image details"""
        try:
            db = get_mongo_db()
            image = db.images.find_one({'_id': ObjectId(image_id)})
            
            if not image:
                return {'message': 'Image not found'}, 404
            
            serialized_image = serialize_mongo_doc(image)
            serialized_image['id'] = serialized_image['_id']
            
            return {'image': serialized_image}, 200
            
        except Exception as e:
            print(f"Error getting image details: {e}")
            return {'message': 'Internal server error'}, 500
    
    @jwt_required()
    def delete(self, image_id):
        """Delete image from database and storage"""
        try:
            db = get_mongo_db()
            image = db.images.find_one({'_id': ObjectId(image_id)})
            
            if not image:
                return {'message': 'Image not found'}, 404
            
            # Delete file from storage
            try:
                if os.path.exists(image['storage_path']):
                    os.remove(image['storage_path'])
            except Exception as e:
                print(f"Warning: Could not delete file {image['storage_path']}: {e}")
            
            # Delete from database
            db.images.delete_one({'_id': ObjectId(image_id)})
            
            return {'message': 'Image deleted successfully'}, 200
            
        except Exception as e:
            print(f"Error deleting image: {e}")
            return {'message': 'Internal server error'}, 500

@images_ns.route('/serve/<date_path>/<filename>')
class ImageServe(Resource):
    @jwt_required()
    def get(self, date_path, filename):
        """Serve image file over HTTP"""
        try:
            file_path = os.path.join(UPLOAD_BASE_PATH, date_path, filename)
            
            if not os.path.exists(file_path):
                return {'message': 'Image not found'}, 404
            
            return send_file(file_path)
            
        except Exception as e:
            print(f"Error serving image: {e}")
            return {'message': 'Internal server error'}, 500

@images_ns.route('/bulk-delete')
class ImageBulkDelete(Resource):
    @jwt_required()
    def post(self):
        """Delete multiple images"""
        try:
            data = request.get_json()
            image_ids = data.get('image_ids', [])
            
            if not image_ids:
                return {'message': 'image_ids list is required'}, 400
            
            # Convert string IDs to ObjectIds
            object_ids = []
            for img_id in image_ids:
                try:
                    object_ids.append(ObjectId(img_id))
                except:
                    return {'message': f'Invalid image ID: {img_id}'}, 400
            
            db = get_mongo_db()
            
            # Find images first to get file paths
            images = list(db.images.find({'_id': {'$in': object_ids}}))
            
            # Delete files from storage
            deleted_files = 0
            for image in images:
                try:
                    if os.path.exists(image['storage_path']):
                        os.remove(image['storage_path'])
                        deleted_files += 1
                except Exception as e:
                    print(f"Warning: Could not delete file {image['storage_path']}: {e}")
            
            # Delete from database
            result = db.images.delete_many({'_id': {'$in': object_ids}})
            
            return {
                'message': f'Successfully deleted {result.deleted_count} images',
                'deleted_count': result.deleted_count,
                'deleted_files': deleted_files
            }, 200
            
        except Exception as e:
            print(f"Error bulk deleting images: {e}")
            return {'message': 'Internal server error'}, 500

# Health check for images service
@images_ns.route('/health')
class ImageHealth(Resource):
    def get(self):
        """Health check for images service"""
        try:
            # Check if upload directory exists and is writable
            test_date_path = datetime.now().strftime('%Y-%m-%d')
            test_dir = ensure_upload_directory(test_date_path)
            
            # Check database connection
            db = get_mongo_db()
            db.command('ping')
            
            return {
                'status': 'healthy',
                'upload_directory': UPLOAD_BASE_PATH,
                'allowed_extensions': list(ALLOWED_EXTENSIONS),
                'max_file_size': MAX_FILE_SIZE
            }, 200
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }, 500

@images_ns.route('/my-images')
class MyImages(Resource):
    @jwt_required()
    def get(self):
        """Get all images uploaded by the current user"""
        try:
            current_user_id = get_jwt_identity()
            
            # Find images uploaded by current user
            query = {'uploaded_by': current_user_id}
            
            db = get_mongo_db()
            images = list(db.images.find(query))
            
            # Convert ObjectId to string
            for image in images:
                image['id'] = str(image['_id'])
                del image['_id']
            
            return {
                'message': f'Found {len(images)} images',
                'images': images
            }, 200
            
        except Exception as e:
            print(f"Error fetching user images: {e}")
            return {'message': 'Internal server error'}, 500
