@echo off
echo 🚀 Starting RAG Analytics Frontend
echo ================================================

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: npm is not installed or not in PATH
    pause
    exit /b 1
)

echo ✓ Node.js and npm are available

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✓ Dependencies installed successfully
) else (
    echo ✓ Dependencies already installed
)

echo.
echo ✓ All checks passed!
echo Starting React development server...
echo Frontend will be available at: http://localhost:3000
echo Press Ctrl+C to stop the server
echo.

REM Start the React development server
npm start

pause
