import { Button } from "@/components/ui/button";
import { Music, Users, Vote } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero Section */}
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-20">
        <div className="max-w-4xl mx-auto text-center space-y-8 animate-fade-in">
          {/* Logo/Icon */}
          <div className="flex justify-center mb-8">
            <div className="relative">
              <Music className="w-20 h-20 text-primary animate-pulse-glow" />
              <div className="absolute inset-0 blur-2xl bg-primary/20 rounded-full" />
            </div>
          </div>

          {/* Heading */}
          <h1 className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-foreground to-primary bg-clip-text text-transparent">
            Vote for the Next Song
          </h1>
          
          <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto">
            Create a party lobby and let your friends vote for what plays next in real time!
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
            <Button 
              size="lg"
              onClick={() => navigate("/login")}
              className="text-lg px-8 py-6 bg-primary hover:bg-primary/90 spotify-glow hover:spotify-glow transition-all"
            >
              <Users className="mr-2" />
              Create Lobby
            </Button>
            
            <Button 
              size="lg"
              variant="outline"
              onClick={() => navigate("/join-lobby")}
              className="text-lg px-8 py-6 glass-panel hover:bg-white/10 transition-all"
            >
              <Vote className="mr-2" />
              Join Lobby
            </Button>
          </div>
        </div>

        {/* Scroll Down Indicator */}
        <div className="mt-20 animate-bounce">
          <div className="w-6 h-10 border-2 border-primary rounded-full flex justify-center">
            <div className="w-1 h-3 bg-primary rounded-full mt-2 animate-pulse" />
          </div>
        </div>
      </div>

      {/* Info Section */}
      <div className="px-4 py-20 glass-panel">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
            How It Works
          </h2>
          
          <div className="grid md:grid-cols-2 gap-8 mb-16">
            {/* Host Card */}
            <div className="glass-panel p-8 rounded-2xl hover:scale-105 transition-transform">
              <div className="flex items-center gap-4 mb-4">
                <div className="p-3 bg-primary/20 rounded-full">
                  <Users className="w-8 h-8 text-primary" />
                </div>
                <h3 className="text-2xl font-bold">Create</h3>
              </div>
              <p className="text-muted-foreground mb-6">
                Host a music party by creating a lobby. Connect your Spotify account, 
                choose the first song, and share the lobby code with friends.
              </p>
              <Button 
                onClick={() => navigate("/login")}
                className="w-full bg-primary hover:bg-primary/90"
              >
                Start as Host
              </Button>
            </div>

            {/* Guest Card */}
            <div className="glass-panel p-8 rounded-2xl hover:scale-105 transition-transform">
              <div className="flex items-center gap-4 mb-4">
                <div className="p-3 bg-primary/20 rounded-full">
                  <Vote className="w-8 h-8 text-primary" />
                </div>
                <h3 className="text-2xl font-bold">Join</h3>
              </div>
              <p className="text-muted-foreground mb-6">
                Enter a lobby code to join a friend's party. Vote for your favorite 
                songs from the recommendations and enjoy the music together!
              </p>
              <Button 
                onClick={() => navigate("/join-lobby")}
                variant="outline"
                className="w-full glass-panel hover:bg-white/10"
              >
                Join a Party
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="py-8 text-center text-muted-foreground border-t border-border">
        <p className="text-sm">Made for Hackathon 2025 🎉</p>
      </footer>
    </div>
  );
};

export default Home;
