#!/bin/bash

# Mozbot Development Server Launcher
# Starts all services for development

set -e

echo "🚀 Mozbot Development Launcher"
echo "==============================="

# Function to check if a port is in use
port_in_use() {
    netstat -tuln 2>/dev/null | grep -q ":$1 " 2>/dev/null || lsof -ti:$1 >/dev/null 2>&1
}

# Function to start a service in background
start_service() {
    local name="$1"
    local command="$2"
    local port="$3"
    
    if port_in_use "$port"; then
        echo "⚠️  $name appears to be running (port $port in use)"
        return
    fi
    
    echo "🔄 Starting $name on port $port..."
    eval "$command" &
    echo "✅ $name started (PID: $!)"
}

echo ""
echo "Starting all Mozbot services..."
echo ""

# Start Backend (Flask typically runs on 5000)
echo "🔧 Starting Backend..."
cd mozbot-backend
if [ -d "venv" ]; then
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
        start_service "Backend" "source venv/Scripts/activate && python src/main.py" "5000"
    else
        start_service "Backend" "source venv/bin/activate && python src/main.py" "5000"
    fi
else
    echo "⚠️  Virtual environment not found. Run ./quick-setup.sh first."
fi
cd ..

sleep 2

# Start Admin Frontend (Vite typically runs on 5173)
echo ""
echo "🎛️  Starting Admin Frontend..."
cd mozbot-admin
if [ -d "node_modules" ]; then
    start_service "Admin Frontend" "pnpm dev" "5173"
else
    echo "⚠️  Dependencies not installed. Run ./quick-setup.sh first."
fi
cd ..

sleep 2

# Start Widget Frontend (Vite typically runs on 5174)
echo ""
echo "🤖 Starting Widget Frontend..."
cd mozbot-widget  
if [ -d "node_modules" ]; then
    start_service "Widget Frontend" "pnpm dev --port 5174" "5174"
else
    echo "⚠️  Dependencies not installed. Run ./quick-setup.sh first."
fi
cd ..

echo ""
echo "🎉 Development servers starting!"
echo ""
echo "📱 Access your services:"
echo "   Backend API:     http://localhost:5000"
echo "   Admin Panel:     http://localhost:5173" 
echo "   Widget Demo:     http://localhost:5174"
echo ""
echo "⏹️  To stop all services: Ctrl+C or run 'pkill -f 'pnpm dev|python src/main.py''"
echo ""
echo "💡 Logs will appear below. Press Ctrl+C to stop all services."

# Wait for services and handle Ctrl+C
trap 'echo ""; echo "🛑 Stopping all services..."; pkill -f "pnpm dev" 2>/dev/null || true; pkill -f "python src/main.py" 2>/dev/null || true; echo "✅ All services stopped"; exit 0' INT

# Keep script running
wait
