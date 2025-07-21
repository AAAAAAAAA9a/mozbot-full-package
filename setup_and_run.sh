#!/bin/bash

# Fixed script for MozBot setup

echo "🚀 Starting MozBot setup..."

# Check if ZIP file exists
if [ ! -f "mozbot-platform-configured.zip" ]; then
    echo "❌ Error: mozbot-platform-configured.zip not found"
    exit 1
fi

# Clean up previous installation
echo "🧹 Cleaning up previous installation..."
rm -rf mozbot-project
mkdir mozbot-project

# Extract files
echo "📦 Extracting MozBot files..."
unzip -q mozbot-platform-configured.zip -d ./mozbot-project

# Find the correct path (handles different extraction structures)
if [ -d "./mozbot-project/mozbot-platform-configured/home/ubuntu/upload" ]; then
    PROJECT_PATH="./mozbot-project/mozbot-platform-configured/home/ubuntu/upload"
elif [ -d "./mozbot-project/home/ubuntu/upload" ]; then
    PROJECT_PATH="./mozbot-project/home/ubuntu/upload"
else
    echo "❌ Error: Cannot find project files after extraction"
    exit 1
fi

echo "📁 Project path: $PROJECT_PATH"
cd "$PROJECT_PATH"

# Setup Backend
echo "🐍 Setting up Python backend..."
cd mozbot-backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install requests

# Create necessary directories
mkdir -p instance database src/database
chmod 755 instance database src/database

# Initialize database
echo "🗄️ Creating database..."
python create_db.py

# Start backend
echo "🚀 Starting backend..."
python src/main.py &
BACKEND_PID=$!
echo "✅ Backend running (PID: $BACKEND_PID)"

# Give backend time to start
sleep 2

# Go back to upload directory
cd ..

# Setup Admin Panel
echo "⚛️ Setting up admin panel..."
cd mozbot-admin

# Install dependencies
pnpm install

# Start admin panel
echo "🚀 Starting admin panel..."
pnpm dev --port 5173 &
ADMIN_PID=$!
echo "✅ Admin panel running (PID: $ADMIN_PID)"

# Go back to upload directory
cd ..

# Setup Widget
echo "🔧 Setting up widget..."
cd mozbot-widget

# Install dependencies
pnpm install

# Start widget
echo "🚀 Starting widget..."
pnpm dev --port 5174 &
WIDGET_PID=$!
echo "✅ Widget running (PID: $WIDGET_PID)"

# Final status
echo ""
echo "🎉 MozBot successfully started!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 Service URLs:"
echo "   Backend API:    http://127.0.0.1:5000"
echo "   Admin Panel:    http://localhost:5173"
echo "   Chat Widget:    http://localhost:5174"
echo ""
echo "🛑 To stop all services:"
echo "   kill $BACKEND_PID $ADMIN_PID $WIDGET_PID"
echo ""
echo "📝 Process IDs saved to: pids.txt"
echo "$BACKEND_PID $ADMIN_PID $WIDGET_PID" > pids.txt

# Wait a moment to ensure all services are running
sleep 3
echo "🔍 Checking service status..."

# Check if processes are still running
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "✅ Backend: Running"
else
    echo "❌ Backend: Failed to start"
fi

if kill -0 $ADMIN_PID 2>/dev/null; then
    echo "✅ Admin Panel: Running"
else
    echo "❌ Admin Panel: Failed to start"
fi

if kill -0 $WIDGET_PID 2>/dev/null; then
    echo "✅ Widget: Running"
else
    echo "❌ Widget: Failed to start"
fi

echo ""
echo "🎯 Setup complete! You can now access the MozBot platform."