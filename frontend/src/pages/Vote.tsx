import { Button } from "@/components/ui/button";
import { Music, LogOut, Copy, Check } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { useState, useEffect } from "react";

const mockRecommendations = [
  { id: 1, title: "Shake It Off", artist: "Taylor Swift", votes: 0 },
  { id: 2, title: "Levitating", artist: "Dua Lipa", votes: 0 },
  { id: 3, title: "Blinding Lights", artist: "The Weeknd", votes: 0 },
];

const Vote = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { lobbyCode, isHost, firstSong } = location.state || {};
  
  const [currentSong] = useState(firstSong || { title: "Love Story", artist: "Taylor Swift" });
  const [progress, setProgress] = useState(0);
  const [recommendations, setRecommendations] = useState(mockRecommendations);
  const [userVote, setUserVote] = useState<number | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => (prev >= 100 ? 0 : prev + 1));
    }, 300);
    return () => clearInterval(interval);
  }, []);

  const handleVote = (songId: number) => {
    if (userVote === songId) {
      setUserVote(null);
      setRecommendations((prev) =>
        prev.map((song) =>
          song.id === songId ? { ...song, votes: song.votes - 1 } : song
        )
      );
    } else {
      if (userVote !== null) {
        setRecommendations((prev) =>
          prev.map((song) =>
            song.id === userVote ? { ...song, votes: song.votes - 1 } : song
          )
        );
      }
      setUserVote(songId);
      setRecommendations((prev) =>
        prev.map((song) =>
          song.id === songId ? { ...song, votes: song.votes + 1 } : song
        )
      );
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

        {/* Now Playing */}
        <div className="glass-panel p-8 rounded-2xl space-y-6 animate-fade-in">
          <div className="text-center">
            <p className="text-sm text-muted-foreground mb-4">NOW PLAYING</p>
            
            {/* Album Art */}
            <div className="w-64 h-64 mx-auto mb-6 relative">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/40 to-purple-600/40 blur-3xl" />
              <div className="relative w-full h-full bg-gradient-to-br from-primary to-purple-600 rounded-2xl flex items-center justify-center shadow-2xl">
                <Music className="w-24 h-24 text-white" />
              </div>
            </div>

            {/* Song Info */}
            <h2 className="text-3xl font-bold mb-2">{currentSong.title}</h2>
            <p className="text-xl text-muted-foreground">{currentSong.artist}</p>

            {/* Progress Bar */}
            <div className="mt-6 space-y-2">
              <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>{Math.floor(progress * 3 / 10)}:{String(Math.floor((progress * 3) % 60)).padStart(2, '0')}</span>
                <span>3:00</span>
              </div>
            </div>
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

        {/* Timer Info */}
        <div className="text-center text-sm text-muted-foreground">
          <p>New recommendations will appear 30 seconds before the song ends</p>
        </div>
      </div>
    </div>
  );
};

export default Vote;
