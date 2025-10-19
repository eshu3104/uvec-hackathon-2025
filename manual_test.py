#!/usr/bin/env python3
"""
Manual test script for room management endpoints
Run this after starting your Flask server to test the API endpoints
"""
import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def print_response(response, title):
    """Print formatted response"""
    print(f"\n{'='*20} {title} {'='*20}")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_room_management():
    """Test room management endpoints"""
    print("🧪 Manual Testing of Room Management API")
    print("=" * 60)
    
    # Test 1: Create room (requires Spotify auth - will fail without it)
    print("\n1️⃣ Testing CREATE ROOM (requires Spotify authentication)")
    response = requests.post(f"{API_BASE}/create-room")
    print_response(response, "CREATE ROOM")
    
    if response.status_code == 401:
        print("❌ Authentication required - you need to login with Spotify first")
        print("   Go to: http://localhost:5000/api/spotify/login")
        return
    
    # If we get here, room was created successfully
    room_data = response.json()
    room_code = room_data['room_code']
    print(f"✅ Room created with code: {room_code}")
    
    # Test 2: Join room
    print(f"\n2️⃣ Testing JOIN ROOM: {room_code}")
    response = requests.post(f"{API_BASE}/join-room/{room_code}")
    print_response(response, "JOIN ROOM")
    
    # Test 3: Join room again (multiple participants)
    print(f"\n3️⃣ Testing JOIN ROOM AGAIN: {room_code}")
    response = requests.post(f"{API_BASE}/join-room/{room_code}")
    print_response(response, "JOIN ROOM AGAIN")
    
    # Test 4: Get room status
    print(f"\n4️⃣ Testing ROOM STATUS: {room_code}")
    response = requests.get(f"{API_BASE}/room/{room_code}/status")
    print_response(response, "ROOM STATUS")
    
    # Test 5: Test case insensitive room codes
    print(f"\n5️⃣ Testing CASE INSENSITIVE: {room_code.lower()}")
    response = requests.post(f"{API_BASE}/join-room/{room_code.lower()}")
    print_response(response, "CASE INSENSITIVE JOIN")
    
    # Test 6: Leave room
    if response.status_code == 200:
        join_data = response.json()
        participant_id = join_data['participant']['user_id']
        print(f"\n6️⃣ Testing LEAVE ROOM: {participant_id}")
        response = requests.post(
            f"{API_BASE}/room/{room_code}/leave",
            json={'participant_id': participant_id}
        )
        print_response(response, "LEAVE ROOM")
    
    # Test 7: Get room status after leaving
    print(f"\n7️⃣ Testing ROOM STATUS AFTER LEAVE: {room_code}")
    response = requests.get(f"{API_BASE}/room/{room_code}/status")
    print_response(response, "ROOM STATUS AFTER LEAVE")
    
    # Test 8: End room (requires host authentication)
    print(f"\n8️⃣ Testing END ROOM: {room_code}")
    response = requests.post(f"{API_BASE}/room/{room_code}/end")
    print_response(response, "END ROOM")
    
    # Test 9: Try to join ended room
    print(f"\n9️⃣ Testing JOIN ENDED ROOM: {room_code}")
    response = requests.post(f"{API_BASE}/join-room/{room_code}")
    print_response(response, "JOIN ENDED ROOM")
    
    # Test 10: Try to get status of ended room
    print(f"\n🔟 Testing STATUS OF ENDED ROOM: {room_code}")
    response = requests.get(f"{API_BASE}/room/{room_code}/status")
    print_response(response, "STATUS OF ENDED ROOM")

def test_error_cases():
    """Test error cases"""
    print("\n🚨 Testing Error Cases")
    print("=" * 40)
    
    # Test non-existent room
    print("\n1️⃣ Testing NON-EXISTENT ROOM")
    response = requests.post(f"{API_BASE}/join-room/NONEXIST")
    print_response(response, "NON-EXISTENT ROOM")
    
    # Test room status of non-existent room
    print("\n2️⃣ Testing STATUS OF NON-EXISTENT ROOM")
    response = requests.get(f"{API_BASE}/room/NONEXIST/status")
    print_response(response, "STATUS NON-EXISTENT")
    
    # Test leave room without participant_id
    print("\n3️⃣ Testing LEAVE WITHOUT PARTICIPANT_ID")
    response = requests.post(f"{API_BASE}/room/TEST123/leave")
    print_response(response, "LEAVE WITHOUT ID")

def test_spotify_endpoints():
    """Test Spotify endpoints (requires authentication)"""
    print("\n🎵 Testing Spotify Endpoints")
    print("=" * 40)
    
    # Test Spotify login
    print("\n1️⃣ Testing SPOTIFY LOGIN")
    response = requests.get(f"{API_BASE}/spotify/login", allow_redirects=False)
    print_response(response, "SPOTIFY LOGIN")
    
    # Test Spotify profile (will fail without auth)
    print("\n2️⃣ Testing SPOTIFY PROFILE")
    response = requests.get(f"{API_BASE}/spotify/profile")
    print_response(response, "SPOTIFY PROFILE")
    
    # Test Spotify playlists (will fail without auth)
    print("\n3️⃣ Testing SPOTIFY PLAYLISTS")
    response = requests.get(f"{API_BASE}/spotify/playlists")
    print_response(response, "SPOTIFY PLAYLISTS")

if __name__ == '__main__':
    print("🚀 Starting Manual API Tests")
    print("Make sure your Flask server is running on http://localhost:5000")
    print("=" * 60)
    
    try:
        # Test basic connectivity
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
        else:
            print("❌ Server responded with error")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Flask is running on localhost:5000")
        print("   Run: python3 run.py")
        exit(1)
    
    # Run tests
    test_room_management()
    test_error_cases()
    test_spotify_endpoints()
    
    print("\n" + "=" * 60)
    print("🏁 Manual testing complete!")
    print("\nTo test with Spotify authentication:")
    print("1. Go to: http://localhost:5000/api/spotify/login")
    print("2. Authenticate with Spotify")
    print("3. Run this script again")
