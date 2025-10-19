import { Button } from "@/components/ui/button";
import { Music } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { api } from "@/lib/api";

const Login = () => {
  const navigate = useNavigate();

  const handleSpotifyLogin = () => {
    // Redirect to Flask backend Spotify OAuth endpoint
    window.location.href = api.getSpotifyLoginUrl();
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-background to-background blur-3xl" />
      
      <div className="relative max-w-md w-full space-y-8 animate-fade-in">
        <div className="text-center">
          {/* Spotify-style Logo */}
          <div className="flex justify-center mb-8">
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full" />
              <Music className="w-24 h-24 text-primary relative animate-pulse-glow" />
            </div>
          </div>

          <h1 className="text-4xl font-bold mb-4">Connect with Spotify</h1>
          <p className="text-muted-foreground text-lg">
            Connect your Spotify account to create or join a music party
          </p>
        </div>

        <div className="glass-panel p-8 rounded-2xl space-y-6">
          <Button
            onClick={handleSpotifyLogin}
            size="lg"
            className="w-full text-lg py-6 bg-primary hover:bg-primary/90 spotify-glow hover:spotify-glow transition-all animate-pulse-glow"
          >
            <Music className="mr-2" />
            Login with Spotify
          </Button>

          <p className="text-center text-sm text-muted-foreground">
            We'll redirect you to Spotify to authorize access
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

export default Login;
