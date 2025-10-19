from flask import Blueprint, jsonify, request, session, redirect, url_for
from datetime import datetime
import os
import string
import random
from backend.utils.spotify_oauth import SpotifyOAuth
import traceback

api_bp = Blueprint('api', __name__)

# In-memory storage for rooms, participants, and votes
rooms = {}
participants = {}
votes = {}  # room_code -> {track_id: vote_count}

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

@api_bp.route('/spotify/top-tracks', methods=['GET', 'POST'])
def spotify_top_tracks():
    """Get user's top tracks"""
    print(f"Top tracks called - session data: {dict(session)}")
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
        
        print("Getting top tracks...")
        top_tracks = spotify_oauth.get_top_tracks(access_token, time_range, limit)
        return jsonify(top_tracks)
    except Exception as e:
        print(f"Error getting top tracks: {str(e)}")
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
    print(f"Join room called - room_code: {room_code}")
    print(f"Session data: {dict(session)}")
    print(f"Request cookies: {dict(request.cookies)}")
    print(f"Request headers: {dict(request.headers)}")
    
    try:
        room_code = room_code.upper()
        print(f"Looking for room: {room_code}")
        print(f"Available rooms: {list(rooms.keys())}")
        
        if room_code not in rooms:
            print(f"Room {room_code} not found")
            return jsonify({'error': 'Room not found'}), 404
        
        room = rooms[room_code]
        print(f"Found room: {room}")
        
        if room['status'] != 'active':
            print(f"Room {room_code} is not active, status: {room['status']}")
            return jsonify({'error': 'Room is not active'}), 400
        
        # Generate a simple participant ID (since non-Spotify users don't need accounts)
        participant_id = f"guest_{len(participants.get(room_code, [])) + 1}"
        print(f"Generated participant_id: {participant_id}")
        
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
        
        print(f"Successfully added participant: {participant}")
        print(f"Room now has {rooms[room_code]['participant_count']} participants")
        
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
        
    except Exception as e:
        print(f"Error joining room: {str(e)}")
        return jsonify({'error': f'Failed to join room: {str(e)}'}), 500

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

@api_bp.route('/spotify/currently-playing', methods=['GET', 'POST'])
def spotify_currently_playing():
    """Get currently playing track with full details"""
    print(f"Currently playing called - session data: {dict(session)}")
    print(f"Request cookies: {dict(request.cookies)}")
    print(f"Request headers: {dict(request.headers)}")
    
    # Try to get access token from request body first, then session
    if request.method == 'POST':
        data = request.get_json() or {}
        access_token = data.get('access_token') or session.get('spotify_access_token')
        print(f"Access token from request body: {data.get('access_token', 'None')[:20] if data.get('access_token') else 'None'}...")
    else:
        data = {}
        access_token = session.get('spotify_access_token')
        print(f"Access token from request body: None...")
    
    print(f"Access token from session: {session.get('spotify_access_token', 'None')[:20] if session.get('spotify_access_token') else 'None'}...")
    print(f"Final access token: {access_token[:20] if access_token else 'None'}...")
    
    if not access_token:
        print("No access token found in request body or session")
        return jsonify({'error': 'Not authenticated with Spotify'}), 401
    
    try:
        spotify_oauth = SpotifyOAuth()
        
        print("Getting currently playing track...")
        playback_state = spotify_oauth.get_playback_state(access_token)
        
        # If there's a currently playing track, get its full details
        if playback_state.get('item'):
            track = playback_state['item']
            # The track object already contains album images and other details
            print(f"Currently playing: {track.get('name', 'Unknown')} by {', '.join([artist['name'] for artist in track.get('artists', [])])}")
        
        return jsonify(playback_state)
    except Exception as e:
        print(f"Error getting currently playing: {str(e)}")
        return jsonify({'error': f'Failed to get currently playing: {str(e)}'}), 500

@api_bp.route('/spotify/play', methods=['POST'])
def spotify_play():
    """Play a track on user's Spotify"""
    print(f"Play track called - session data: {dict(session)}")
    print(f"Request cookies: {dict(request.cookies)}")
    print(f"Request headers: {dict(request.headers)}")
    
    # Try to get access token from request body first, then session
    data = request.get_json() or {}
    access_token = data.get('access_token') or session.get('spotify_access_token')
    track_uri = data.get('track_uri')
    
    print(f"Access token from request body: {data.get('access_token', 'None')[:20] if data.get('access_token') else 'None'}...")
    print(f"Access token from session: {session.get('spotify_access_token', 'None')[:20] if session.get('spotify_access_token') else 'None'}...")
    print(f"Final access token: {access_token[:20] if access_token else 'None'}...")
    print(f"Track URI: {track_uri}")
    
    if not access_token:
        print("No access token found in request body or session")
        return jsonify({'error': 'Not authenticated with Spotify'}), 401
    
    if not track_uri:
        return jsonify({'error': 'track_uri is required'}), 400
    
    try:
        spotify_oauth = SpotifyOAuth()
        
        print("Trying to add track to queue...")
        try:
            result = spotify_oauth.add_to_queue(access_token, track_uri)
            return jsonify({'message': 'Track added to queue successfully', 'result': result})
        except Exception as queue_error:
            print(f"Queue method failed: {str(queue_error)}")
            print("Trying direct playback method...")
            try:
                result = spotify_oauth.start_playback(access_token, track_uri)
                return jsonify({'message': 'Track playback started successfully', 'result': result})
            except Exception as playback_error:
                print(f"Playback method also failed: {str(playback_error)}")
                raise Exception(f"Both queue and playback methods failed. Queue error: {str(queue_error)}, Playback error: {str(playback_error)}")
    except Exception as e:
        print(f"Error playing track: {str(e)}")
        return jsonify({'error': f'Failed to play track: {str(e)}'}), 500

@api_bp.route('/spotify/start-party', methods=['POST'])
def spotify_start_party():
    """Stop current playback, add song to playlist, and start the party song"""
    print(f"Start party called - session data: {dict(session)}")
    print(f"Request cookies: {dict(request.cookies)}")
    print(f"Request headers: {dict(request.headers)}")
    
    # Try to get access token from request body first, then session
    data = request.get_json() or {}
    access_token = data.get('access_token') or session.get('spotify_access_token')
    track_uri = data.get('track_uri')
    room_code = data.get('room_code')
    
    print(f"Access token from request body: {data.get('access_token', 'None')[:20] if data.get('access_token') else 'None'}...")
    print(f"Access token from session: {session.get('spotify_access_token', 'None')[:20] if session.get('spotify_access_token') else 'None'}...")
    print(f"Final access token: {access_token[:20] if access_token else 'None'}...")
    print(f"Track URI: {track_uri}")
    print(f"Room code: {room_code}")
    
    if not access_token:
        print("No access token found in request body or session")
        return jsonify({'error': 'Not authenticated with Spotify'}), 401
    
    if not track_uri:
        return jsonify({'error': 'track_uri is required'}), 400
    
    try:
        spotify_oauth = SpotifyOAuth()
        
        # Add track to playlist if room_code is provided
        if room_code and room_code in rooms:
            playlist_id = rooms[room_code]['playlist_id']
            print(f"Adding track to playlist {playlist_id}...")
            try:
                spotify_oauth.add_tracks_to_playlist(access_token, playlist_id, [track_uri])
                print("Successfully added track to playlist")
            except Exception as playlist_error:
                print(f"Could not add track to playlist: {str(playlist_error)}")
        
        print("Pausing current playback...")
        try:
            spotify_oauth.pause_playback(access_token)
            print("Successfully paused current playback")
        except Exception as pause_error:
            print(f"Could not pause current playback (might not be playing): {str(pause_error)}")
        
        print("Starting party song...")
        result = spotify_oauth.start_playback(access_token, track_uri)
        return jsonify({'message': 'Party started successfully!', 'result': result})
    except Exception as e:
        print(f"Error starting party: {str(e)}")
        return jsonify({'error': f'Failed to start party: {str(e)}'}), 500

@api_bp.route('/spotify/skip', methods=['POST'])
def spotify_skip():
    """Skip to next track - play highest voted song if available"""
    print(f"Skip track called - session data: {dict(session)}")
    print(f"Request cookies: {dict(request.cookies)}")
    print(f"Request headers: {dict(request.headers)}")
    
    # Try to get access token from request body first, then session
    data = request.get_json() or {}
    access_token = data.get('access_token') or session.get('spotify_access_token')
    room_code = data.get('room_code')
    
    print(f"Access token from request body: {data.get('access_token', 'None')[:20] if data.get('access_token') else 'None'}...")
    print(f"Access token from session: {session.get('spotify_access_token', 'None')[:20] if session.get('spotify_access_token') else 'None'}...")
    print(f"Final access token: {access_token[:20] if access_token else 'None'}...")
    print(f"Room code: {room_code}")
    
    if not access_token:
        print("No access token found in request body or session")
        return jsonify({'error': 'Not authenticated with Spotify'}), 401
    
    try:
        spotify_oauth = SpotifyOAuth()
        
        # If room_code is provided, try to get the highest voted song
        print(f"Room code provided: {room_code}")
        print(f"Available rooms: {list(rooms.keys())}")
        print(f"Room exists: {room_code in rooms}")
        
        if room_code and room_code in rooms:
            print("Room found, checking for highest voted song...")
            
            # Get the highest voted song
            room_votes = votes.get(room_code, {})
            print(f"Room votes: {room_votes}")
            if room_votes:
                # Find the song with the highest vote count
                highest_voted = max(room_votes.items(), key=lambda x: x[1]['count'])
                track_id, vote_data = highest_voted
                track_uri = vote_data['track_uri']
                track_name = vote_data['track_name']
                vote_count = vote_data['count']
                
                print(f"Highest voted song: {track_name} with {vote_count} votes")
                
                # Add the highest voted song to the playlist
                playlist_id = rooms[room_code]['playlist_id']
                try:
                    spotify_oauth.add_tracks_to_playlist(access_token, playlist_id, [track_uri])
                    print(f"Added {track_name} to playlist")
                except Exception as e:
                    print(f"Could not add track to playlist: {str(e)}")
                
                # Start playing the highest voted song
                try:
                    result = spotify_oauth.start_playback(access_token, track_uri)
                    print(f"Started playing {track_name}")
                    return jsonify({
                        'message': f'Playing highest voted song: {track_name}',
                        'track_name': track_name,
                        'vote_count': vote_count,
                        'result': result
                    })
                except Exception as e:
                    print(f"Could not start playback: {str(e)}")
                    # Fallback to normal skip
                    result = spotify_oauth.skip_to_next(access_token)
                    return jsonify({'message': 'Skipped to next track successfully', 'result': result})
            else:
                print("No votes found, skipping to next track normally...")
                result = spotify_oauth.skip_to_next(access_token)
                return jsonify({'message': 'Skipped to next track successfully', 'result': result})
        else:
            print("No room code provided, skipping to next track normally...")
            result = spotify_oauth.skip_to_next(access_token)
            return jsonify({'message': 'Skipped to next track successfully', 'result': result})
            
    except Exception as e:
        print(f"Error skipping track: {str(e)}")
        return jsonify({'error': f'Failed to skip track: {str(e)}'}), 500

@api_bp.route('/vote/<room_code>', methods=['POST'])
def vote_for_song(room_code):
    """Vote for a song in a room"""
    print(f"Vote called - room_code: {room_code}")
    print(f"Session data: {dict(session)}")
    print(f"Request cookies: {dict(request.cookies)}")
    print(f"Request headers: {dict(request.headers)}")
    
    data = request.get_json() or {}
    track_id = data.get('track_id')
    track_name = data.get('track_name')
    track_artist = data.get('track_artist')
    track_uri = data.get('track_uri')
    user_id = data.get('user_id', 'anonymous')
    
    print(f"Vote data: track_id={track_id}, track_name={track_name}, user_id={user_id}")
    
    if not track_id:
        return jsonify({'error': 'track_id is required'}), 400
    
    if room_code not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    
    # Initialize votes for this room if not exists
    if room_code not in votes:
        votes[room_code] = {}
    
    # Initialize track vote count if not exists
    if track_id not in votes[room_code]:
        votes[room_code][track_id] = {
            'count': 0,
            'track_name': track_name,
            'track_artist': track_artist,
            'track_uri': track_uri,
            'voters': []
        }
    
    # Add vote
    votes[room_code][track_id]['count'] += 1
    votes[room_code][track_id]['voters'].append(user_id)
    
    print(f"Vote added. Total votes for {track_name}: {votes[room_code][track_id]['count']}")
    
    return jsonify({
        'message': 'Vote recorded successfully',
        'track_id': track_id,
        'vote_count': votes[room_code][track_id]['count']
    })

@api_bp.route('/votes/<room_code>', methods=['GET'])
def get_votes(room_code):
    """Get all votes for a room"""
    print(f"Get votes called - room_code: {room_code}")
    
    if room_code not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    
    room_votes = votes.get(room_code, {})
    
    # Convert to list format for frontend
    vote_list = []
    for track_id, vote_data in room_votes.items():
        vote_list.append({
            'id': track_id,
            'title': vote_data['track_name'],
            'artist': vote_data['track_artist'],
            'uri': vote_data['track_uri'],
            'votes': vote_data['count']
        })
    
    # Sort by vote count (highest first)
    vote_list.sort(key=lambda x: x['votes'], reverse=True)
    
    return jsonify({
        'votes': vote_list
    })

@api_bp.route('/debug/rooms', methods=['GET'])
def debug_rooms():
    """Debug endpoint to check rooms and votes"""
    return jsonify({
        'rooms': list(rooms.keys()),
        'votes': {room: list(votes.get(room, {}).keys()) for room in rooms.keys()}
    })

@api_bp.route('/spotify/logout', methods=['POST'])
def spotify_logout():
    """Logout from Spotify (clear session)"""
    session.pop('spotify_access_token', None)
    session.pop('spotify_refresh_token', None)
    session.pop('spotify_token_expires_in', None)
    
    return jsonify({'message': 'Successfully logged out from Spotify'})