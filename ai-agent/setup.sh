#!/bin/bash

echo "🚀 Setting up Worldmine Market News AI Agent..."

# Check if Python 3.11+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Check environment variables
echo "🔧 Checking environment variables..."
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Please copy .env.example to .env and fill in your API keys."
    cp .env.example .env
    echo "📝 Created .env file from template. Please edit it with your API keys."
fi

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run the agent: python main.py"
echo "3. Or use Docker: docker-compose up -d"
echo ""
echo "📚 For more information, see README.md"
