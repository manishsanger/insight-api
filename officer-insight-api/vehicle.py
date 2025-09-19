"""
Vehicle API Module for Officer Insight API
Handles vehicle CRUD operations, search, and management
"""

from datetime import datetime
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

# Create namespace
vehicle_ns = Namespace('vehicles', description='Vehicle management operations')

# Swagger models
vehicle_model = vehicle_ns.model('Vehicle', {
    'name': fields.String(description='Vehicle name/identifier'),
    'vehicle_registration_number': fields.String(required=True, description='Vehicle Registration Number (VRN)'),
    'model': fields.String(description='Vehicle model'),
    'vehicle_make': fields.String(description='Vehicle manufacturer/make'),
    'vehicle_model': fields.String(description='Vehicle model/series'),
    'vehicle_color': fields.String(description='Vehicle color'),
    'country_of_origin': fields.String(description='Country of origin'),
    'vehicle_photos': fields.List(fields.String, description='List of image IDs')
})

vehicle_response_model = vehicle_ns.model('VehicleResponse', {
    'id': fields.String(description='Vehicle ID'),
    'name': fields.String(description='Vehicle name/identifier'),
    'vehicle_registration_number': fields.String(description='Vehicle Registration Number'),
    'model': fields.String(description='Vehicle model'),
    'vehicle_make': fields.String(description='Vehicle manufacturer/make'),
    'vehicle_model': fields.String(description='Vehicle model/series'),
    'vehicle_color': fields.String(description='Vehicle color'),
    'country_of_origin': fields.String(description='Country of origin'),
    'vehicle_photos': fields.List(fields.Raw, description='List of image objects'),
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

def validate_vehicle_data(data):
    """Validate vehicle data"""
    errors = []
    
    if not data.get('vehicle_registration_number'):
        errors.append('vehicle_registration_number is required')
    
    return errors

@vehicle_ns.route('/create')
class VehicleCreate(Resource):
    @jwt_required()
    @vehicle_ns.expect(vehicle_model)
    def post(self):
        """Create a new vehicle"""
        try:
            data = request.get_json()
            
            # Validate data
            errors = validate_vehicle_data(data)
            if errors:
                return {'message': 'Validation errors', 'errors': errors}, 400
            
            # Check if VRN already exists
            db = get_mongo_db()
            existing_vehicle = db.vehicles.find_one({
                'vehicle_registration_number': data['vehicle_registration_number'],
                'is_deleted': {'$ne': True}
            })
            
            if existing_vehicle:
                return {'message': 'Vehicle with this registration number already exists'}, 400
            
            # Get image objects if vehicle_photos are provided
            vehicle_photos = []
            if data.get('vehicle_photos'):
                vehicle_photos = get_image_objects_by_ids(data['vehicle_photos'])
            
            # Create vehicle document
            vehicle_doc = {
                'name': data.get('name', ''),
                'vehicle_registration_number': data['vehicle_registration_number'].upper(),
                'model': data.get('model', ''),
                'vehicle_make': data.get('vehicle_make', ''),
                'vehicle_model': data.get('vehicle_model', ''),
                'vehicle_color': data.get('vehicle_color', ''),
                'country_of_origin': data.get('country_of_origin', ''),
                'vehicle_photos': vehicle_photos,
                'is_deleted': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = db.vehicles.insert_one(vehicle_doc)
            
            # Return created vehicle
            vehicle_doc['_id'] = result.inserted_id
            vehicle_doc['id'] = str(result.inserted_id)
            
            return {
                'message': 'Vehicle created successfully',
                'vehicle': serialize_mongo_doc(vehicle_doc)
            }, 201
            
        except Exception as e:
            print(f"Error creating vehicle: {e}")
            return {'message': 'Internal server error'}, 500

@vehicle_ns.route('/list')
class VehicleList(Resource):
    @jwt_required()
    def get(self):
        """Get list of vehicles with pagination"""
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
            total = db.vehicles.count_documents(query)
            
            # Get paginated results
            vehicles = list(db.vehicles.find(query)
                           .sort('created_at', -1)
                           .skip((page - 1) * per_page)
                           .limit(per_page))
            
            # Serialize results
            serialized_vehicles = []
            for vehicle in vehicles:
                serialized_vehicle = serialize_mongo_doc(vehicle)
                serialized_vehicle['id'] = serialized_vehicle['_id']
                serialized_vehicles.append(serialized_vehicle)
            
            return {
                'vehicles': serialized_vehicles,
                'pagination': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'pages': (total + per_page - 1) // per_page
                }
            }, 200
            
        except Exception as e:
            print(f"Error getting vehicle list: {e}")
            return {'message': 'Internal server error'}, 500

@vehicle_ns.route('/search')
class VehicleSearch(Resource):
    @jwt_required()
    def get(self):
        """Search vehicles by VRN (Vehicle Registration Number)"""
        try:
            # Get query parameters
            vrn = request.args.get('vrn', '').strip().upper()
            vehicle_make = request.args.get('vehicle_make', '').strip()
            vehicle_color = request.args.get('vehicle_color', '').strip()
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
            
            if not vrn and not vehicle_make and not vehicle_color:
                return {'message': 'At least one of vrn, vehicle_make, or vehicle_color is required'}, 400
            
            # Build search query
            search_conditions = []
            
            if vrn:
                search_conditions.append({
                    'vehicle_registration_number': {'$regex': vrn, '$options': 'i'}
                })
            
            if vehicle_make:
                search_conditions.append({
                    'vehicle_make': {'$regex': vehicle_make, '$options': 'i'}
                })
            
            if vehicle_color:
                search_conditions.append({
                    'vehicle_color': {'$regex': vehicle_color, '$options': 'i'}
                })
            
            query = {}
            if search_conditions:
                query['$or'] = search_conditions
            
            if not include_deleted:
                query['is_deleted'] = {'$ne': True}
            
            db = get_mongo_db()
            
            # Get total count
            total = db.vehicles.count_documents(query)
            
            # Get paginated results
            vehicles = list(db.vehicles.find(query)
                           .sort('created_at', -1)
                           .skip((page - 1) * per_page)
                           .limit(per_page))
            
            # Serialize results
            serialized_vehicles = []
            for vehicle in vehicles:
                serialized_vehicle = serialize_mongo_doc(vehicle)
                serialized_vehicle['id'] = serialized_vehicle['_id']
                serialized_vehicles.append(serialized_vehicle)
            
            return {
                'vehicles': serialized_vehicles,
                'pagination': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'pages': (total + per_page - 1) // per_page
                },
                'search_criteria': {
                    'vrn': vrn,
                    'vehicle_make': vehicle_make,
                    'vehicle_color': vehicle_color
                }
            }, 200
            
        except Exception as e:
            print(f"Error searching vehicles: {e}")
            return {'message': 'Internal server error'}, 500

@vehicle_ns.route('/<vehicle_id>')
class VehicleDetail(Resource):
    @jwt_required()
    def get(self, vehicle_id):
        """Get single vehicle details"""
        try:
            db = get_mongo_db()
            vehicle = db.vehicles.find_one({'_id': ObjectId(vehicle_id)})
            
            if not vehicle:
                return {'message': 'Vehicle not found'}, 404
            
            serialized_vehicle = serialize_mongo_doc(vehicle)
            serialized_vehicle['id'] = serialized_vehicle['_id']
            
            return {'vehicle': serialized_vehicle}, 200
            
        except Exception as e:
            print(f"Error getting vehicle details: {e}")
            return {'message': 'Internal server error'}, 500
    
    @jwt_required()
    @vehicle_ns.expect(vehicle_model)
    def put(self, vehicle_id):
        """Update vehicle details"""
        try:
            data = request.get_json()
            
            # Validate data
            errors = validate_vehicle_data(data)
            if errors:
                return {'message': 'Validation errors', 'errors': errors}, 400
            
            db = get_mongo_db()
            
            # Check if vehicle exists
            existing_vehicle = db.vehicles.find_one({'_id': ObjectId(vehicle_id)})
            if not existing_vehicle:
                return {'message': 'Vehicle not found'}, 404
            
            # Check if VRN already exists for other vehicles
            if data.get('vehicle_registration_number'):
                vrn_check = db.vehicles.find_one({
                    'vehicle_registration_number': data['vehicle_registration_number'].upper(),
                    '_id': {'$ne': ObjectId(vehicle_id)},
                    'is_deleted': {'$ne': True}
                })
                if vrn_check:
                    return {'message': 'Vehicle with this registration number already exists'}, 400
            
            # Handle vehicle photos update (merge with existing)
            if 'vehicle_photos' in data:
                existing_photo_ids = [img.get('id') if isinstance(img, dict) else str(img) 
                                    for img in existing_vehicle.get('vehicle_photos', [])]
                new_photo_ids = data['vehicle_photos']
                
                # Merge unique photo IDs
                all_photo_ids = list(set(existing_photo_ids + new_photo_ids))
                data['vehicle_photos'] = get_image_objects_by_ids(all_photo_ids)
            
            # Update document
            update_data = {k: v for k, v in data.items() if v is not None}
            if 'vehicle_registration_number' in update_data:
                update_data['vehicle_registration_number'] = update_data['vehicle_registration_number'].upper()
            update_data['updated_at'] = datetime.utcnow()
            
            result = db.vehicles.update_one(
                {'_id': ObjectId(vehicle_id)},
                {'$set': update_data}
            )
            
            if result.matched_count:
                # Return updated vehicle
                updated_vehicle = db.vehicles.find_one({'_id': ObjectId(vehicle_id)})
                serialized_vehicle = serialize_mongo_doc(updated_vehicle)
                serialized_vehicle['id'] = serialized_vehicle['_id']
                
                return {
                    'message': 'Vehicle updated successfully',
                    'vehicle': serialized_vehicle
                }, 200
            else:
                return {'message': 'Vehicle not found'}, 404
            
        except Exception as e:
            print(f"Error updating vehicle: {e}")
            return {'message': 'Internal server error'}, 500
    
    @jwt_required()
    def delete(self, vehicle_id):
        """Hard delete vehicle"""
        try:
            db = get_mongo_db()
            result = db.vehicles.delete_one({'_id': ObjectId(vehicle_id)})
            
            if result.deleted_count:
                return {'message': 'Vehicle deleted successfully'}, 200
            else:
                return {'message': 'Vehicle not found'}, 404
                
        except Exception as e:
            print(f"Error deleting vehicle: {e}")
            return {'message': 'Internal server error'}, 500

@vehicle_ns.route('/<vehicle_id>/soft-delete')
class VehicleSoftDelete(Resource):
    @jwt_required()
    def patch(self, vehicle_id):
        """Soft delete vehicle (mark as deleted)"""
        try:
            db = get_mongo_db()
            result = db.vehicles.update_one(
                {'_id': ObjectId(vehicle_id)},
                {'$set': {
                    'is_deleted': True,
                    'deleted_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }}
            )
            
            if result.matched_count:
                return {'message': 'Vehicle soft deleted successfully'}, 200
            else:
                return {'message': 'Vehicle not found'}, 404
                
        except Exception as e:
            print(f"Error soft deleting vehicle: {e}")
            return {'message': 'Internal server error'}, 500

@vehicle_ns.route('/<vehicle_id>/restore')
class VehicleRestore(Resource):
    @jwt_required()
    def patch(self, vehicle_id):
        """Restore soft deleted vehicle"""
        try:
            db = get_mongo_db()
            result = db.vehicles.update_one(
                {'_id': ObjectId(vehicle_id)},
                {'$set': {
                    'is_deleted': False,
                    'updated_at': datetime.utcnow()
                }, '$unset': {
                    'deleted_at': ""
                }}
            )
            
            if result.matched_count:
                return {'message': 'Vehicle restored successfully'}, 200
            else:
                return {'message': 'Vehicle not found'}, 404
                
        except Exception as e:
            print(f"Error restoring vehicle: {e}")
            return {'message': 'Internal server error'}, 500

# Health check for vehicle service
@vehicle_ns.route('/health')
class VehicleHealth(Resource):
    def get(self):
        """Health check for vehicle service"""
        try:
            # Check database connection
            db = get_mongo_db()
            db.command('ping')
            
            # Get collection stats
            total_vehicles = db.vehicles.count_documents({})
            active_vehicles = db.vehicles.count_documents({'is_deleted': {'$ne': True}})
            deleted_vehicles = db.vehicles.count_documents({'is_deleted': True})
            
            return {
                'status': 'healthy',
                'statistics': {
                    'total_vehicles': total_vehicles,
                    'active_vehicles': active_vehicles,
                    'deleted_vehicles': deleted_vehicles
                }
            }, 200
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }, 500
