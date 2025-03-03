#!/bin/bash
# Setup script for Communication Centralizer

echo "Setting up Communication Centralizer..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is required but not installed."
    exit 1
fi

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not installed."
    exit 1
fi

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "Error: npm is required but not installed."
    exit 1
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Install spaCy model
echo "Installing spaCy language model..."
python -m spacy download en_core_web_sm

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p screenshots
mkdir -p logs
mkdir -p config/credentials

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your credentials."
fi

echo "Setup complete!"
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Add API credentials to config/credentials/ directory"
echo "3. Run the application with 'python src/main.py'" 