import { API_BASE_URL, API_ENDPOINTS } from './config';
import type { CreateRoomResponse, JoinRoomResponse, ApiResponse } from './types';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include', // Important for session-based auth
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async get<T>(endpoint: string, options: { params?: Record<string, any> } = {}): Promise<T> {
    const url = new URL(endpoint, this.baseUrl);
    
    if (options.params) {
      Object.entries(options.params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value));
      });
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
    });
  }

  // Room management methods
  async createRoom(accessToken?: string): Promise<CreateRoomResponse> {
    const body = accessToken ? { access_token: accessToken } : {};
    return this.post<CreateRoomResponse>(API_ENDPOINTS.createRoom, body);
  }

  async joinRoom(roomCode: string): Promise<JoinRoomResponse> {
    return this.post<JoinRoomResponse>(`${API_ENDPOINTS.joinRoom}/${roomCode}`);
  }

  // Spotify methods
  getSpotifyLoginUrl(): string {
    return `${this.baseUrl}${API_ENDPOINTS.spotifyLogin}`;
  }

  async getTopTracks(params: { limit?: number; time_range?: string } = {}): Promise<any> {
    const accessToken = localStorage.getItem('spotify_access_token');
    const body = accessToken ? { access_token: accessToken } : {};
    
    const url = new URL(API_ENDPOINTS.spotifyTopTracks, this.baseUrl);
    if (params.limit) url.searchParams.append('limit', String(params.limit));
    if (params.time_range) url.searchParams.append('time_range', params.time_range);

    const response = await fetch(url.toString(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async skipTrack(roomCode?: string): Promise<any> {
    const accessToken = localStorage.getItem('spotify_access_token');
    const body = accessToken 
      ? { access_token: accessToken, room_code: roomCode }
      : { room_code: roomCode };
    
    return this.post('/api/spotify/skip', body);
  }

  async getCurrentlyPlaying(): Promise<any> {
    const accessToken = localStorage.getItem('spotify_access_token');
    const body = accessToken ? { access_token: accessToken } : {};
    
    return this.post('/api/spotify/currently-playing', body);
  }

  async voteForSong(roomCode: string, trackId: string, trackName: string, trackArtist: string, trackUri: string): Promise<any> {
    const body = {
      track_id: trackId,
      track_name: trackName,
      track_artist: trackArtist,
      track_uri: trackUri,
      user_id: 'user_' + Date.now() // Simple user ID for demo
    };
    
    return this.post(`/api/vote/${roomCode}`, body);
  }

  async getVotes(roomCode: string): Promise<any> {
    return this.get(`/api/votes/${roomCode}`);
  }

  async startParty(trackUri: string, roomCode?: string): Promise<any> {
    const accessToken = localStorage.getItem('spotify_access_token');
    const body = accessToken 
      ? { access_token: accessToken, track_uri: trackUri, room_code: roomCode }
      : { track_uri: trackUri, room_code: roomCode };
    
    return this.post('/api/spotify/start-party', body);
  }
}

export const api = new ApiClient();
