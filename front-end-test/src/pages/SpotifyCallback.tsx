import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Music, Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

const SpotifyCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('Processing authentication...');

  useEffect(() => {
    const code = searchParams.get('code');
    const error = searchParams.get('error');

    if (error) {
      setStatus('error');
      setMessage(`Authentication failed: ${error}`);
      return;
    }

    // If we have a code, the backend hasn't processed it yet
    if (code) {
      setStatus('error');
      setMessage('Authentication failed - please try again');
      return;
    }

    // If we're here without a code, it means the backend successfully processed
    // the OAuth callback and redirected us here
    setStatus('success');
    setMessage('Successfully authenticated with Spotify!');
    
    // Redirect to create lobby after a short delay
    setTimeout(() => {
      navigate('/create-lobby');
    }, 1500);
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-background to-background blur-3xl" />
      
      <div className="relative max-w-md w-full space-y-8 animate-fade-in">
        <div className="text-center">
          <div className="flex justify-center mb-8">
            {status === 'loading' && (
              <Loader2 className="w-16 h-16 text-primary animate-spin" />
            )}
            {status === 'success' && (
              <div className="relative">
                <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full" />
                <Music className="w-16 h-16 text-primary relative animate-pulse-glow" />
              </div>
            )}
            {status === 'error' && (
              <AlertCircle className="w-16 h-16 text-destructive" />
            )}
          </div>

          <h1 className="text-3xl font-bold mb-4">
            {status === 'loading' && 'Connecting to Spotify...'}
            {status === 'success' && 'Authentication Successful!'}
            {status === 'error' && 'Authentication Failed'}
          </h1>
          
          <p className="text-muted-foreground text-lg">
            {message}
          </p>
        </div>

        {status === 'error' && (
          <div className="flex justify-center">
            <Button
              onClick={() => navigate('/login')}
              className="bg-primary hover:bg-primary/90"
            >
              Try Again
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SpotifyCallback;
