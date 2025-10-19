import { Button } from "@/components/ui/button";
import { Music, Copy, Check, Loader2, AlertCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import type { CreateRoomResponse } from "@/lib/types";

const CreateLobby = () => {
  const navigate = useNavigate();
  const [lobbyCreated, setLobbyCreated] = useState(false);
  const [lobbyCode, setLobbyCode] = useState<string>("");
  const [playlistInfo, setPlaylistInfo] = useState<{ name: string; url: string } | null>(null);
  const [copied, setCopied] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreateLobby = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response: CreateRoomResponse = await api.createRoom();
      
      setLobbyCode(response.room_code);
      setPlaylistInfo({
        name: response.playlist.name,
        url: response.playlist.url
      });
      setLobbyCreated(true);
      
      toast.success("Lobby created successfully!");
      
      // Redirect to select song after a delay
      setTimeout(() => {
        navigate("/select-song", { 
          state: { 
            lobbyCode: response.room_code,
            room: response.room,
            playlist: response.playlist
          } 
        });
      }, 3000);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create lobby';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(lobbyCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-background to-background blur-3xl" />
      
      <div className="relative max-w-2xl w-full space-y-8 animate-fade-in">
        {!lobbyCreated ? (
          <>
            <div className="text-center">
              <div className="flex justify-center mb-6">
                <Music className="w-16 h-16 text-primary animate-pulse" />
              </div>
              <h1 className="text-5xl font-bold mb-4">
                Create Your Party Lobby 🎉
              </h1>
              <p className="text-muted-foreground text-xl max-w-xl mx-auto">
                Start a music party where you and your friends can vote on what plays next. 
                You'll be able to control the session and share a code with your guests.
              </p>
            </div>

            <div className="glass-panel p-12 rounded-2xl text-center space-y-6">
              {error && (
                <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
                  <div className="flex items-center gap-2 text-destructive">
                    <AlertCircle className="w-5 h-5" />
                    <span className="text-sm">{error}</span>
                  </div>
                </div>
              )}
              
              <Button
                onClick={handleCreateLobby}
                disabled={isLoading}
                size="lg"
                className="text-xl px-12 py-8 bg-primary hover:bg-primary/90 spotify-glow hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-6 w-6 animate-spin" />
                    Creating Lobby...
                  </>
                ) : (
                  "Create Lobby"
                )}
              </Button>
              
              <p className="text-sm text-muted-foreground">
                You'll be able to choose the first song after creating the lobby
              </p>
            </div>
          </>
        ) : (
          <div className="glass-panel p-12 rounded-2xl text-center space-y-6 animate-scale-in">
            <div className="flex justify-center mb-4">
              <div className="p-4 bg-primary/20 rounded-full">
                <Check className="w-12 h-12 text-primary" />
              </div>
            </div>
            
            <h2 className="text-4xl font-bold text-primary">Lobby Created!</h2>
            
            <div className="space-y-4">
              <p className="text-muted-foreground">
                Share this code with your friends:
              </p>
              
              <div className="glass-panel p-6 rounded-xl">
                <div className="flex items-center justify-center gap-4">
                  <span className="text-5xl font-bold tracking-widest text-primary">
                    {lobbyCode}
                  </span>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={handleCopyCode}
                    className="hover:bg-white/10"
                  >
                    {copied ? <Check className="w-5 h-5" /> : <Copy className="w-5 h-5" />}
                  </Button>
                </div>
              </div>
              
              {playlistInfo && (
                <div className="glass-panel p-4 rounded-xl">
                  <p className="text-sm text-muted-foreground mb-2">Spotify Playlist Created:</p>
                  <p className="font-semibold text-primary">{playlistInfo.name}</p>
                  <a 
                    href={playlistInfo.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-xs text-muted-foreground hover:text-primary transition-colors"
                  >
                    Open in Spotify →
                  </a>
                </div>
              )}
            </div>

            <p className="text-sm text-muted-foreground animate-pulse">
              Redirecting to song selection...
            </p>
          </div>
        )}

        <div className="text-center">
          <Button
            variant="link"
            onClick={() => navigate("/")}
            className="text-muted-foreground"
          >
            ← Back to Home
          </Button>
        </div>
      </div>
    </div>
  );
};

export default CreateLobby;
