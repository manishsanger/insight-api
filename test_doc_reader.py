#!/usr/bin/env python3
"""
Test script for Document Reader Service
"""

import requests
import json
import time
from io import BytesIO
from PIL import Image

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
            print(f"❌ API docs failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API docs error: {str(e)}")
        return False

def create_test_image():
    """Create a simple test image with text"""
    # Create a simple image with text
    img = Image.new('RGB', (400, 200), color='white')
    # Note: For a real test, you'd need PIL with text capabilities
    # For now, we'll create a simple colored image
    
    # Convert to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes

def test_document_processing():
    """Test document processing endpoint"""
    print("\n🔍 Testing document processing...")
    try:
        # Create a test image
        test_image = create_test_image()
        
        # Prepare the file for upload
        files = {
            'file': ('test_document.png', test_image, 'image/png')
        }
        
        print("   Sending test image to /api/public/doc-reader...")
        response = requests.post(
            "http://localhost:8654/api/public/doc-reader", 
            files=files,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document processing successful")
            print(f"   Document ID: {result.get('id')}")
            print(f"   Model used: {result.get('model')}")
            print(f"   Service: {result.get('service')}")
            print(f"   Extracted fields: {len(result.get('extracted_info', {}))}")
            
            # Show some extracted info if available
            extracted = result.get('extracted_info', {})
            if extracted:
                print("   Extracted information:")
                for key, value in list(extracted.items())[:3]:  # Show first 3 items
                    if value:
                        print(f"     {key}: {value}")
            
            return True
        else:
            print(f"❌ Document processing failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Document processing error: {str(e)}")
        return False

def test_invalid_file():
    """Test with invalid file type"""
    print("\n🔍 Testing invalid file handling...")
    try:
        # Create a text file (invalid type)
        files = {
            'file': ('test.txt', BytesIO(b'This is not an image'), 'text/plain')
        }
        
        response = requests.post(
            "http://localhost:8654/api/public/doc-reader", 
            files=files,
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ Invalid file type correctly rejected")
            return True
        else:
            print(f"❌ Invalid file handling failed: Expected 400, got {response.status_code}")
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
    
    tests = [
        test_health,
        test_api_docs,
        test_document_processing,
        test_invalid_file
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Document Reader Service is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the service configuration.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
