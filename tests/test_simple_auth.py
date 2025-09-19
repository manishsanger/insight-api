#!/usr/bin/env python3

import requests
import json

# Test JWT authentication manually
def test_jwt_auth():
    print("Testing JWT Authentication...")
    
    # 1. Get JWT token
    auth_url = "http://localhost:8650/api/auth/login"
    login_data = {"username": "admin", "password": "Apple@123"}
    
    try:
        response = requests.post(auth_url, json=login_data, timeout=10)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"✅ Got JWT token: {token[:50]}...")
            
            # 2. Test with token
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test car-identifier
            print("\nTesting car-identifier with token...")
            test_url = "http://localhost:8653/api/car-identifier"
            
            # Use a simple POST with minimal data to avoid file upload issues
            test_response = requests.get(test_url, headers=headers, timeout=10)
            print(f"Status: {test_response.status_code}")
            if test_response.status_code != 200:
                print(f"Response: {test_response.text}")
                
        else:
            print(f"❌ Login failed: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_jwt_auth()
