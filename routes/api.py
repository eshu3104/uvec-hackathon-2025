from flask import Blueprint, jsonify, request, session, redirect, url_for
from datetime import datetime
import os
from utils.spotify_oauth import SpotifyOAuth

api_bp = Blueprint('api', __name__)

@api_bp.route('/status', methods=['GET'])
def get_status():
    """Get API status"""
    return jsonify({
        'status': 'active',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@api_bp.route('/users', methods=['GET'])
def get_users():
    """Get all users (placeholder)"""
    # This is a placeholder endpoint
    return jsonify({
        'users': [],
        'message': 'Users endpoint - implement your logic here'
    })

@api_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user (placeholder)"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # This is a placeholder endpoint
    return jsonify({
        'message': 'User creation endpoint - implement your logic here',
        'received_data': data
    }), 201

@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID (placeholder)"""
    return jsonify({
        'user_id': user_id,
        'message': 'Get user endpoint - implement your logic here'
    })

@api_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update a user by ID (placeholder)"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    return jsonify({
        'user_id': user_id,
        'message': 'Update user endpoint - implement your logic here',
        'received_data': data
    })

@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user by ID (placeholder)"""
    return jsonify({
        'message': f'User {user_id} deleted - implement your logic here'
    }), 200

# Spotify OAuth Routes
@api_bp.route('/spotify/login', methods=['GET'])
def spotify_login():
    """Initiate Spotify OAuth login"""
    try:
        spotify_oauth = SpotifyOAuth()
        auth_url = spotify_oauth.get_authorization_url()
        return redirect(auth_url)
    except ValueError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'Failed to initiate login: {str(e)}'}), 500

@api_bp.route('/spotify/callback', methods=['GET'])
def spotify_callback():
    """Handle Spotify OAuth callback"""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        return jsonify({'error': f'Spotify authorization failed: {error}'}), 400
    
    if not code:
        return jsonify({'error': 'No authorization code provided'}), 400
    
    try:
        spotify_oauth = SpotifyOAuth()
        token_data = spotify_oauth.get_access_token(code)
        
        # Store tokens in session
        session['spotify_access_token'] = token_data['access_token']
        session['spotify_refresh_token'] = token_data.get('refresh_token')
        session['spotify_token_expires_in'] = token_data.get('expires_in')
        
        return jsonify({
            'message': 'Successfully authenticated with Spotify',
            'access_token': token_data['access_token'],
            'expires_in': token_data.get('expires_in')
        })
    except Exception as e:
        return jsonify({'error': f'Failed to authenticate: {str(e)}'}), 500

@api_bp.route('/spotify/profile', methods=['GET'])
def spotify_profile():
    """Get user's Spotify profile"""
    access_token = session.get('spotify_access_token')
    
    if not access_token:
        return jsonify({'error': 'Not authenticated with Spotify'}), 401
    
    try:
        spotify_oauth = SpotifyOAuth()
        
        # Check if token is still valid, refresh if needed
        if not spotify_oauth.is_token_valid(access_token):
            refresh_token = session.get('spotify_refresh_token')
            if refresh_token:
                try:
                    token_data = spotify_oauth.refresh_access_token(refresh_token)
                    access_token = token_data['access_token']
                    session['spotify_access_token'] = access_token
                    if 'refresh_token' in token_data:
                        session['spotify_refresh_token'] = token_data['refresh_token']
                except:
                    return jsonify({'error': 'Session expired, please login again'}), 401
            else:
                return jsonify({'error': 'Session expired, please login again'}), 401
        
        profile = spotify_oauth.get_user_profile(access_token)
        return jsonify(profile)
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

@api_bp.route('/spotify/top-tracks', methods=['GET'])
def spotify_top_tracks():
    """Get user's top tracks"""
    access_token = session.get('spotify_access_token')
    
    if not access_token:
        return jsonify({'error': 'Not authenticated with Spotify'}), 401
    
    # Get query parameters
    time_range = request.args.get('time_range', 'medium_term')
    limit = request.args.get('limit', 20, type=int)
    
    # Validate parameters
    if time_range not in ['short_term', 'medium_term', 'long_term']:
        return jsonify({'error': 'Invalid time_range. Must be short_term, medium_term, or long_term'}), 400
    
    if limit < 1 or limit > 50:
        return jsonify({'error': 'Limit must be between 1 and 50'}), 400
    
    try:
        spotify_oauth = SpotifyOAuth()
        
        # Check if token is still valid, refresh if needed
        if not spotify_oauth.is_token_valid(access_token):
            refresh_token = session.get('spotify_refresh_token')
            if refresh_token:
                try:
                    token_data = spotify_oauth.refresh_access_token(refresh_token)
                    access_token = token_data['access_token']
                    session['spotify_access_token'] = access_token
                    if 'refresh_token' in token_data:
                        session['spotify_refresh_token'] = token_data['refresh_token']
                except:
                    return jsonify({'error': 'Session expired, please login again'}), 401
            else:
                return jsonify({'error': 'Session expired, please login again'}), 401
        
        top_tracks = spotify_oauth.get_top_tracks(access_token, time_range, limit)
        return jsonify(top_tracks)
    except Exception as e:
        return jsonify({'error': f'Failed to get top tracks: {str(e)}'}), 500

@api_bp.route('/spotify/recently-played', methods=['GET'])
def spotify_recently_played():
    """Get user's recently played tracks"""
    access_token = session.get('spotify_access_token')
    
    if not access_token:
        return jsonify({'error': 'Not authenticated with Spotify'}), 401
    
    # Get query parameters
    limit = request.args.get('limit', 20, type=int)
    
    # Validate parameters
    if limit < 1 or limit > 50:
        return jsonify({'error': 'Limit must be between 1 and 50'}), 400
    
    try:
        spotify_oauth = SpotifyOAuth()
        
        # Check if token is still valid, refresh if needed
        if not spotify_oauth.is_token_valid(access_token):
            refresh_token = session.get('spotify_refresh_token')
            if refresh_token:
                try:
                    token_data = spotify_oauth.refresh_access_token(refresh_token)
                    access_token = token_data['access_token']
                    session['spotify_access_token'] = access_token
                    if 'refresh_token' in token_data:
                        session['spotify_refresh_token'] = token_data['refresh_token']
                except:
                    return jsonify({'error': 'Session expired, please login again'}), 401
            else:
                return jsonify({'error': 'Session expired, please login again'}), 401
        
        recently_played = spotify_oauth.get_recently_played(access_token, limit)
        return jsonify(recently_played)
    except Exception as e:
        return jsonify({'error': f'Failed to get recently played tracks: {str(e)}'}), 500

@api_bp.route('/spotify/logout', methods=['POST'])
def spotify_logout():
    """Logout from Spotify (clear session)"""
    session.pop('spotify_access_token', None)
    session.pop('spotify_refresh_token', None)
    session.pop('spotify_token_expires_in', None)
    
    return jsonify({'message': 'Successfully logged out from Spotify'})
