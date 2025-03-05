# #!/bin/bash
# # Setup script for Communication Centralizer

# echo "Setting up Communication Centralizer..."

# # Check for Python
# if ! command -v python3 &> /dev/null; then
#     echo "Error: Python 3 is required but not installed."
#     exit 1
# fi

# # Check for Node.js
# if ! command -v node &> /dev/null; then
#     echo "Error: Node.js is required but not installed."
#     exit 1
# fi

# # Check for pip
# if ! command -v pip3 &> /dev/null; then
#     echo "Error: pip3 is required but not installed."
#     exit 1
# fi

# # Check for npm
# if ! command -v npm &> /dev/null; then
#     echo "Error: npm is required but not installed."
#     exit 1
# fi

# # Create virtual environment
# echo "Creating Python virtual environment..."
# python3 -m venv venv
# source venv/bin/activate

# # Install Python dependencies
# echo "Installing Python dependencies..."
# pip3 install -r requirements.txt

# # Install spaCy model
# echo "Installing spaCy language model..."
# python -m spacy download en_core_web_sm

# # Install Node.js dependencies
# echo "Installing Node.js dependencies..."
# npm install

# # Verify puppeteer version for security
# PUPPETEER_VERSION=$(npm list puppeteer | grep puppeteer | cut -d@ -f2)
# REQUIRED_VERSION="24.3.1"
# if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PUPPETEER_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
#   echo "Warning: Puppeteer version $PUPPETEER_VERSION is installed, but version $REQUIRED_VERSION or higher is recommended for security."
#   echo "Running: npm install puppeteer@latest --save"
#   npm install puppeteer@latest --save
# else
#   echo "Puppeteer version $PUPPETEER_VERSION installed (meets security requirements)."
# fi

# # Create necessary directories
# echo "Creating necessary directories..."
# mkdir -p screenshots
# mkdir -p logs
# mkdir -p config/credentials

# # Create .env file if it doesn't exist
# if [ ! -f .env ]; then
#     echo "Creating .env file from template..."
#     cp .env.example .env
#     echo "Please edit .env file with your credentials."
# fi

# # Make sure Google credentials directory exists
# if [ ! -d "config/credentials" ]; then
#     mkdir -p config/credentials
#     echo "Created config/credentials directory for API credentials"
# fi

# # Create empty .gitkeep in credentials directory to ensure it's tracked by git
# touch config/credentials/.gitkeep

# # Add executable permissions to Python scripts
# chmod +x src/main.py
# if [ -f "scripts/schedule_job.py" ]; then
#     chmod +x scripts/schedule_job.py
# fi

# echo ""
# echo "Setup complete!"
# echo "--------------------------------------------------"
# echo "Next steps:"
# echo "1. Edit .env file with your credentials"
# echo "2. For advanced configurations, add API credentials to config/credentials/ directory"
# echo "3. Run the application with: python src/main.py"
# echo "--------------------------------------------------"
# echo "To run scheduled jobs: python scripts/schedule_job.py schedule --frequency hourly"
# echo "For more information, see the README.md file" 