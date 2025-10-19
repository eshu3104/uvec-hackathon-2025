export interface SpotifyTrack {
  id: string;
  name: string;
  artists: { name: string }[];
  album: {
    name: string;
    images: { url: string }[];
  };
  external_urls: {
    spotify: string;
  };
}

export interface CreateRoomResponse {
  room_code: string;
  room_id: string;
  message: string;
}

export interface JoinRoomResponse {
  room_id: string;
  room_code: string;
  message: string;
  success: boolean;
}

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}
