#!/usr/bin/env python3
"""
Test script to verify the security implementation across all services.
This script tests:
1. Public endpoints (health, auth/login) - should work without token
2. Secured endpoints - should require bearer token
3. Authentication flow - login should return JWT token
"""

import requests
import json

# Service endpoints
SERVICES = {
    'officer-insight-api': 'http://localhost:8650',
    'speech2text-service': 'http://localhost:8652', 
    'car-identifier-service': 'http://localhost:8653',
    'doc-reader-service': 'http://localhost:8654'
}

def test_public_endpoints():
    """Test that public endpoints (health) work without authentication"""
    print("🔍 Testing public endpoints (should work without token)...")
    
    for service_name, base_url in SERVICES.items():
        try:
            # Test health endpoint
            health_url = f"{base_url}/api/public/health"
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {service_name} health endpoint accessible")
            else:
                print(f"❌ {service_name} health endpoint failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {service_name} health endpoint error: {e}")

def test_auth_endpoint():
    """Test authentication endpoint and get JWT token"""
    print("\n🔑 Testing authentication endpoint...")
    
    auth_url = f"{SERVICES['officer-insight-api']}/api/auth/login"
    login_data = {
        'username': 'admin',
        'password': 'Apple@123'
    }
    
    try:
        response = requests.post(auth_url, json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                print("✅ Authentication successful - JWT token received")
                return data['access_token']
            else:
                print("❌ Authentication response missing token")
                return None
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_secured_endpoints_without_token():
    """Test that secured endpoints reject requests without token"""
    print("\n🚫 Testing secured endpoints without token (should be rejected)...")
    
    secured_endpoints = [
        (SERVICES['officer-insight-api'], '/api/parse-message'),
        (SERVICES['officer-insight-api'], '/images/serve/2023-01-01/test.jpg'),  # Images endpoint
        (SERVICES['speech2text-service'], '/api/convert'),
        (SERVICES['speech2text-service'], '/api/process-text'),
        (SERVICES['speech2text-service'], '/api/files'),
        (SERVICES['car-identifier-service'], '/api/car-identifier'),
        (SERVICES['doc-reader-service'], '/api/doc-reader')
    ]
    
    for base_url, endpoint in secured_endpoints:
        try:
            # Use GET for images endpoints, POST for others
            if '/images/' in endpoint:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code in [401, 422]:  # 401 Unauthorized or 422 for missing token
                print(f"✅ {endpoint} correctly rejected without token")
            else:
                print(f"❌ {endpoint} should have rejected request: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} error: {e}")

def test_secured_endpoints_with_token(token):
    """Test that secured endpoints work with valid token"""
    if not token:
        print("\n❌ No token available for testing secured endpoints")
        return
        
    print("\n🔐 Testing secured endpoints with token (should work)...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test endpoints that don't require file uploads
    get_endpoints = [
        (SERVICES['speech2text-service'], '/api/files')
    ]
    
    for base_url, endpoint in get_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            
            if response.status_code in [200, 405]:  # 200 OK or 405 Method Not Allowed (but authenticated)
                print(f"✅ {endpoint} accepted token")
            else:
                print(f"❌ {endpoint} rejected valid token: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} error: {e}")

def test_path_changes():
    """Test that old public paths for secured endpoints are no longer accessible"""
    print("\n🔄 Testing path changes (old public paths should not exist)...")
    
    old_public_paths = [
        (SERVICES['car-identifier-service'], '/api/public/car-identifier'),
        (SERVICES['doc-reader-service'], '/api/public/doc-reader')
    ]
    
    for base_url, endpoint in old_public_paths:
        try:
            response = requests.post(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 404:
                print(f"✅ Old public path {endpoint} correctly removed")
            else:
                print(f"❌ Old public path {endpoint} still exists: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} error: {e}")

def main():
    print("=" * 60)
    print("INSIGHT API SECURITY TEST SUITE")
    print("=" * 60)
    
    # Test public endpoints
    test_public_endpoints()
    
    # Test authentication and get token
    token = test_auth_endpoint()
    
    # Test secured endpoints without token
    test_secured_endpoints_without_token()
    
    # Test secured endpoints with token
    test_secured_endpoints_with_token(token)
    
    # Test path changes
    test_path_changes()
    
    print("\n" + "=" * 60)
    print("SECURITY TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()
