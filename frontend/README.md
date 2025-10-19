# Party Room - Music Voting App

A real-time music voting application where users can create party lobbies and vote for songs to be added to a Spotify playlist.

## Features

- **Spotify Integration**: Connect with Spotify to create and manage playlists
- **Room Management**: Create unique lobby codes for friends to join
- **Real-time Voting**: Vote for songs to be added to the queue
- **Cross-platform**: Works on desktop and mobile devices

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui
- **Backend**: Flask, Python, Spotify Web API
- **Authentication**: Spotify OAuth 2.0

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- Python 3.8+
- Spotify Developer Account

### Installation

1. Clone the repository
2. Install frontend dependencies:

```bash
cd front-end-test
npm install
```

3. Install backend dependencies:

```bash
cd ..
source venv/bin/activate
pip install -r requirements.txt
```

### Development

1. Start the backend server:

```bash
source venv/bin/activate
python3 run.py
```

2. Start the frontend development server:

```bash
cd front-end-test
npm run dev
```

- Backend: http://localhost:5001
- Frontend: http://localhost:8080

### Building for Production

To build the frontend for production:

```bash
cd front-end-test
npm run build
```

The built files will be in the `dist` directory.

## Usage

1. **Create a Lobby**: Login with Spotify and create a party room
2. **Share Code**: Share the 6-character room code with friends
3. **Join Room**: Friends can join using the room code
4. **Vote for Songs**: Participants vote for songs to be added to the playlist
5. **Enjoy Music**: The most voted song gets added to the Spotify playlist

## API Endpoints

- `POST /api/create-room` - Create a new party room
- `POST /api/join-room/<code>` - Join an existing room
- `GET /api/room/<code>/status` - Get room status and participants
- `POST /api/room/<code>/leave` - Leave a room
- `POST /api/room/<code>/end` - End a room (host only)

## Spotify Integration

The app uses Spotify Web API for:
- User authentication via OAuth 2.0
- Creating and managing playlists
- Fetching user's top tracks and recently played songs

## License

MIT License