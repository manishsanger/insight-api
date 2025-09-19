#!/usr/bin/env python3
"""
User-Specific Data Endpoints Test Script
Tests the new my-persons, my-vehicles, and my-images endpoints
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class UserSpecificEndpointsTest:
    def __init__(self):
        self.base_url = "http://localhost:8650"
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'response_data': response_data,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_auth_token(self):
        """Get JWT token for admin user"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"username": "admin", "password": "Apple@123"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('access_token')
                self.log_test("Authentication", True, f"Got JWT token: {self.admin_token[:20]}...")
                return True
            else:
                self.log_test("Authentication", False, f"Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Login error: {str(e)}")
            return False
    
    def get_headers(self):
        """Get headers with JWT token"""
        return {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
    
    def test_my_persons(self):
        """Test GET /persons/my-persons endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/persons/my-persons",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if 'message' in data and 'persons' in data:
                    persons_count = len(data['persons'])
                    self.log_test(
                        "My Persons Endpoint", 
                        True, 
                        f"Found {persons_count} persons for current user",
                        data
                    )
                    
                    # Validate each person has created_by field
                    for person in data['persons']:
                        if 'created_by' not in person:
                            self.log_test(
                                "My Persons Data Validation", 
                                False, 
                                "Person missing created_by field"
                            )
                            return False
                    
                    self.log_test(
                        "My Persons Data Validation", 
                        True, 
                        "All persons have proper user association"
                    )
                    
                else:
                    self.log_test(
                        "My Persons Endpoint", 
                        False, 
                        "Invalid response structure"
                    )
            else:
                self.log_test(
                    "My Persons Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("My Persons Endpoint", False, f"Request error: {str(e)}")
    
    def test_my_vehicles(self):
        """Test GET /vehicles/my-vehicles endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/vehicles/my-vehicles",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if 'message' in data and 'vehicles' in data:
                    vehicles_count = len(data['vehicles'])
                    self.log_test(
                        "My Vehicles Endpoint", 
                        True, 
                        f"Found {vehicles_count} vehicles for current user",
                        data
                    )
                    
                    # Validate each vehicle has created_by field
                    for vehicle in data['vehicles']:
                        if 'created_by' not in vehicle:
                            self.log_test(
                                "My Vehicles Data Validation", 
                                False, 
                                "Vehicle missing created_by field"
                            )
                            return False
                    
                    self.log_test(
                        "My Vehicles Data Validation", 
                        True, 
                        "All vehicles have proper user association"
                    )
                    
                else:
                    self.log_test(
                        "My Vehicles Endpoint", 
                        False, 
                        "Invalid response structure"
                    )
            else:
                self.log_test(
                    "My Vehicles Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("My Vehicles Endpoint", False, f"Request error: {str(e)}")
    
    def test_my_images(self):
        """Test GET /images/my-images endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/images/my-images",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if 'message' in data and 'images' in data:
                    images_count = len(data['images'])
                    self.log_test(
                        "My Images Endpoint", 
                        True, 
                        f"Found {images_count} images for current user",
                        data
                    )
                    
                    # Validate each image has uploaded_by field
                    for image in data['images']:
                        if 'uploaded_by' not in image:
                            self.log_test(
                                "My Images Data Validation", 
                                False, 
                                "Image missing uploaded_by field"
                            )
                            return False
                    
                    self.log_test(
                        "My Images Data Validation", 
                        True, 
                        "All images have proper user association"
                    )
                    
                else:
                    self.log_test(
                        "My Images Endpoint", 
                        False, 
                        "Invalid response structure"
                    )
            else:
                self.log_test(
                    "My Images Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("My Images Endpoint", False, f"Request error: {str(e)}")
    
    def test_authentication_required(self):
        """Test that endpoints require authentication"""
        endpoints = [
            "/persons/my-persons",
            "/vehicles/my-vehicles", 
            "/images/my-images"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 401:
                    self.log_test(
                        f"Auth Required - {endpoint}", 
                        True, 
                        "Correctly requires authentication"
                    )
                else:
                    self.log_test(
                        f"Auth Required - {endpoint}", 
                        False, 
                        f"Expected 401, got {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_test(
                    f"Auth Required - {endpoint}", 
                    False, 
                    f"Request error: {str(e)}"
                )
    
    def create_test_data(self):
        """Create test person and vehicle for testing"""
        # Create test person
        try:
            person_data = {
                "first_name": "Test",
                "last_name": "User",
                "phone_number": "123-456-7890",
                "gender": "Male",
                "nationality": "American"
            }
            
            response = requests.post(
                f"{self.base_url}/persons/create",
                headers=self.get_headers(),
                json=person_data
            )
            
            if response.status_code == 201:
                self.log_test("Create Test Person", True, "Test person created successfully")
            else:
                self.log_test("Create Test Person", False, f"Failed to create: {response.status_code}")
                
        except Exception as e:
            self.log_test("Create Test Person", False, f"Error: {str(e)}")
        
        # Create test vehicle
        try:
            vehicle_data = {
                "vehicle_registration_number": f"TEST{datetime.now().strftime('%H%M%S')}",
                "vehicle_make": "Test",
                "vehicle_model": "Model",
                "vehicle_color": "Blue",
                "country_of_origin": "USA"
            }
            
            response = requests.post(
                f"{self.base_url}/vehicles/create",
                headers=self.get_headers(),
                json=vehicle_data
            )
            
            if response.status_code == 201:
                self.log_test("Create Test Vehicle", True, "Test vehicle created successfully")
            else:
                self.log_test("Create Test Vehicle", False, f"Failed to create: {response.status_code}")
                
        except Exception as e:
            self.log_test("Create Test Vehicle", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all user-specific endpoint tests"""
        print("🚀 Starting User-Specific Data Endpoints Tests")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.get_auth_token():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Step 2: Test authentication requirement
        print("\n📋 Testing Authentication Requirements...")
        self.test_authentication_required()
        
        # Step 3: Create test data
        print("\n📋 Creating Test Data...")
        self.create_test_data()
        
        # Step 4: Test endpoints
        print("\n📋 Testing User-Specific Endpoints...")
        self.test_my_persons()
        self.test_my_vehicles() 
        self.test_my_images()
        
        # Step 5: Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
        
        return failed_tests == 0

def main():
    tester = UserSpecificEndpointsTest()
    success = tester.run_all_tests()
    
    # Save results to file
    results_file = "user_specific_endpoints_test_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'results': tester.test_results
        }, f, indent=2)
    
    print(f"\n📄 Test results saved to: {results_file}")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
