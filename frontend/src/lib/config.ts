export const API_ENDPOINTS = {
  spotifyTopTracks: '/api/spotify/top-tracks',
  spotifySearch: '/api/spotify/search',
  createRoom: '/api/create-room',
  joinRoom: '/api/join-room',
  spotifyLogin: '/api/spotify/login',
} as const;

export const API_BASE_URL = 'http://localhost:5000';
