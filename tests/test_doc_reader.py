#!/usr/bin/env python3
"""
Test script for Document Reader Service with JWT authentication
"""

import requests
import json
import time
from io import BytesIO
from PIL import Image

def get_auth_token():
    """Get JWT authentication token"""
    try:
        response = requests.post("http://localhost:8650/api/auth/login", 
                               json={"username": "admin", "password": "Apple@123"})
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8654/api/public/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed")
            print(f"   Service: {health_data.get('service')}")
            print(f"   Model: {health_data.get('model')}")
            print(f"   Database: {health_data.get('services', {}).get('database')}")
            print(f"   Ollama: {health_data.get('services', {}).get('ollama')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_api_docs():
    """Test API documentation endpoint"""
    print("\n🔍 Testing API documentation...")
    try:
        response = requests.get("http://localhost:8654/docs/")
        if response.status_code == 200:
            print("✅ API documentation is accessible")
            return True
        else:
            print(f"❌ API documentation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API documentation error: {str(e)}")
        return False

def create_test_image():
    """Create a simple test image"""
    # Create a simple test image
    img = Image.new('RGB', (200, 100), color='white')
    
    # Convert to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes

def test_document_processing(token):
    """Test document processing endpoint with authentication"""
    print("\n🔍 Testing document processing...")
    try:
        # Create a test image
        test_image = create_test_image()
        
        # Prepare the file for upload
        files = {
            'file': ('test_document.png', test_image, 'image/png')
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        
        print("   Sending test image to /api/doc-reader...")
        response = requests.post(
            "http://localhost:8654/api/doc-reader", 
            files=files,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document processing successful")
            print(f"   Response ID: {result.get('id', 'N/A')}")
            print(f"   Model used: {result.get('model', 'N/A')}")
            print(f"   Service: {result.get('service', 'N/A')}")
            
            if 'extracted_info' in result:
                print(f"   Extracted info: {len(result['extracted_info'])} fields")
                for key, value in result['extracted_info'].items():
                    print(f"     {key}: {value}")
            else:
                print("   No extracted info returned")
            
            return True
        else:
            print(f"❌ Document processing failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Document processing error: {str(e)}")
        return False

def test_invalid_file(token):
    """Test with invalid file type"""
    print("\n🔍 Testing invalid file handling...")
    try:
        # Create a text file (invalid type)
        files = {
            'file': ('test.txt', BytesIO(b'This is not an image'), 'text/plain')
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(
            "http://localhost:8654/api/doc-reader", 
            files=files,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ Invalid file type correctly rejected")
            return True
        else:
            print(f"❌ Invalid file handling unexpected: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Invalid file test error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Document Reader Service Tests")
    print("=" * 50)
    
    # Wait for service to be ready
    print("⏳ Waiting for service to be ready...")
    time.sleep(2)
    
    # Get authentication token
    print("🔐 Getting authentication token...")
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    tests = [
        (test_health, []),
        (test_api_docs, []),
        (test_document_processing, [token]),
        (test_invalid_file, [token])
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func, args in tests:
        try:
            if test_func(*args):
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with error: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed")

if __name__ == "__main__":
    main()
