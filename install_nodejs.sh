#!/bin/bash

# Node.js Installation Script for Ubuntu/Debian Linux
# This will install Node.js LTS version which includes npm and npx

echo "======================================"
echo "  Node.js Installation Script"
echo "======================================"
echo ""

# Method 1: Using NodeSource repository (Recommended - Latest LTS)
echo "📦 Installing Node.js LTS via NodeSource repository..."
echo ""

# Download and execute NodeSource setup script
curl -fsSL https://deb.nodesource.com/setup_lts.x -o nodesource_setup.sh

# Make it executable and run with sudo
sudo -E bash nodesource_setup.sh

# Install Node.js (includes npm and npx)
sudo apt-get install -y nodejs

# Clean up
rm nodesource_setup.sh

# Verify installation
echo ""
echo "======================================"
echo "  Checking Installation"
echo "======================================"

if command -v node &> /dev/null; then
    echo "✅ Node.js installed: $(node --version)"
else
    echo "❌ Node.js installation failed"
fi

if command -v npm &> /dev/null; then
    echo "✅ npm installed: $(npm --version)"
else
    echo "❌ npm installation failed"
fi

if command -v npx &> /dev/null; then
    echo "✅ npx installed: $(npx --version)"
else
    echo "❌ npx installation failed"
fi

echo ""
echo "======================================"
echo "  Installation Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Restart your terminal or run: source ~/.bashrc"
echo "2. Test MCP with: mcp dev server_setup/server.py"
echo ""
