import pytest
import os
import tempfile
import shutil
from app import app, create_directories

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    app.config['API_TOKEN'] = 'test_token'
    app.config['AUDIO_UPLOAD_FOLDER'] = tempfile.mkdtemp()
    app.config['TEMP_FOLDER'] = tempfile.mkdtemp()
    
    with app.test_client() as client:
        with app.app_context():
            create_directories()
            yield client
    
    # Cleanup
    shutil.rmtree(app.config['AUDIO_UPLOAD_FOLDER'], ignore_errors=True)
    shutil.rmtree(app.config['TEMP_FOLDER'], ignore_errors=True)

def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'status' in data
    assert 'timestamp' in data
    assert 'model' in data
    assert 'storage' in data

def test_convert_without_token(client):
    """Test convert endpoint without authentication token"""
    response = client.post('/api/convert')
    assert response.status_code == 401
    
    data = response.get_json()
    assert 'message' in data
    assert 'token' in data['message'].lower()

def test_convert_with_invalid_token(client):
    """Test convert endpoint with invalid token"""
    headers = {'Authorization': 'Bearer invalid_token'}
    response = client.post('/api/convert', headers=headers)
    assert response.status_code == 401

def test_convert_without_file(client):
    """Test convert endpoint without file"""
    headers = {'Authorization': 'Bearer test_token'}
    response = client.post('/api/convert', headers=headers)
    assert response.status_code == 400
    
    data = response.get_json()
    assert 'message' in data
    assert 'audio file' in data['message'].lower()

def test_convert_with_empty_file(client):
    """Test convert endpoint with empty file"""
    headers = {'Authorization': 'Bearer test_token'}
    data = {'audio_file': (tempfile.NamedTemporaryFile(), '')}
    response = client.post('/api/convert', headers=headers, data=data)
    assert response.status_code == 400

def test_files_endpoint_without_token(client):
    """Test files endpoint without authentication"""
    response = client.get('/api/files')
    assert response.status_code == 401

def test_files_endpoint_with_token(client):
    """Test files endpoint with valid token"""
    headers = {'Authorization': 'Bearer test_token'}
    response = client.get('/api/files', headers=headers)
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'files' in data
    assert 'total_files' in data
    assert isinstance(data['files'], list)

def test_api_documentation(client):
    """Test that API documentation is accessible"""
    response = client.get('/docs/')
    assert response.status_code == 200

if __name__ == '__main__':
    pytest.main([__file__])
