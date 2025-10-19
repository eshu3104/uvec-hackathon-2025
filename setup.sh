#!/bin/bash
# Complete setup script for Flask backend
echo "Setting up Flask Backend for UVEC Hackathon 2025..."
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    echo "Virtual environment created!"
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip first
echo "Upgrading pip..."
pip install --upgrade pip

# Install minimal dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Flask Configuration
SECRET_KEY=your-secret-key-here-$(date +%s)
DEBUG=True
HOST=0.0.0.0
PORT=5000

# Database Configuration (if needed)
# DATABASE_URL=sqlite:///app.db

# API Configuration
# API_KEY=your-api-key-here
EOF
    echo ".env file created with default values!"
else
    echo ".env file already exists."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start development:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the server: python run.py"
echo ""
echo "Or use the convenience script: ./activate.sh"
