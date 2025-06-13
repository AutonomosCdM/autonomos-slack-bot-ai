#!/bin/bash
set -e

echo "🚀 Starting Dona Bot build process..."

# Check Node.js availability
echo "🔍 Checking Node.js..."
if command -v node >/dev/null 2>&1; then
    echo "✅ Node.js found: $(node --version)"
else
    echo "❌ Node.js not found!"
    exit 1
fi

if command -v npm >/dev/null 2>&1; then
    echo "✅ npm found: $(npm --version)"
else
    echo "❌ npm not found!"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if MCP toolbox directory exists
if [ ! -d "dona-mcp-toolbox" ]; then
    echo "❌ MCP toolbox directory not found!"
    exit 1
fi

# Install Node.js dependencies for MCP toolbox
echo "🔧 Installing MCP toolbox dependencies..."
cd dona-mcp-toolbox

# Verify package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found in MCP toolbox!"
    exit 1
fi

# Install dependencies with verbose output
echo "📋 Installing npm dependencies..."
npm install --verbose

# Verify installation
if [ ! -d "node_modules" ]; then
    echo "❌ node_modules not created!"
    exit 1
fi

echo "✅ MCP dependencies installed"
cd ..

# Test MCP functionality
echo "🧪 Testing MCP functionality..."
python -c "
import sys
import os
sys.path.append('.')
try:
    from mcp_integration import mcp_integration
    result = mcp_integration.initialize()
    if result:
        print('✅ MCP integration test passed')
    else:
        print('❌ MCP integration test failed')
        sys.exit(1)
except Exception as e:
    print(f'❌ MCP test error: {e}')
    sys.exit(1)
"

echo "✅ Build completed successfully!"