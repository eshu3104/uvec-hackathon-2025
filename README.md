# Flask Backend API

A Flask-based REST API backend for the UVEC Hackathon 2025 project.

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

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/status` - API status
- `GET /api/users` - Get all users
- `POST /api/users` - Create a new user
- `GET /api/users/<id>` - Get user by ID
- `PUT /api/users/<id>` - Update user by ID
- `DELETE /api/users/<id>` - Delete user by ID

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

## Production Deployment

For production, you can add Gunicorn to requirements.txt:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```
Repo for our submission for the UVEC Hackathon 2025
