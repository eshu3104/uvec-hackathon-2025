#!/usr/bin/env python3
"""
Test suite for room management functionality
"""
import unittest
import json
from unittest.mock import patch, MagicMock
from app import create_app
from routes.api import rooms, participants

class TestRoomManagement(unittest.TestCase):
    """Test cases for room management endpoints"""
    
    def setUp(self):
        """Set up test client and clear data"""
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Clear in-memory storage
        rooms.clear()
        participants.clear()
        
        # Mock Spotify authentication
        self.mock_spotify_auth = {
            'access_token': 'mock_access_token',
            'refresh_token': 'mock_refresh_token',
            'expires_in': 3600
        }
        
        self.mock_spotify_profile = {
            'id': 'test_spotify_user_id',
            'display_name': 'Test User',
            'email': 'test@example.com'
        }
        
        self.mock_playlist = {
            'id': 'test_playlist_id',
            'name': 'Party Room - TEST123',
            'external_urls': {
                'spotify': 'https://open.spotify.com/playlist/test_playlist_id'
            }
        }
    
    def tearDown(self):
        """Clean up after tests"""
        rooms.clear()
        participants.clear()
        self.app_context.pop()
    
    def test_create_room_success(self):
        """Test successful room creation"""
        with patch('routes.api.SpotifyOAuth') as mock_oauth_class:
            mock_oauth = MagicMock()
            mock_oauth_class.return_value = mock_oauth
            mock_oauth.is_token_valid.return_value = True
            mock_oauth.get_user_profile.return_value = self.mock_spotify_profile
            
            # Mock playlist creation
            with patch('requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = self.mock_playlist
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response
                
                # Mock session with Spotify token
                with self.client.session_transaction() as sess:
                    sess['spotify_access_token'] = 'mock_access_token'
                
                response = self.client.post('/api/create-room')
                
                self.assertEqual(response.status_code, 201)
                data = json.loads(response.data)
                
                # Verify response structure
                self.assertIn('message', data)
                self.assertIn('room_code', data)
                self.assertIn('room', data)
                self.assertIn('playlist', data)
                
                # Verify room was created
                room_code = data['room_code']
                self.assertIn(room_code, rooms)
                
                # Verify room data
                room = rooms[room_code]
                self.assertEqual(room['host_user_id'], 'test_spotify_user_id')
                self.assertEqual(room['host_display_name'], 'Test User')
                self.assertEqual(room['playlist_id'], 'test_playlist_id')
                self.assertEqual(room['status'], 'active')
                self.assertEqual(room['participant_count'], 1)
                
                # Verify host is added as participant
                self.assertIn(room_code, participants)
                self.assertEqual(len(participants[room_code]), 1)
                self.assertTrue(participants[room_code][0]['is_host'])
    
    def test_create_room_no_auth(self):
        """Test room creation without authentication"""
        response = self.client.post('/api/create-room')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Not authenticated', data['error'])
    
    def test_join_room_success(self):
        """Test successful room joining"""
        # First create a room
        room_code = 'TEST123'
        rooms[room_code] = {
            'code': room_code,
            'host_user_id': 'host_id',
            'host_display_name': 'Host User',
            'playlist_id': 'playlist_id',
            'playlist_url': 'https://spotify.com/playlist/playlist_id',
            'created_at': '2025-01-27T10:30:00Z',
            'status': 'active',
            'participant_count': 1
        }
        participants[room_code] = [{
            'user_id': 'host_id',
            'display_name': 'Host User',
            'joined_at': '2025-01-27T10:30:00Z',
            'is_host': True
        }]
        
        response = self.client.post(f'/api/join-room/{room_code}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify response
        self.assertIn('message', data)
        self.assertIn('participant', data)
        self.assertIn('room_info', data)
        
        # Verify participant was added
        self.assertEqual(len(participants[room_code]), 2)
        self.assertEqual(rooms[room_code]['participant_count'], 2)
        
        # Verify guest participant
        guest = participants[room_code][1]
        self.assertFalse(guest['is_host'])
        self.assertTrue(guest['user_id'].startswith('guest_'))
    
    def test_join_room_not_found(self):
        """Test joining non-existent room"""
        response = self.client.post('/api/join-room/NONEXIST')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Room not found', data['error'])
    
    def test_join_room_inactive(self):
        """Test joining inactive room"""
        room_code = 'TEST123'
        rooms[room_code] = {
            'code': room_code,
            'host_user_id': 'host_id',
            'host_display_name': 'Host User',
            'playlist_id': 'playlist_id',
            'playlist_url': 'https://spotify.com/playlist/playlist_id',
            'created_at': '2025-01-27T10:30:00Z',
            'status': 'ended',
            'participant_count': 0
        }
        
        response = self.client.post(f'/api/join-room/{room_code}')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Room is not active', data['error'])
    
    def test_get_room_status_success(self):
        """Test getting room status"""
        room_code = 'TEST123'
        rooms[room_code] = {
            'code': room_code,
            'host_user_id': 'host_id',
            'host_display_name': 'Host User',
            'playlist_id': 'playlist_id',
            'playlist_url': 'https://spotify.com/playlist/playlist_id',
            'created_at': '2025-01-27T10:30:00Z',
            'status': 'active',
            'participant_count': 2
        }
        participants[room_code] = [
            {
                'user_id': 'host_id',
                'display_name': 'Host User',
                'joined_at': '2025-01-27T10:30:00Z',
                'is_host': True
            },
            {
                'user_id': 'guest_1',
                'display_name': 'Guest 1',
                'joined_at': '2025-01-27T10:31:00Z',
                'is_host': False
            }
        ]
        
        response = self.client.get(f'/api/room/{room_code}/status')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify response structure
        self.assertIn('room', data)
        self.assertIn('participants', data)
        self.assertIn('participant_count', data)
        
        # Verify data
        self.assertEqual(data['participant_count'], 2)
        self.assertEqual(len(data['participants']), 2)
        self.assertEqual(data['room']['code'], room_code)
    
    def test_get_room_status_not_found(self):
        """Test getting status of non-existent room"""
        response = self.client.get('/api/room/NONEXIST/status')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Room not found', data['error'])
    
    def test_leave_room_success(self):
        """Test successful room leaving"""
        room_code = 'TEST123'
        rooms[room_code] = {
            'code': room_code,
            'host_user_id': 'host_id',
            'host_display_name': 'Host User',
            'playlist_id': 'playlist_id',
            'playlist_url': 'https://spotify.com/playlist/playlist_id',
            'created_at': '2025-01-27T10:30:00Z',
            'status': 'active',
            'participant_count': 2
        }
        participants[room_code] = [
            {
                'user_id': 'host_id',
                'display_name': 'Host User',
                'joined_at': '2025-01-27T10:30:00Z',
                'is_host': True
            },
            {
                'user_id': 'guest_1',
                'display_name': 'Guest 1',
                'joined_at': '2025-01-27T10:31:00Z',
                'is_host': False
            }
        ]
        
        response = self.client.post(
            f'/api/room/{room_code}/leave',
            json={'participant_id': 'guest_1'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify response
        self.assertIn('message', data)
        self.assertIn('participant_count', data)
        
        # Verify participant was removed
        self.assertEqual(len(participants[room_code]), 1)
        self.assertEqual(rooms[room_code]['participant_count'], 1)
    
    def test_leave_room_missing_participant_id(self):
        """Test leaving room without participant_id"""
        room_code = 'TEST123'
        rooms[room_code] = {
            'code': room_code,
            'host_user_id': 'host_id',
            'host_display_name': 'Host User',
            'playlist_id': 'playlist_id',
            'playlist_url': 'https://spotify.com/playlist/playlist_id',
            'created_at': '2025-01-27T10:30:00Z',
            'status': 'active',
            'participant_count': 1
        }
        
        # Test with empty JSON body
        response = self.client.post(
            f'/api/room/{room_code}/leave',
            json={}
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('participant_id is required', data['error'])
    
    def test_leave_room_participant_not_found(self):
        """Test leaving room with non-existent participant"""
        room_code = 'TEST123'
        rooms[room_code] = {
            'code': room_code,
            'host_user_id': 'host_id',
            'host_display_name': 'Host User',
            'playlist_id': 'playlist_id',
            'playlist_url': 'https://spotify.com/playlist/playlist_id',
            'created_at': '2025-01-27T10:30:00Z',
            'status': 'active',
            'participant_count': 1
        }
        participants[room_code] = [{
            'user_id': 'host_id',
            'display_name': 'Host User',
            'joined_at': '2025-01-27T10:30:00Z',
            'is_host': True
        }]
        
        response = self.client.post(
            f'/api/room/{room_code}/leave',
            json={'participant_id': 'non_existent'}
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Participant not found', data['error'])
    
    def test_end_room_success(self):
        """Test successful room ending by host"""
        room_code = 'TEST123'
        rooms[room_code] = {
            'code': room_code,
            'host_user_id': 'test_spotify_user_id',
            'host_display_name': 'Host User',
            'playlist_id': 'playlist_id',
            'playlist_url': 'https://spotify.com/playlist/playlist_id',
            'created_at': '2025-01-27T10:30:00Z',
            'status': 'active',
            'participant_count': 2
        }
        participants[room_code] = [
            {
                'user_id': 'test_spotify_user_id',
                'display_name': 'Host User',
                'joined_at': '2025-01-27T10:30:00Z',
                'is_host': True
            },
            {
                'user_id': 'guest_1',
                'display_name': 'Guest 1',
                'joined_at': '2025-01-27T10:31:00Z',
                'is_host': False
            }
        ]
        
        with patch('routes.api.SpotifyOAuth') as mock_oauth_class:
            mock_oauth = MagicMock()
            mock_oauth_class.return_value = mock_oauth
            mock_oauth.get_user_profile.return_value = self.mock_spotify_profile
            
            # Mock session with Spotify token
            with self.client.session_transaction() as sess:
                sess['spotify_access_token'] = 'mock_access_token'
            
            response = self.client.post(f'/api/room/{room_code}/end')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            # Verify response
            self.assertIn('message', data)
            self.assertIn('room_code', data)
            self.assertIn('ended_at', data)
            
            # Verify room was ended
            self.assertEqual(rooms[room_code]['status'], 'ended')
            self.assertIn('ended_at', rooms[room_code])
            
            # Verify participants were cleared
            self.assertNotIn(room_code, participants)
    
    def test_end_room_no_auth(self):
        """Test ending room without authentication"""
        room_code = 'TEST123'
        rooms[room_code] = {
            'code': room_code,
            'host_user_id': 'host_id',
            'host_display_name': 'Host User',
            'playlist_id': 'playlist_id',
            'playlist_url': 'https://spotify.com/playlist/playlist_id',
            'created_at': '2025-01-27T10:30:00Z',
            'status': 'active',
            'participant_count': 1
        }
        
        response = self.client.post(f'/api/room/{room_code}/end')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Authentication required', data['error'])
    
    def test_end_room_not_host(self):
        """Test ending room by non-host user"""
        room_code = 'TEST123'
        rooms[room_code] = {
            'code': room_code,
            'host_user_id': 'different_user_id',
            'host_display_name': 'Host User',
            'playlist_id': 'playlist_id',
            'playlist_url': 'https://spotify.com/playlist/playlist_id',
            'created_at': '2025-01-27T10:30:00Z',
            'status': 'active',
            'participant_count': 1
        }
        
        with patch('routes.api.SpotifyOAuth') as mock_oauth_class:
            mock_oauth = MagicMock()
            mock_oauth_class.return_value = mock_oauth
            mock_oauth.get_user_profile.return_value = self.mock_spotify_profile
            
            # Mock session with Spotify token
            with self.client.session_transaction() as sess:
                sess['spotify_access_token'] = 'mock_access_token'
            
            response = self.client.post(f'/api/room/{room_code}/end')
            
            self.assertEqual(response.status_code, 403)
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertIn('Only the host can end the room', data['error'])
    
    def test_room_code_generation_uniqueness(self):
        """Test that room codes are unique"""
        from routes.api import generate_room_code
        
        codes = set()
        for _ in range(100):  # Generate 100 codes
            code = generate_room_code()
            self.assertNotIn(code, codes)
            codes.add(code)
            self.assertEqual(len(code), 6)
            self.assertTrue(code.isalnum())
    
    def test_room_code_case_insensitive(self):
        """Test that room codes are case insensitive"""
        room_code = 'test123'
        rooms[room_code.upper()] = {
            'code': room_code.upper(),
            'host_user_id': 'host_id',
            'host_display_name': 'Host User',
            'playlist_id': 'playlist_id',
            'playlist_url': 'https://spotify.com/playlist/playlist_id',
            'created_at': '2025-01-27T10:30:00Z',
            'status': 'active',
            'participant_count': 1
        }
        
        # Test with lowercase
        response = self.client.post(f'/api/join-room/{room_code}')
        self.assertEqual(response.status_code, 200)
        
        # Test with mixed case
        response = self.client.post('/api/join-room/TeSt123')
        self.assertEqual(response.status_code, 200)
    
    def test_multiple_rooms_isolation(self):
        """Test that multiple rooms are properly isolated"""
        # Create two rooms
        room1_code = 'ROOM001'
        room2_code = 'ROOM002'
        
        rooms[room1_code] = {
            'code': room1_code,
            'host_user_id': 'host1',
            'host_display_name': 'Host 1',
            'playlist_id': 'playlist1',
            'playlist_url': 'https://spotify.com/playlist/playlist1',
            'created_at': '2025-01-27T10:30:00Z',
            'status': 'active',
            'participant_count': 1
        }
        
        rooms[room2_code] = {
            'code': room2_code,
            'host_user_id': 'host2',
            'host_display_name': 'Host 2',
            'playlist_id': 'playlist2',
            'playlist_url': 'https://spotify.com/playlist/playlist2',
            'created_at': '2025-01-27T10:31:00Z',
            'status': 'active',
            'participant_count': 1
        }
        
        participants[room1_code] = [{'user_id': 'host1', 'display_name': 'Host 1', 'joined_at': '2025-01-27T10:30:00Z', 'is_host': True}]
        participants[room2_code] = [{'user_id': 'host2', 'display_name': 'Host 2', 'joined_at': '2025-01-27T10:31:00Z', 'is_host': True}]
        
        # Join room 1
        response = self.client.post(f'/api/join-room/{room1_code}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(participants[room1_code]), 2)
        self.assertEqual(len(participants[room2_code]), 1)
        
        # Join room 2
        response = self.client.post(f'/api/join-room/{room2_code}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(participants[room1_code]), 2)
        self.assertEqual(len(participants[room2_code]), 2)
        
        # Verify isolation
        self.assertNotEqual(participants[room1_code], participants[room2_code])
        self.assertNotEqual(rooms[room1_code]['host_user_id'], rooms[room2_code]['host_user_id'])


if __name__ == '__main__':
    unittest.main()
