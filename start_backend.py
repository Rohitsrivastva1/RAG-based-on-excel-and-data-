#!/usr/bin/env python3
"""
Start script for the RAG Analytics backend
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)

def install_requirements():
    """Install Python requirements"""
    print("Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Python requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    directories = ["uploads", "temp", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✓ Directories created")

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists(".env"):
        print("Warning: .env file not found. Please copy env.example to .env and configure it.")
        print("You can run: cp env.example .env")
        return False
    return True

def start_server():
    """Start the FastAPI server"""
    print("Starting RAG Analytics backend server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\nServer stopped")

def main():
    """Main function"""
    print("🚀 Starting RAG Analytics Backend")
    print("=" * 50)
    
    check_python_version()
    install_requirements()
    create_directories()
    
    if not check_env_file():
        print("\nPlease configure your .env file before starting the server.")
        return
    
    print("\n✓ All checks passed!")
    start_server()

if __name__ == "__main__":
    main()
