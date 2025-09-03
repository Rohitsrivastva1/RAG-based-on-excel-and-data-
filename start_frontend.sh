#!/bin/bash

echo "🚀 Starting RAG Analytics Frontend"
echo "================================================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed or not in PATH"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed or not in PATH"
    exit 1
fi

echo "✓ Node.js and npm are available"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
    echo "✓ Dependencies installed successfully"
else
    echo "✓ Dependencies already installed"
fi

echo ""
echo "✓ All checks passed!"
echo "Starting React development server..."
echo "Frontend will be available at: http://localhost:3000"
echo "Press Ctrl+C to stop the server"
echo ""

# Start the React development server
npm start
