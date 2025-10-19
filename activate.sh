#!/bin/bash
# Virtual environment activation script
source venv/bin/activate
echo "Virtual environment activated!"
echo "To deactivate, run: deactivate"
echo ""
echo "Installing dependencies..."
pip3 install -r requirements.txt
echo ""
echo "Setup complete! You can now run:"
echo "  python3 run.py"
