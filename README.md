# Party Music App

A collaborative music party app where users can create rooms, vote on songs, and control the playlist together.

## Project Structure

```
├── backend/           # Flask backend API
│   ├── routes/       # API routes
│   └── utils/        # Utility functions (Spotify OAuth)
├── frontend/         # React frontend
└── venv/            # Python virtual environment
```

## Quick Start

### Backend
```bash
source venv/bin/activate
python run.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Features

- Spotify OAuth authentication
- Create/join party rooms
- Collaborative playlist creation
- Song voting system
- Real-time updates

## Environment Variables

Create a `.env` file with:
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:5000/api/spotify/callback
SECRET_KEY=your_secret_key
```
