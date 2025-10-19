import { Button } from "@/components/ui/button";
import { Music, CheckCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

const EndSession = () => {
  const navigate = useNavigate();
  const [showConfetti, setShowConfetti] = useState(true);

  useEffect(() => {
    setTimeout(() => setShowConfetti(false), 3000);
  }, []);

  const handleSavePlaylist = () => {
    // Mock save action
    setTimeout(() => {
      navigate("/");
    }, 1000);
  };

  const handleSkip = () => {
    navigate("/");
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden">
      {/* Gradient Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-purple-600/20 to-background blur-3xl" />
      
      {/* Confetti Effect */}
      {showConfetti && (
        <div className="absolute inset-0 pointer-events-none">
          {[...Array(50)].map((_, i) => (
            <div
              key={i}
              className="absolute animate-fade-in"
              style={{
                left: `${Math.random() * 100}%`,
                top: `-10%`,
                animation: `fall ${2 + Math.random() * 3}s linear infinite`,
                animationDelay: `${Math.random() * 2}s`,
              }}
            >
              <div
                className="w-2 h-2 rounded-full"
                style={{
                  backgroundColor: [
                    "hsl(141, 73%, 42%)",
                    "hsl(280, 70%, 60%)",
                    "hsl(40, 90%, 60%)",
                    "hsl(200, 80%, 60%)",
                  ][Math.floor(Math.random() * 4)],
                }}
              />
            </div>
          ))}
        </div>
      )}

      <div className="relative max-w-2xl w-full space-y-8 animate-scale-in">
        <div className="text-center">
          <div className="flex justify-center mb-6">
            <div className="relative">
              <Music className="w-20 h-20 text-primary animate-pulse" />
              <div className="absolute inset-0 blur-2xl bg-primary/30 rounded-full" />
            </div>
          </div>
          
          <h1 className="text-6xl font-bold mb-4">Session Ended 🎉</h1>
          <p className="text-muted-foreground text-xl">
            Thanks for using our music party app!
          </p>
        </div>

        <div className="glass-panel p-12 rounded-2xl space-y-8">
          <div className="text-center space-y-4">
            <CheckCircle className="w-16 h-16 text-primary mx-auto" />
            <h2 className="text-3xl font-bold">Save Your Playlist?</h2>
            <p className="text-muted-foreground text-lg">
              Would you like to save this session's playlist to your Spotify account?
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4">
            <Button
              onClick={handleSavePlaylist}
              size="lg"
              className="flex-1 text-lg py-6 bg-primary hover:bg-primary/90 spotify-glow"
            >
              Yes, Save It
            </Button>
            
            <Button
              onClick={handleSkip}
              size="lg"
              variant="outline"
              className="flex-1 text-lg py-6 glass-panel hover:bg-white/10"
            >
              No, Thanks
            </Button>
          </div>
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

      <style>{`
        @keyframes fall {
          to {
            transform: translateY(100vh) rotate(360deg);
          }
        }
      `}</style>
    </div>
  );
};

export default EndSession;
