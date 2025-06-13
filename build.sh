#!/bin/bash
set -e

echo "🚀 Starting Dona Bot build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies for MCP toolbox
echo "🔧 Installing MCP toolbox dependencies..."
cd dona-mcp-toolbox
npm install
cd ..

echo "✅ Build completed successfully!"