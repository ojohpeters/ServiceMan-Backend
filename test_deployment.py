#!/usr/bin/env python3
"""
Test script for deployed API
Run this after deployment to verify everything works
"""

import requests
import json

# Update this URL with your deployed API URL
API_BASE_URL = "https://your-app-name.railway.app/api"

def test_endpoint(endpoint, method="GET", data=None):
    """Test an API endpoint"""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"✅ {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
            except:
                print(f"   Response: {response.text[:200]}...")
        else:
            print(f"   Error: {response.text}")
        
        print()
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ {method} {endpoint}")
        print(f"   Error: {str(e)}")
        print()
        return False

def main():
    print("🧪 Testing Serviceman Platform API")
    print(f"Base URL: {API_BASE_URL}")
    print("=" * 50)
    
    # Test public endpoints
    tests = [
        ("/services/categories/", "GET"),
        ("/users/create-test-servicemen/", "POST", {"category_id": 1}),
        ("/services/categories/1/servicemen/", "GET"),
        ("/ratings/", "GET"),
    ]
    
    passed = 0
    total = len(tests)
    
    for endpoint, method, *data in tests:
        data = data[0] if data else None
        if test_endpoint(endpoint, method, data):
            passed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Your API is ready for your friend!")
        print(f"\n🔗 API Base URL: {API_BASE_URL}")
        print(f"📚 API Documentation: {API_BASE_URL}/docs/")
        print(f"🔧 Admin Panel: {API_BASE_URL.replace('/api', '')}/admin/")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
