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
        self.scope = 'user-read-private user-read-email user-top-read user-read-recently-played'
        
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
    
    def is_token_valid(self, access_token):
        """Check if access token is valid by making a simple API call"""
        try:
            self.get_user_profile(access_token)
            return True
        except:
            return False
