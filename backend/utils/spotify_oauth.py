import os
import requests
import base64
from urllib.parse import urlencode
from flask import session, redirect, request
import json

class SpotifyOAuth:
    def __init__(self):
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:5000/api/spotify/callback')
        self.scope = 'user-read-private user-read-email user-top-read user-read-recently-played playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative user-read-playback-state user-modify-playback-state user-read-currently-playing streaming app-remote-control'
        
        if not self.client_id or not self.client_secret:
            raise ValueError("SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables are required")
    
    def get_authorization_url(self):
        """Generate Spotify authorization URL"""
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'show_dialog': 'true'
        }
        
        auth_url = 'https://accounts.spotify.com/authorize?' + urlencode(params)
        return auth_url
    
    def get_access_token(self, code):
        """Exchange authorization code for access token"""
        token_url = 'https://accounts.spotify.com/api/token'
        
        # Prepare the request
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode('utf-8')
        auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        
        try:
            response = requests.post(token_url, headers=headers, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get access token: {str(e)}")
    
    def refresh_access_token(self, refresh_token):
        """Refresh access token using refresh token"""
        token_url = 'https://accounts.spotify.com/api/token'
        
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode('utf-8')
        auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        try:
            response = requests.post(token_url, headers=headers, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to refresh access token: {str(e)}")
    
    def get_user_profile(self, access_token):
        """Get user profile information"""
        url = 'https://api.spotify.com/v1/me'
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get user profile: {str(e)}")
    
    def get_top_tracks(self, access_token, time_range='medium_term', limit=20):
        """Get user's top tracks"""
        url = 'https://api.spotify.com/v1/me/top/tracks'
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            'time_range': time_range,  # short_term, medium_term, long_term
            'limit': limit
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get top tracks: {str(e)}")
    
    def get_recently_played(self, access_token, limit=20):
        """Get user's recently played tracks"""
        url = 'https://api.spotify.com/v1/me/player/recently-played'
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {'limit': limit}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get recently played tracks: {str(e)}")
    
    def get_user_playlists(self, access_token, limit=20, offset=0):
        """Get user's playlists"""
        url = 'https://api.spotify.com/v1/me/playlists'
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            'limit': limit,
            'offset': offset
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get user playlists: {str(e)}")
    
    def create_playlist(self, access_token, user_id, name, description="", public=True):
        """Create a new playlist"""
        url = f'https://api.spotify.com/v1/users/{user_id}/playlists'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        data = {
            'name': name,
            'description': description,
            'public': public
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create playlist: {str(e)}")
    
    def add_tracks_to_playlist(self, access_token, playlist_id, track_uris):
        """Add tracks to a playlist"""
        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        data = {'uris': track_uris}
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to add tracks to playlist: {str(e)}")
    
    def get_playback_state(self, access_token):
        """Get current playback state"""
        url = 'https://api.spotify.com/v1/me/player'
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get playback state: {str(e)}")
    
    def add_to_queue(self, access_token, track_uri):
        """Add a track to the queue"""
        url = 'https://api.spotify.com/v1/me/player/queue'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        params = {'uri': track_uri}
        
        try:
            response = requests.post(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to add track to queue: {str(e)}")
    
    def start_playback(self, access_token, track_uri=None, device_id=None):
        """Start playback of a track"""
        url = 'https://api.spotify.com/v1/me/player/play'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {}
        if track_uri:
            data['uris'] = [track_uri]
        if device_id:
            data['device_id'] = device_id
        
        try:
            response = requests.put(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to start playback: {str(e)}")
    
    def pause_playback(self, access_token):
        """Pause current playback"""
        url = 'https://api.spotify.com/v1/me/player/pause'
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = requests.put(url, headers=headers)
            response.raise_for_status()
            # Spotify pause endpoint returns empty response on success
            if response.status_code == 204 or not response.content.strip():
                return {'success': True}
            else:
                try:
                    return response.json()
                except:
                    return {'success': True}
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to pause playback: {str(e)}")
    
    def skip_to_next(self, access_token):
        """Skip to next track"""
        url = 'https://api.spotify.com/v1/me/player/next'
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            # Spotify skip endpoint returns empty response on success
            if response.status_code == 204 or not response.content.strip():
                return {'success': True}
            else:
                try:
                    return response.json()
                except:
                    return {'success': True}
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to skip to next track: {str(e)}")
    
    def is_token_valid(self, access_token):
        """Check if access token is valid by making a simple API call"""
        try:
            self.get_user_profile(access_token)
            return True
        except:
            return False
