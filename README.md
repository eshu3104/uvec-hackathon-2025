# Flask Backend API

A Flask-based REST API backend for the UVEC Hackathon 2025 project..

## Project Structure

```
├── app.py                 # Main Flask application
├── run.py                 # Development server runner
├── requirements.txt       # Python dependencies
├── setup.sh              # Automated setup script
├── activate.sh            # Virtual environment activation script
├── .gitignore            # Git ignore file
├── venv/                 # Virtual environment (created by setup)
├── routes/               # API route blueprints
│   ├── __init__.py
│   └── api.py           # Main API routes
├── models/               # Data models
│   └── __init__.py
├── utils/                # Utility functions
│   └── __init__.py
└── tests/                # Test files
    ├── __init__.py
    └── test_app.py       # Application tests
```

## Setup

### Quick Setup (Recommended)
```bash
# Run the automated setup script
./setup.sh
```

### Manual Setup

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Create .env file with your configuration
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   HOST=0.0.0.0
   PORT=5000
   
   # Spotify OAuth Configuration (Required for Spotify integration)
   SPOTIFY_CLIENT_ID=your-spotify-client-id
   SPOTIFY_CLIENT_SECRET=your-spotify-client-secret
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:5000/api/spotify/callback
   ```

4. **Run the development server:**
   ```bash
   python run.py
   # or
   python app.py
   ```

### Convenience Scripts

- `./setup.sh` - Complete automated setup
- `./activate.sh` - Activate virtual environment and install dependencies

## API Endpoints

### General Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/status` - API status

### User Management
- `GET /api/users` - Get all users
- `POST /api/users` - Create a new user
- `GET /api/users/<id>` - Get user by ID
- `PUT /api/users/<id>` - Update user by ID
- `DELETE /api/users/<id>` - Delete user by ID

### Spotify OAuth Integration
- `GET /api/spotify/login` - Initiate Spotify OAuth login
- `GET /api/spotify/callback` - Handle Spotify OAuth callback
- `GET /api/spotify/profile` - Get user's Spotify profile
- `GET /api/spotify/top-tracks` - Get user's top tracks (supports time_range and limit params)
- `GET /api/spotify/recently-played` - Get user's recently played tracks (supports limit param)
- `POST /api/spotify/logout` - Logout from Spotify (clear session)

## Testing

Run tests with:
```bash
python -m pytest tests/
# or
python tests/test_app.py
```

## Development

The application uses:
- Flask 2.3.3
- Flask-CORS for cross-origin requests
- python-dotenv for environment variables
- requests for HTTP requests to Spotify API

## Spotify OAuth Setup

To use the Spotify integration features, you need to:

1. **Create a Spotify App:**
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Log in with your Spotify account
   - Click "Create App"
   - Fill in the app details (name, description)
   - Accept the terms and conditions

2. **Configure Redirect URI:**
   - In your Spotify app settings, add the redirect URI: `http://127.0.0.1:5000/api/spotify/callback`
   - For production, update the URI to match your domain

3. **Get Credentials:**
   - Copy your Client ID and Client Secret from the app settings
   - Add them to your `.env` file as `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`

4. **Required Scopes:**
   The integration requests the following Spotify scopes:
   - `user-read-private` - Read user's profile information
   - `user-read-email` - Read user's email address
   - `user-top-read` - Read user's top artists and tracks
   - `user-read-recently-played` - Read user's recently played tracks

## Production Deployment

For production, you can add Gunicorn to requirements.txt:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```
Repo for our submission for the UVEC Hackathon 2025
