#!/bin/bash

# Mozbot Quick Setup Script
# This script installs all dependencies for the compact Mozbot project

set -e  # Exit on error

echo "🤖 Mozbot Quick Setup"
echo "===================="
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Node.js and pnpm
if ! command_exists node; then
    echo "❌ Node.js is required but not installed."
    echo "   Please install Node.js from https://nodejs.org/"
    exit 1
fi

if ! command_exists pnpm; then
    echo "📦 pnpm not found. Installing pnpm..."
    npm install -g pnpm
fi

# Check Python
if ! command_exists python3 && ! command_exists python; then
    echo "❌ Python is required but not installed."
    echo "   Please install Python from https://python.org/"
    exit 1
fi

# Use python3 if available, otherwise python
if command_exists python3; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo "✅ Prerequisites check complete"
echo ""

# Setup Frontend - Admin
echo "🎛️  Setting up Mozbot Admin (Frontend)..."
cd mozbot-admin
if [ -f "package.json" ]; then
    pnpm install
    echo "✅ Mozbot Admin dependencies installed"
else
    echo "⚠️  No package.json found in mozbot-admin"
fi
cd ..

echo ""

# Setup Frontend - Widget  
echo "🤖 Setting up Mozbot Widget (Frontend)..."
cd mozbot-widget
if [ -f "package.json" ]; then
    pnpm install
    echo "✅ Mozbot Widget dependencies installed"
else
    echo "⚠️  No package.json found in mozbot-widget"
fi
cd ..

echo ""

# Setup Backend
echo "🔧 Setting up Mozbot Backend (Python)..."
cd mozbot-backend
if [ -f "requirements.txt" ]; then
    # Check if venv exists, create if not
    if [ ! -d "venv" ]; then
        echo "   Creating virtual environment..."
        $PYTHON_CMD -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    echo "   Installing Python dependencies..."
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
        # Windows
        source venv/Scripts/activate
    else
        # Linux/macOS
        source venv/bin/activate
    fi
    
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Mozbot Backend dependencies installed"
    
    deactivate
else
    echo "⚠️  No requirements.txt found in mozbot-backend"
fi
cd ..

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "🚀 Quick Start Commands:"
echo ""
echo "Frontend (Admin):"
echo "  cd mozbot-admin && pnpm dev"
echo ""
echo "Frontend (Widget):"  
echo "  cd mozbot-widget && pnpm dev"
echo ""
echo "Backend:"
echo "  cd mozbot-backend && source venv/bin/activate && python src/main.py"
echo "  (On Windows: venv\\Scripts\\activate)"
echo ""
echo "📚 For more details, see README.md"
