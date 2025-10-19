#!/usr/bin/env python3
"""
Integration test to verify frontend-backend connectivity
"""
import requests
import json
import time

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get('http://localhost:5001/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend Health Check:")
            print(f"   Status: {data['status']}")
            print(f"   Message: {data['message']}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def test_api_status():
    """Test API status endpoint"""
    try:
        response = requests.get('http://localhost:5001/api/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API Status Check:")
            print(f"   Status: {data['status']}")
            print(f"   Version: {data['version']}")
            return True
        else:
            print(f"❌ API status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API status check error: {e}")
        return False

def test_spotify_login_redirect():
    """Test Spotify login redirect"""
    try:
        response = requests.get('http://localhost:5001/api/spotify/login', allow_redirects=False, timeout=5)
        if response.status_code == 302:
            print("✅ Spotify Login Redirect:")
            print(f"   Redirects to: {response.headers.get('Location', 'Unknown')}")
            return True
        else:
            print(f"❌ Spotify login redirect failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Spotify login redirect error: {e}")
        return False

def test_room_endpoints():
    """Test room management endpoints (without auth)"""
    endpoints = [
        ('/api/create-room', 'POST'),
        ('/api/join-room/TEST123', 'POST'),
        ('/api/room/TEST123/status', 'GET'),
    ]
    
    print("✅ Room Endpoints Test:")
    for endpoint, method in endpoints:
        try:
            if method == 'GET':
                response = requests.get(f'http://localhost:5001{endpoint}', timeout=5)
            else:
                response = requests.post(f'http://localhost:5001{endpoint}', timeout=5)
            
            if response.status_code == 401:
                print(f"   ✅ {method} {endpoint} - Returns 401 (auth required) ✓")
            elif response.status_code == 404:
                print(f"   ✅ {method} {endpoint} - Returns 404 (not found) ✓")
            else:
                print(f"   ⚠️  {method} {endpoint} - Returns {response.status_code}")
        except Exception as e:
            print(f"   ❌ {method} {endpoint} - Error: {e}")

def test_frontend_connectivity():
    """Test if frontend is accessible"""
    try:
        response = requests.get('http://localhost:8080', timeout=5)
        if response.status_code == 200:
            print("✅ Frontend Server:")
            print("   React app is running on port 8080")
            return True
        else:
            print(f"❌ Frontend server returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend server not accessible: {e}")
        print("   Make sure to run: cd front-end-test && npm run dev")
        return False

def main():
    print("🧪 Frontend-Backend Integration Test")
    print("=" * 50)
    
    # Test backend
    backend_ok = test_backend_health()
    api_ok = test_api_status()
    spotify_ok = test_spotify_login_redirect()
    
    print()
    test_room_endpoints()
    
    print()
    frontend_ok = test_frontend_connectivity()
    
    print()
    print("=" * 50)
    print("📊 Integration Test Summary:")
    print(f"   Backend Health: {'✅' if backend_ok else '❌'}")
    print(f"   API Status: {'✅' if api_ok else '❌'}")
    print(f"   Spotify OAuth: {'✅' if spotify_ok else '❌'}")
    print(f"   Frontend Server: {'✅' if frontend_ok else '❌'}")
    
    if backend_ok and api_ok and spotify_ok:
        print("\n🎉 Backend integration is working correctly!")
        print("   You can now test the full flow:")
        print("   1. Go to http://localhost:8080")
        print("   2. Click 'Create Lobby'")
        print("   3. Login with Spotify")
        print("   4. Create a room and test joining")
    else:
        print("\n❌ Some integration tests failed. Check the errors above.")

if __name__ == '__main__':
    main()
