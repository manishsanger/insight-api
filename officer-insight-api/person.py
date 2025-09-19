"""
Person API Module for Officer Insight API
Handles person CRUD operations, search, and management
"""

from datetime import datetime
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

# Create namespace
person_ns = Namespace('persons', description='Person management operations')

# Swagger models
person_model = person_ns.model('Person', {
    'name': fields.String(description='Full name'),
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name'),
    'phone_number': fields.String(description='Phone number'),
    'mobile_number': fields.String(description='Mobile number'),
    'gender': fields.String(description='Gender (Male/Female/Other)'),
    'date_of_birth': fields.String(description='Date of birth (YYYY-MM-DD)'),
    'place_of_birth': fields.String(description='Place of birth'),
    'nationality': fields.String(description='Nationality'),
    'pin_code': fields.String(description='Pin code'),
    'address': fields.String(description='Address'),
    'person_photos': fields.List(fields.String, description='List of image IDs'),
    'type_of_document': fields.String(description='Type of document'),
    'date_of_issue': fields.String(description='Document issue date (YYYY-MM-DD)'),
    'expiry_date': fields.String(description='Document expiry date (YYYY-MM-DD)')
})

person_response_model = person_ns.model('PersonResponse', {
    'id': fields.String(description='Person ID'),
    'name': fields.String(description='Full name'),
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
    'phone_number': fields.String(description='Phone number'),
    'mobile_number': fields.String(description='Mobile number'),
    'gender': fields.String(description='Gender'),
    'date_of_birth': fields.String(description='Date of birth'),
    'place_of_birth': fields.String(description='Place of birth'),
    'nationality': fields.String(description='Nationality'),
    'pin_code': fields.String(description='Pin code'),
    'address': fields.String(description='Address'),
    'person_photos': fields.List(fields.Raw, description='List of image objects'),
    'type_of_document': fields.String(description='Type of document'),
    'date_of_issue': fields.String(description='Document issue date'),
    'expiry_date': fields.String(description='Document expiry date'),
    'is_deleted': fields.Boolean(description='Soft delete flag'),
    'created_at': fields.DateTime(description='Created timestamp'),
    'updated_at': fields.DateTime(description='Updated timestamp')
})

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

def get_image_objects_by_ids(image_ids):
    """Get image objects by their IDs"""
    if not image_ids:
        return []
    
    try:
        db = get_mongo_db()
        object_ids = [ObjectId(img_id) for img_id in image_ids if img_id]
        images = list(db.images.find({'_id': {'$in': object_ids}}))
        return [serialize_mongo_doc(img) for img in images]
    except Exception as e:
        print(f"Error getting image objects: {e}")
        return []

def validate_person_data(data):
    """Validate person data"""
    errors = []
    
    if not data.get('first_name'):
        errors.append('first_name is required')
    
    if not data.get('last_name'):
        errors.append('last_name is required')
    
    # Validate date format if provided
    date_fields = ['date_of_birth', 'date_of_issue', 'expiry_date']
    for field in date_fields:
        if data.get(field):
            try:
                datetime.strptime(data[field], '%Y-%m-%d')
            except ValueError:
                errors.append(f'{field} must be in YYYY-MM-DD format')
    
    # Validate gender if provided
    if data.get('gender') and data['gender'] not in ['Male', 'Female', 'Other']:
        errors.append('gender must be Male, Female, or Other')
    
    return errors

@person_ns.route('/create')
class PersonCreate(Resource):
    @jwt_required()
    @person_ns.expect(person_model)
    def post(self):
        """Create a new person"""
        try:
            data = request.get_json()
            
            # Validate data
            errors = validate_person_data(data)
            if errors:
                return {'message': 'Validation errors', 'errors': errors}, 400
            
            # Create full name if not provided
            if not data.get('name'):
                data['name'] = f"{data['first_name']} {data['last_name']}"
            
            # Get image objects if person_photos are provided
            person_photos = []
            if data.get('person_photos'):
                person_photos = get_image_objects_by_ids(data['person_photos'])
            
            # Create person document
            person_doc = {
                'name': data['name'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'phone_number': data.get('phone_number', ''),
                'mobile_number': data.get('mobile_number', ''),
                'gender': data.get('gender', ''),
                'date_of_birth': data.get('date_of_birth', ''),
                'place_of_birth': data.get('place_of_birth', ''),
                'nationality': data.get('nationality', ''),
                'pin_code': data.get('pin_code', ''),
                'address': data.get('address', ''),
                'person_photos': person_photos,
                'type_of_document': data.get('type_of_document', ''),
                'date_of_issue': data.get('date_of_issue', ''),
                'expiry_date': data.get('expiry_date', ''),
                'is_deleted': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            db = get_mongo_db()
            result = db.persons.insert_one(person_doc)
            
            # Return created person
            person_doc['_id'] = result.inserted_id
            person_doc['id'] = str(result.inserted_id)
            
            return {
                'message': 'Person created successfully',
                'person': serialize_mongo_doc(person_doc)
            }, 201
            
        except Exception as e:
            print(f"Error creating person: {e}")
            return {'message': 'Internal server error'}, 500

@person_ns.route('/list')
class PersonList(Resource):
    @jwt_required()
    def get(self):
        """Get list of persons with pagination"""
        try:
            # Get query parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
            
            # Build query
            query = {}
            if not include_deleted:
                query['is_deleted'] = {'$ne': True}
            
            db = get_mongo_db()
            
            # Get total count
            total = db.persons.count_documents(query)
            
            # Get paginated results
            persons = list(db.persons.find(query)
                          .sort('created_at', -1)
                          .skip((page - 1) * per_page)
                          .limit(per_page))
            
            # Serialize results
            serialized_persons = []
            for person in persons:
                serialized_person = serialize_mongo_doc(person)
                serialized_person['id'] = serialized_person['_id']
                serialized_persons.append(serialized_person)
            
            return {
                'persons': serialized_persons,
                'pagination': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'pages': (total + per_page - 1) // per_page
                }
            }, 200
            
        except Exception as e:
            print(f"Error getting person list: {e}")
            return {'message': 'Internal server error'}, 500

@person_ns.route('/search')
class PersonSearch(Resource):
    @jwt_required()
    def get(self):
        """Search persons by name (first name and last name)"""
        try:
            # Get query parameters
            first_name = request.args.get('first_name', '').strip()
            last_name = request.args.get('last_name', '').strip()
            name = request.args.get('name', '').strip()
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
            
            if not first_name and not last_name and not name:
                return {'message': 'At least one of first_name, last_name, or name is required'}, 400
            
            # Build search query
            search_conditions = []
            
            if first_name:
                search_conditions.append({
                    'first_name': {'$regex': first_name, '$options': 'i'}
                })
            
            if last_name:
                search_conditions.append({
                    'last_name': {'$regex': last_name, '$options': 'i'}
                })
            
            if name:
                search_conditions.append({
                    'name': {'$regex': name, '$options': 'i'}
                })
            
            query = {}
            if search_conditions:
                query['$or'] = search_conditions
            
            if not include_deleted:
                query['is_deleted'] = {'$ne': True}
            
            db = get_mongo_db()
            
            # Get total count
            total = db.persons.count_documents(query)
            
            # Get paginated results
            persons = list(db.persons.find(query)
                          .sort('created_at', -1)
                          .skip((page - 1) * per_page)
                          .limit(per_page))
            
            # Serialize results
            serialized_persons = []
            for person in persons:
                serialized_person = serialize_mongo_doc(person)
                serialized_person['id'] = serialized_person['_id']
                serialized_persons.append(serialized_person)
            
            return {
                'persons': serialized_persons,
                'pagination': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'pages': (total + per_page - 1) // per_page
                },
                'search_criteria': {
                    'first_name': first_name,
                    'last_name': last_name,
                    'name': name
                }
            }, 200
            
        except Exception as e:
            print(f"Error searching persons: {e}")
            return {'message': 'Internal server error'}, 500

@person_ns.route('/<person_id>')
class PersonDetail(Resource):
    @jwt_required()
    def get(self, person_id):
        """Get single person details"""
        try:
            db = get_mongo_db()
            person = db.persons.find_one({'_id': ObjectId(person_id)})
            
            if not person:
                return {'message': 'Person not found'}, 404
            
            serialized_person = serialize_mongo_doc(person)
            serialized_person['id'] = serialized_person['_id']
            
            return {'person': serialized_person}, 200
            
        except Exception as e:
            print(f"Error getting person details: {e}")
            return {'message': 'Internal server error'}, 500
    
    @jwt_required()
    @person_ns.expect(person_model)
    def put(self, person_id):
        """Update person details"""
        try:
            data = request.get_json()
            
            # Validate data
            errors = validate_person_data(data)
            if errors:
                return {'message': 'Validation errors', 'errors': errors}, 400
            
            db = get_mongo_db()
            
            # Check if person exists
            existing_person = db.persons.find_one({'_id': ObjectId(person_id)})
            if not existing_person:
                return {'message': 'Person not found'}, 404
            
            # Create full name if not provided
            if not data.get('name') and (data.get('first_name') or data.get('last_name')):
                first_name = data.get('first_name', existing_person.get('first_name', ''))
                last_name = data.get('last_name', existing_person.get('last_name', ''))
                data['name'] = f"{first_name} {last_name}"
            
            # Handle person photos update (merge with existing)
            if 'person_photos' in data:
                existing_photo_ids = [img.get('id') if isinstance(img, dict) else str(img) 
                                    for img in existing_person.get('person_photos', [])]
                new_photo_ids = data['person_photos']
                
                # Merge unique photo IDs
                all_photo_ids = list(set(existing_photo_ids + new_photo_ids))
                data['person_photos'] = get_image_objects_by_ids(all_photo_ids)
            
            # Update document
            update_data = {k: v for k, v in data.items() if v is not None}
            update_data['updated_at'] = datetime.utcnow()
            
            result = db.persons.update_one(
                {'_id': ObjectId(person_id)},
                {'$set': update_data}
            )
            
            if result.matched_count:
                # Return updated person
                updated_person = db.persons.find_one({'_id': ObjectId(person_id)})
                serialized_person = serialize_mongo_doc(updated_person)
                serialized_person['id'] = serialized_person['_id']
                
                return {
                    'message': 'Person updated successfully',
                    'person': serialized_person
                }, 200
            else:
                return {'message': 'Person not found'}, 404
            
        except Exception as e:
            print(f"Error updating person: {e}")
            return {'message': 'Internal server error'}, 500
    
    @jwt_required()
    def delete(self, person_id):
        """Hard delete person"""
        try:
            db = get_mongo_db()
            result = db.persons.delete_one({'_id': ObjectId(person_id)})
            
            if result.deleted_count:
                return {'message': 'Person deleted successfully'}, 200
            else:
                return {'message': 'Person not found'}, 404
                
        except Exception as e:
            print(f"Error deleting person: {e}")
            return {'message': 'Internal server error'}, 500

@person_ns.route('/<person_id>/soft-delete')
class PersonSoftDelete(Resource):
    @jwt_required()
    def patch(self, person_id):
        """Soft delete person (mark as deleted)"""
        try:
            db = get_mongo_db()
            result = db.persons.update_one(
                {'_id': ObjectId(person_id)},
                {'$set': {
                    'is_deleted': True,
                    'deleted_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }}
            )
            
            if result.matched_count:
                return {'message': 'Person soft deleted successfully'}, 200
            else:
                return {'message': 'Person not found'}, 404
                
        except Exception as e:
            print(f"Error soft deleting person: {e}")
            return {'message': 'Internal server error'}, 500

@person_ns.route('/<person_id>/restore')
class PersonRestore(Resource):
    @jwt_required()
    def patch(self, person_id):
        """Restore soft deleted person"""
        try:
            db = get_mongo_db()
            result = db.persons.update_one(
                {'_id': ObjectId(person_id)},
                {'$set': {
                    'is_deleted': False,
                    'updated_at': datetime.utcnow()
                }, '$unset': {
                    'deleted_at': ""
                }}
            )
            
            if result.matched_count:
                return {'message': 'Person restored successfully'}, 200
            else:
                return {'message': 'Person not found'}, 404
                
        except Exception as e:
            print(f"Error restoring person: {e}")
            return {'message': 'Internal server error'}, 500

# Health check for person service
@person_ns.route('/health')
class PersonHealth(Resource):
    def get(self):
        """Health check for person service"""
        try:
            # Check database connection
            db = get_mongo_db()
            db.command('ping')
            
            # Get collection stats
            total_persons = db.persons.count_documents({})
            active_persons = db.persons.count_documents({'is_deleted': {'$ne': True}})
            deleted_persons = db.persons.count_documents({'is_deleted': True})
            
            return {
                'status': 'healthy',
                'statistics': {
                    'total_persons': total_persons,
                    'active_persons': active_persons,
                    'deleted_persons': deleted_persons
                }
            }, 200
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }, 500
