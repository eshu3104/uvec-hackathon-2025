import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Music, Search, Loader2 } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { API_ENDPOINTS } from "@/lib/config";
import { useToast } from "@/hooks/use-toast";

interface SpotifyTrack {
  id: string;
  name: string;
  artists: { name: string }[];
  album: {
    name: string;
    images: { url: string }[];
  };
}

const SelectSong = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const lobbyCode = location.state?.lobbyCode;
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSong, setSelectedSong] = useState<SpotifyTrack | null>(null);
  const [topTracks, setTopTracks] = useState<SpotifyTrack[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [initialLoad, setInitialLoad] = useState(true);

  // Load user's top tracks on mount
  useEffect(() => {
    const loadTopTracks = async () => {
      try {
        setIsLoading(true);
        const data = await api.get<{ items: SpotifyTrack[] }>(
          API_ENDPOINTS.spotifyTopTracks,
          { params: { limit: 5, time_range: 'short_term' } }
        );
        setTopTracks(data.items || []);
      } catch (error) {
        toast({
          title: "Error",
          description: error instanceof Error ? error.message : "Failed to load top tracks",
          variant: "destructive",
        });
        // If auth fails, redirect to login
        if (error instanceof Error && error.message.includes('auth')) {
          navigate('/login');
        }
      } finally {
        setIsLoading(false);
        setInitialLoad(false);
      }
    };

    loadTopTracks();
  }, [navigate, toast]);

  const displayedSongs = searchQuery
    ? topTracks.filter(
        (song) =>
          song.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          song.artists[0].name.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : topTracks;

  const handleContinue = () => {
    if (selectedSong) {
      navigate("/vote", { state: { lobbyCode, isHost: true, firstSong: selectedSong } });
    }
  };

  return (
    <div className="min-h-screen px-4 py-12">
      <div className="max-w-3xl mx-auto space-y-8 animate-fade-in">
        <div className="text-center">
          <h1 className="text-5xl font-bold mb-4">
            Let's get this party started! 🎵
          </h1>
          <p className="text-muted-foreground text-xl">
            Choose the first song to play
          </p>
        </div>

        {/* Search Bar */}
        <div className="glass-panel p-6 rounded-2xl">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-muted-foreground w-5 h-5" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search for a song..."
              className="pl-12 h-14 text-lg bg-background/50 border-primary/20 focus:border-primary"
            />
          </div>
        </div>

        {/* Song Recommendations */}
        {isLoading && initialLoad ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-12 h-12 text-primary animate-spin" />
          </div>
        ) : (
          <div className="space-y-4">
            {displayedSongs.length > 0 ? (
              displayedSongs.map((song) => (
                <div
                  key={song.id}
                  onClick={() => setSelectedSong(song)}
                  className={`glass-panel p-6 rounded-xl cursor-pointer transition-all hover:scale-102 ${
                    selectedSong?.id === song.id
                      ? "border-2 border-primary spotify-glow"
                      : "hover:bg-white/10"
                  }`}
                >
                  <div className="flex items-center gap-4">
                    {song.album.images[0] ? (
                      <img
                        src={song.album.images[0].url}
                        alt={song.album.name}
                        className="w-16 h-16 rounded-lg object-cover"
                      />
                    ) : (
                      <div className="w-16 h-16 bg-primary/20 rounded-lg flex items-center justify-center">
                        <Music className="w-8 h-8 text-primary" />
                      </div>
                    )}
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg">{song.name}</h3>
                      <p className="text-muted-foreground">{song.artists.map(a => a.name).join(', ')}</p>
                      <p className="text-sm text-muted-foreground">{song.album.name}</p>
                    </div>
                  </div>
                </div>
              ))
            ) : !searchQuery ? (
              <div className="text-center py-12 text-muted-foreground">
                <p>Start typing to search for songs</p>
                <p className="text-sm mt-2">or select from your top tracks below</p>
              </div>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                No songs found. Try a different search.
              </div>
            )}
          </div>
        )}

        {/* Continue Button */}
        {selectedSong && (
          <div className="flex justify-center animate-scale-in">
            <Button
              onClick={handleContinue}
              size="lg"
              className="text-xl px-12 py-6 bg-primary hover:bg-primary/90 spotify-glow"
            >
              Continue to Lobby
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SelectSong;
