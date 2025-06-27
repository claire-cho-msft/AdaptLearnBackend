#!/bin/bash

# Setup script for AdaptLearn Backend with LLM content adaptation

echo "🚀 Setting up AdaptLearn Backend with LLM Content Adaptation"
echo "============================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed. Please install pip3 first."
    exit 1
fi

echo "✅ Python 3 and pip3 found"

# Install requirements
echo "📦 Installing Python packages..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ All packages installed successfully"
else
    echo "❌ Failed to install packages. Please check the error messages above."
    exit 1
fi

# Set up environment variables
echo ""
echo "🤖 Setting up Local AI Model for content adaptation"
echo "=================================================="
echo ""
echo "This system now uses a local Hugging Face model for content adaptation."
echo "No API keys or internet connection required for content adaptation!"
echo ""
echo "The system will automatically download and use Microsoft DialoGPT-medium"
echo "on first run. This may take a few minutes for the initial download."
echo ""

read -p "Do you have a GPU available for faster processing? (y/n): " has_gpu

if [ "$has_gpu" = "y" ] || [ "$has_gpu" = "Y" ]; then
    echo ""
    echo "✅ GPU acceleration will be used if PyTorch detects CUDA"
    echo "📝 If you encounter issues, the system will fall back to CPU processing"
else
    echo ""
    echo "✅ CPU processing will be used (works great, just a bit slower)"
    echo "💡 The first content adaptation per session may take 30-60 seconds"
    echo "   Subsequent adaptations will be much faster due to caching"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "  cd src"
echo "  python3 app.py"
echo ""
echo "Then visit: http://localhost:5000/tutorial"
echo ""
echo "Features:"
echo "  ✅ Markdown to HTML tutorial conversion"
echo "  ✅ Microsoft Docs features support"
echo "  ✅ Interactive sliders for difficulty levels"
echo "  ✅ Local AI-powered content adaptation (no API keys needed!)"
echo "  🤖 Uses Hugging Face transformers for free, local processing"
echo ""
