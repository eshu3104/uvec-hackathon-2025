import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Music, Loader2, AlertCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import type { JoinRoomResponse } from "@/lib/types";

const JoinLobby = () => {
  const navigate = useNavigate();
  const [code, setCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleJoinLobby = async () => {
    if (code.length !== 6) {
      setError("Please enter a 6-character room code");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response: JoinRoomResponse = await api.joinRoom(code);
      
      toast.success("Successfully joined the lobby!");
      
      // Navigate to vote page with participant info
      navigate("/vote", { 
        state: { 
          lobbyCode: code, 
          isHost: false,
          participant: response.participant,
          roomInfo: response.room_info
        } 
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to join lobby';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-background to-background blur-3xl" />
      
      <div className="relative max-w-md w-full space-y-8 animate-fade-in">
        <div className="text-center">
          <div className="flex justify-center mb-6">
            <Music className="w-16 h-16 text-primary animate-pulse" />
          </div>
          <h1 className="text-5xl font-bold mb-4">Join the Party</h1>
          <p className="text-muted-foreground text-lg">
            Ask the host for the join code
          </p>
        </div>

        <div className="glass-panel p-8 rounded-2xl space-y-6">
          {error && (
            <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
              <div className="flex items-center gap-2 text-destructive">
                <AlertCircle className="w-5 h-5" />
                <span className="text-sm">{error}</span>
              </div>
            </div>
          )}
          
          <div className="space-y-4">
            <label className="text-sm text-muted-foreground text-center block">
              Enter Lobby Code
            </label>
            <Input
              value={code}
              onChange={(e) => {
                setCode(e.target.value.toUpperCase());
                setError(null); // Clear error when user types
              }}
              placeholder="ABC123"
              maxLength={6}
              disabled={isLoading}
              className="text-center text-3xl font-bold tracking-widest bg-background/50 border-primary/20 focus:border-primary h-16 disabled:opacity-50"
            />
          </div>

          <Button
            onClick={handleJoinLobby}
            disabled={code.length !== 6 || isLoading}
            size="lg"
            className="w-full text-lg py-6 bg-primary hover:bg-primary/90 spotify-glow disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-6 w-6 animate-spin" />
                Joining...
              </>
            ) : (
              "Join Lobby"
            )}
          </Button>

          <p className="text-center text-sm text-muted-foreground">
            The code is 6 characters long
          </p>
        </div>

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

export default JoinLobby;
