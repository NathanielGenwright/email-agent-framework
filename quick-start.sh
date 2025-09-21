#!/bin/bash
"""
Email Agent System - Quick Start Script

One-command setup for the complete email agent system.
"""

set -e  # Exit on any error

echo "🚀 Email Agent System - Quick Start"
echo "=================================="
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Make scripts executable
echo "🔧 Setting up permissions..."
chmod +x email-agent
chmod +x install.py
chmod +x activate.py

# Install the system
echo "📦 Installing Email Agent System..."
python3 install.py

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Installation completed successfully!"
    echo ""
    echo "🎯 Next Steps:"
    echo "1. Configure your email credentials:"
    echo "   nano ~/.email-agent/.env"
    echo ""
    echo "2. Start the system:"
    echo "   ./email-agent activate"
    echo ""
    echo "3. Check status:"
    echo "   ./email-agent status"
    echo ""
    echo "4. Try interactive mode:"
    echo "   ./email-agent interactive"
    echo ""
    echo "📖 For detailed setup instructions, see DEPLOYMENT_GUIDE.md"
else
    echo "❌ Installation failed. Please check the errors above."
    exit 1
fi