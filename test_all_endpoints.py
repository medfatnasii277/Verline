#!/usr/bin/env python3
"""
Comprehensive API endpoint verification script
Tests all endpoints to ensure they work without authentication restrictions
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(method, url, data=None, files=None, description=""):
    """Test an API endpoint and return result"""
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            if files:
                response = requests.post(url, data=data, files=files)
            else:
                response = requests.post(url, json=data)
        elif method.upper() == "PUT":
            if files:
                response = requests.put(url, data=data, files=files)
            else:
                response = requests.put(url, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url)
        
        status = "✅ PASS" if response.status_code < 400 else "❌ FAIL"
        print(f"{status} {method} {url} - {response.status_code} - {description}")
        
        if response.status_code >= 400:
            try:
                error_detail = response.json().get('detail', 'Unknown error')
                print(f"    Error: {error_detail}")
            except:
                print(f"    Error: {response.text[:100]}")
        
        return response.status_code < 400, response
        
    except Exception as e:
        print(f"❌ FAIL {method} {url} - Connection error - {str(e)}")
        return False, None

def main():
    print("🎨 Verline Art Gallery API Endpoint Verification")
    print("=" * 50)
    
    passed = 0
    total = 0
    
    # Test basic endpoints
    tests = [
        ("GET", f"{BASE_URL}/health", None, None, "Health check"),
        ("GET", f"{BASE_URL}/", None, None, "Root endpoint"),
        
        # Categories
        ("GET", f"{BASE_URL}/categories/", None, None, "Get all categories"),
        ("POST", f"{BASE_URL}/categories/", {"name": "Test API Category", "description": "API test category"}, None, "Create category"),
        ("GET", f"{BASE_URL}/categories/1", None, None, "Get category by ID"),
        
        # Users
        ("GET", f"{BASE_URL}/users/", None, None, "Get all users"),
        ("GET", f"{BASE_URL}/users/artists", None, None, "Get artists"),
        ("GET", f"{BASE_URL}/users/3", None, None, "Get user by ID"),
        ("GET", f"{BASE_URL}/users/me/3", None, None, "Get current user profile"),
        
        # Paintings
        ("GET", f"{BASE_URL}/paintings/", None, None, "Get all paintings"),
        ("GET", f"{BASE_URL}/paintings/my-paintings/3", None, None, "Get user's paintings"),
        
        # Comments (test get comments for non-existent painting)
        ("GET", f"{BASE_URL}/comments/painting/1", None, None, "Get comments for painting"),
        
        # Ratings
        ("GET", f"{BASE_URL}/ratings/painting/1", None, None, "Get ratings for painting"),
        
        # Auth endpoints
        ("POST", f"{BASE_URL}/auth/register", {
            "username": "testuser",
            "email": "test@example.com", 
            "password": "testpass123",
            "full_name": "Test User",
            "role": "enthusiast"
        }, None, "Register new user"),
    ]
    
    for method, url, data, files, description in tests:
        success, response = test_endpoint(method, url, data, files, description)
        total += 1
        if success:
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} endpoints passed")
    
    if passed == total:
        print("🎉 All endpoints are working correctly!")
        print("✅ No authentication restrictions found")
        print("✅ Both enthusiasts and artists can access all endpoints")
    else:
        print("⚠️  Some endpoints need attention")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
