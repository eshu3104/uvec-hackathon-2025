import { Button } from "@/components/ui/button";
import { Music, LogOut, Copy, Check, SkipForward } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

// Mock recommendations for demo - using real Spotify track URIs
const mockRecommendations = [
  { id: "1", title: "Shake It Off", artist: "Taylor Swift", votes: 0, uri: "spotify:track:nfWTPCe119PGpuFelhQG7" },
  { id: "2", title: "Levitating", artist: "Dua Lipa", votes: 0, uri: "spotify:track:39LLxExYz6ewLAcYrzQQyP" },
  { id: "3", title: "Blinding Lights", artist: "The Weeknd", votes: 0, uri: "spotify:track:0VjIjW4GlUZAMYd2vXMi3b" },
];

const Vote = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const { lobbyCode, isHost, firstSong } = location.state || {};
  
  const [currentSong, setCurrentSong] = useState(firstSong || { title: "Love Story", artist: "Taylor Swift", album: { images: [] } });
  const [recommendations, setRecommendations] = useState(mockRecommendations);
  const [userVote, setUserVote] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [isSkipping, setIsSkipping] = useState(false);
  const [isLoadingCurrent, setIsLoadingCurrent] = useState(false);

  // Fetch currently playing track and votes on mount
  useEffect(() => {
    if (isHost) {
      fetchCurrentlyPlaying();
    }
    fetchVotes();
    
    // Demo: Auto-increment votes on "Levitating" every 2 seconds
    const voteInterval = setInterval(() => {
      setRecommendations((prev) =>
        prev.map((song) =>
          song.id === "2" ? { ...song, votes: song.votes + 1 } : song
        )
      );
    }, 2000);

    return () => clearInterval(voteInterval);
  }, [isHost]);

  const fetchVotes = async () => {
    if (!lobbyCode) {
      console.error('No lobby code provided');
      return;
    }
    
    try {
      const response = await api.getVotes(lobbyCode);
      if (response.votes && response.votes.length > 0) {
        setRecommendations(response.votes);
      }
    } catch (error) {
      console.error('Failed to fetch votes:', error);
      toast({
        title: "Error",
        description: "Failed to load votes. Room may not exist.",
        variant: "destructive",
      });
    }
  };

  const handleVote = async (songId: string) => {
    const song = recommendations.find(s => s.id === songId);
    if (!song) return;

    if (!lobbyCode) {
      toast({
        title: "Error",
        description: "No room code available. Please join a room first.",
        variant: "destructive",
      });
      return;
    }

    try {
      if (userVote === songId) {
        // Remove vote
        setUserVote(null);
        setRecommendations((prev) =>
          prev.map((s) =>
            s.id === songId ? { ...s, votes: s.votes - 1 } : s
          )
        );
      } else {
        // Add vote
        if (userVote !== null) {
          setRecommendations((prev) =>
            prev.map((s) =>
              s.id === userVote ? { ...s, votes: s.votes - 1 } : s
            )
          );
        }
        setUserVote(songId);
        setRecommendations((prev) =>
          prev.map((s) =>
            s.id === songId ? { ...s, votes: s.votes + 1 } : s
          )
        );

        // Send vote to backend
        await api.voteForSong(
          lobbyCode,
          song.id,
          song.title,
          song.artist,
          song.uri
        );

        toast({
          title: "Vote recorded!",
          description: `Voted for ${song.title}`,
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to vote",
        variant: "destructive",
      });
    }
  };

  const fetchCurrentlyPlaying = async () => {
    try {
      setIsLoadingCurrent(true);
      const playbackState = await api.getCurrentlyPlaying();
      
      if (playbackState.item) {
        const track = playbackState.item;
        setCurrentSong({
          title: track.name,
          artist: track.artists.map((artist: any) => artist.name).join(', '),
          album: {
            images: track.album.images || []
          }
        });
      }
    } catch (error) {
      console.error('Failed to fetch currently playing:', error);
    } finally {
      setIsLoadingCurrent(false);
    }
  };

  const handleSkipTrack = async () => {
    if (!isHost) return;
    
    try {
      setIsSkipping(true);
      
      // Find the highest voted song
      const sortedSongs = [...recommendations].sort((a, b) => b.votes - a.votes);
      const highestVoted = sortedSongs[0];
      
      // Update "Now Playing" to show the highest voted song
      setCurrentSong({
        title: highestVoted.title,
        artist: highestVoted.artist,
        album: { images: [] }
      });
      
      toast({
        title: "Playing highest voted!",
        description: `Now playing: ${highestVoted.title} by ${highestVoted.artist}`,
      });
      
      // Play the highest voted song on Spotify using startParty
      try {
        console.log(`Playing highest voted song: ${highestVoted.title} (${highestVoted.uri})`);
        await api.startParty(highestVoted.uri, lobbyCode);
        
        // Fetch the new currently playing track from Spotify after a short delay
        setTimeout(() => {
          fetchCurrentlyPlaying();
        }, 1500);
      } catch (error) {
        console.log("Failed to play on Spotify, showing in UI only:", error);
      }
      
      // Try to call the backend skip API (optional, for tracking)
      try {
        await api.skipTrack(lobbyCode);
        fetchVotes();
      } catch (error) {
        console.log("Backend skip tracking failed, continuing anyway");
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to skip track",
        variant: "destructive",
      });
    } finally {
      setIsSkipping(false);
    }
  };

  const handleEndSession = () => {
    navigate("/end-session");
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(lobbyCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const maxVotes = Math.max(...recommendations.map((s) => s.votes), 1);

  // Show error if no lobby code
  if (!lobbyCode) {
    return (
      <div className="min-h-screen px-4 py-8">
        <div className="max-w-5xl mx-auto space-y-8">
          <div className="glass-panel p-8 rounded-2xl text-center">
            <h2 className="text-2xl font-bold mb-4">No Room Code</h2>
            <p className="text-muted-foreground mb-6">
              You need to join a room to vote for songs.
            </p>
            <Button onClick={() => navigate('/')} className="spotify-glow">
              Go Home
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen px-4 py-8">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header with Join Code */}
        <div className="flex justify-between items-center">
          <div className="glass-panel px-6 py-3 rounded-full flex items-center gap-3">
            <span className="text-sm text-muted-foreground">Join Code:</span>
            <span className="text-xl font-bold text-primary">{lobbyCode || "ABC123"}</span>
            <Button
              size="sm"
              variant="ghost"
              onClick={handleCopyCode}
              className="hover:bg-white/10 h-8 w-8 p-0"
            >
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            </Button>
          </div>

          <div className="flex gap-3">
            {isHost && (
              <Button
                onClick={handleSkipTrack}
                disabled={isSkipping}
                variant="outline"
                className="spotify-glow"
              >
                <SkipForward className="mr-2 w-4 h-4" />
                {isSkipping ? "Skipping..." : "Skip Track"}
              </Button>
            )}
            
            {isHost && (
              <Button
                onClick={handleEndSession}
                variant="destructive"
                className="spotify-glow"
              >
                <LogOut className="mr-2 w-4 h-4" />
                End Session
              </Button>
            )}
          </div>
        </div>

        {/* Now Playing */}
        <div className="glass-panel p-8 rounded-2xl space-y-6 animate-fade-in">
          <div className="text-center">
            <p className="text-sm text-muted-foreground mb-4">NOW PLAYING</p>
            
            {/* Album Art */}
            <div className="w-64 h-64 mx-auto mb-6 relative">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/40 to-purple-600/40 blur-3xl" />
              <div className="relative w-full h-full rounded-2xl overflow-hidden shadow-2xl">
                {currentSong.album?.images?.[0]?.url ? (
                  <img
                    src={currentSong.album.images[0].url}
                    alt={`${currentSong.title} album cover`}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center">
                    <Music className="w-24 h-24 text-white" />
                  </div>
                )}
              </div>
            </div>

            {/* Song Info */}
            <h2 className="text-3xl font-bold mb-2">{currentSong.title}</h2>
            <p className="text-xl text-muted-foreground">{currentSong.artist}</p>
          </div>
        </div>

        {/* Voting Section */}
        <div className="space-y-4">
          <h3 className="text-2xl font-bold text-center">Vote for Next Song</h3>
          
          <div className="grid md:grid-cols-3 gap-6">
            {recommendations.map((song) => (
              <div
                key={song.id}
                onClick={() => handleVote(song.id)}
                className={`glass-panel p-6 rounded-2xl cursor-pointer transition-all hover:scale-105 ${
                  userVote === song.id
                    ? "border-2 border-primary spotify-glow"
                    : "hover:bg-white/10"
                }`}
              >
                <div className="flex flex-col items-center text-center space-y-4">
                  {/* Disc */}
                  <div className="relative w-32 h-32">
                    <div className="absolute inset-0 bg-primary/20 blur-2xl rounded-full" />
                    <div className="relative w-full h-full bg-gradient-to-br from-primary/60 to-primary rounded-full flex items-center justify-center">
                      <div className="w-12 h-12 bg-background rounded-full" />
                    </div>
                  </div>

                  {/* Song Info */}
                  <div>
                    <h4 className="font-semibold text-lg">{song.title}</h4>
                    <p className="text-sm text-muted-foreground">{song.artist}</p>
                  </div>

                  {/* Vote Count */}
                  <div className="w-full space-y-2">
                    <div className="flex justify-center items-center gap-2 text-sm">
                      <span className="text-primary font-bold">{song.votes}</span>
                      <span className="text-muted-foreground">votes</span>
                    </div>
                    <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary transition-all duration-300"
                        style={{ width: `${(song.votes / maxVotes) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Vote;
