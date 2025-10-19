from flask import Blueprint, jsonify, request, session, redirect, url_for
from datetime import datetime
import os
import string
import random
from utils.spotify_oauth import SpotifyOAuth
import traceback

api_bp = Blueprint('api', __name__)

# In-memory storage for rooms
rooms = {}
participants = {}

@api_bp.before_request
def show_session():
    print(dict(session))

def generate_room_code():
    """Generate a unique 6-character alphanumeric room code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if code not in rooms:
            return code

def create_spotify_playlist(access_token, room_code):
    """Create a Spotify playlist for the room"""
    try:
        spotify_oauth = SpotifyOAuth()
        
        # Get user profile to get user ID
        profile = spotify_oauth.get_user_profile(access_token)
        user_id = profile['id']
        
        # Create playlist
        url = f'https://api.spotify.com/v1/users/{user_id}/playlists'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        playlist_data = {
            'name': f'Party Room - {room_code}',
            'description': f'Collaborative playlist for party room {room_code}',
            'public': False
        }
        
        import requests
        response = requests.post(url, headers=headers, json=playlist_data)
        response.raise_for_status()
        return response.json()
        
    except Exception as e:
        raise Exception(f"Failed to create Spotify playlist: {str(e)}")

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
    
    print(f"Spotify callback received - code: {code[:20] if code else None}..., error: {error}")
    
    if error:
        return jsonify({'error': f'Spotify authorization failed: {error}'}), 400
    
    if not code:
        return jsonify({'error': 'No authorization code provided'}), 400
    
    try:
        spotify_oauth = SpotifyOAuth()
        token_data = spotify_oauth.get_access_token(code)
        
        print(f"Token data received: {list(token_data.keys())}")
        
        # Store tokens in session (for backward compatibility)
        session['spotify_access_token'] = token_data['access_token']
        session['spotify_refresh_token'] = token_data.get('refresh_token')
        session['spotify_token_expires_in'] = token_data.get('expires_in')
        
        print(f"Session after storing tokens: {dict(session)}")
        print(f"Session ID: {session.get('_id', 'No session ID')}")
        
        # Force session to be saved
        session.permanent = True
        session.modified = True
        
        # Redirect to frontend callback page with tokens as URL parameters
        redirect_url = f"http://localhost:8080/callback?access_token={token_data['access_token']}&refresh_token={token_data.get('refresh_token', '')}&expires_in={token_data.get('expires_in', 3600)}"
        return redirect(redirect_url)
    except Exception as e:
        print(f"Error in Spotify callback: {str(e)}")
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

@api_bp.route('/spotify/playlists', methods=['GET'])
def spotify_playlists():
    """Get user's playlists"""
    access_token = session.get('spotify_access_token')
    
    if not access_token:
        return jsonify({'error': 'Not authenticated with Spotify'}), 401
    
    # Get query parameters
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Validate parameters
    if limit < 1 or limit > 50:
        return jsonify({'error': 'Limit must be between 1 and 50'}), 400
    
    if offset < 0:
        return jsonify({'error': 'Offset must be 0 or greater'}), 400
    
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
        
        playlists = spotify_oauth.get_user_playlists(access_token, limit, offset)
        return jsonify(playlists)
    except Exception as e:
        return jsonify({'error': f'Failed to get playlists: {str(e)}'}), 500

# Room Management Endpoints
@api_bp.route('/create-room', methods=['POST'])
def create_room():
    """Create a new party room with unique code"""
    print(f"Create room called - session data: {dict(session)}")
    print(f"Request cookies: {dict(request.cookies)}")
    print(f"Request headers: {dict(request.headers)}")
    
    # Try to get access token from request body first, then session
    data = request.get_json() or {}
    access_token = data.get('access_token') or session.get('spotify_access_token')
    
    print(f"Access token from request body: {data.get('access_token', 'None')[:20] if data.get('access_token') else 'None'}...")
    print(f"Access token from session: {session.get('spotify_access_token', 'None')[:20] if session.get('spotify_access_token') else 'None'}...")
    print(f"Final access token: {access_token[:20] if access_token else 'None'}...")
    
    if not access_token:
        print("No access token found in request body or session")
        return jsonify({'error': 'Not authenticated with Spotify'}), 401
    
    try:
        spotify_oauth = SpotifyOAuth()
        
        print("Starting room creation process...")
        
        # Generate unique room code
        room_code = generate_room_code()
        print(f"Generated room code: {room_code}")
        
        # Get user profile
        print("Getting user profile...")
        profile = spotify_oauth.get_user_profile(access_token)
        host_user_id = profile['id']
        host_display_name = profile['display_name']
        print(f"User profile: {host_display_name} ({host_user_id})")
        
        # Create Spotify playlist
        print("Creating Spotify playlist...")
        playlist = create_spotify_playlist(access_token, room_code)
        print(f"Playlist created: {playlist['name']}")
        
        # Create room
        room = {
            'code': room_code,
            'host_user_id': host_user_id,
            'host_display_name': host_display_name,
            'playlist_id': playlist['id'],
            'playlist_url': playlist['external_urls']['spotify'],
            'created_at': datetime.utcnow().isoformat(),
            'status': 'active',
            'participant_count': 1
        }
        
        rooms[room_code] = room
        
        # Add host as first participant
        participants[room_code] = [{
            'user_id': host_user_id,
            'display_name': host_display_name,
            'joined_at': datetime.utcnow().isoformat(),
            'is_host': True
        }]
        
        return jsonify({
            'message': 'Room created successfully',
            'room_code': room_code,
            'room': room,
            'playlist': {
                'id': playlist['id'],
                'name': playlist['name'],
                'url': playlist['external_urls']['spotify']
            }
        }), 201
        
    except Exception as e:
        print(f"Error in create_room: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Failed to create room: {str(e)}'}), 500

@api_bp.route('/join-room/<room_code>', methods=['POST'])
def join_room(room_code):
    """Join an existing room"""
    room_code = room_code.upper()
    
    if room_code not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    
    room = rooms[room_code]
    
    if room['status'] != 'active':
        return jsonify({'error': 'Room is not active'}), 400
    
    # Generate a simple participant ID (since non-Spotify users don't need accounts)
    participant_id = f"guest_{len(participants.get(room_code, [])) + 1}"
    
    # Add participant
    if room_code not in participants:
        participants[room_code] = []
    
    participant = {
        'user_id': participant_id,
        'display_name': f"Guest {len(participants[room_code])}",
        'joined_at': datetime.utcnow().isoformat(),
        'is_host': False
    }
    
    participants[room_code].append(participant)
    rooms[room_code]['participant_count'] = len(participants[room_code])
    
    return jsonify({
        'message': 'Successfully joined room',
        'room_code': room_code,
        'participant': participant,
        'room_info': {
            'code': room['code'],
            'host': room['host_display_name'],
            'participant_count': room['participant_count'],
            'created_at': room['created_at']
        }
    }), 200

@api_bp.route('/room/<room_code>/status', methods=['GET'])
def get_room_status(room_code):
    """Get room status and participants"""
    room_code = room_code.upper()
    
    if room_code not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    
    room = rooms[room_code]
    room_participants = participants.get(room_code, [])
    
    return jsonify({
        'room': room,
        'participants': room_participants,
        'participant_count': len(room_participants)
    })

@api_bp.route('/room/<room_code>/leave', methods=['POST'])
def leave_room(room_code):
    """Leave a room"""
    room_code = room_code.upper()
    
    if room_code not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    
    # Get participant info from request body
    data = request.get_json() or {}
    participant_id = data.get('participant_id')
    
    if not participant_id:
        return jsonify({'error': 'participant_id is required'}), 400
    
    if room_code not in participants:
        return jsonify({'error': 'No participants in room'}), 400
    
    # Remove participant
    room_participants = participants[room_code]
    participant_found = False
    
    for i, participant in enumerate(room_participants):
        if participant['user_id'] == participant_id:
            del room_participants[i]
            participant_found = True
            break
    
    if not participant_found:
        return jsonify({'error': 'Participant not found in room'}), 404
    
    # Update room participant count
    rooms[room_code]['participant_count'] = len(room_participants)
    
    return jsonify({
        'message': 'Successfully left room',
        'participant_count': len(room_participants)
    })

@api_bp.route('/room/<room_code>/end', methods=['POST'])
def end_room(room_code):
    """Host ends the room"""
    room_code = room_code.upper()
    
    if room_code not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    
    # Check if user is authenticated and is the host
    access_token = session.get('spotify_access_token')
    if not access_token:
        return jsonify({'error': 'Authentication required to end room'}), 401
    
    try:
        spotify_oauth = SpotifyOAuth()
        profile = spotify_oauth.get_user_profile(access_token)
        user_id = profile['id']
        
        room = rooms[room_code]
        if room['host_user_id'] != user_id:
            return jsonify({'error': 'Only the host can end the room'}), 403
        
        # End the room
        rooms[room_code]['status'] = 'ended'
        rooms[room_code]['ended_at'] = datetime.utcnow().isoformat()
        
        # Clear participants
        if room_code in participants:
            del participants[room_code]
        
        return jsonify({
            'message': 'Room ended successfully',
            'room_code': room_code,
            'ended_at': rooms[room_code]['ended_at']
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to end room: {str(e)}'}), 500

@api_bp.route('/spotify/logout', methods=['POST'])
def spotify_logout():
    """Logout from Spotify (clear session)"""
    session.pop('spotify_access_token', None)
    session.pop('spotify_refresh_token', None)
    session.pop('spotify_token_expires_in', None)
    
    return jsonify({'message': 'Successfully logged out from Spotify'})