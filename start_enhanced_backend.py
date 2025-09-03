#!/usr/bin/env python3
"""
Startup script for Enhanced RAG Analytics Backend
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'pandas', 'openpyxl', 'python-multipart',
        'python-dotenv', 'sqlalchemy', 'psycopg2', 'pymysql', 'plotly',
        'llama-index', 'langchain', 'openai', 'faiss-cpu', 'sentence-transformers'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Installing missing packages...")
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ All packages installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages. Please install manually:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    return True

def check_environment():
    """Check environment variables"""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  .env file not found. Creating template...")
        with open('.env', 'w') as f:
            f.write("""# OpenAI API Key (required for LLM features)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Key (optional)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database URLs (optional)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
MYSQL_URL=mysql+pymysql://user:password@localhost:3306/dbname
""")
        print("📝 Please edit .env file with your API keys")
        return False
    
    # Check for OpenAI API key
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not found in .env file")
        print("   LLM features will use fallback processing")
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['backend', 'uploads', 'indices', 'logs']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created")

def main():
    """Main startup function"""
    print("🚀 Enhanced RAG Analytics Backend Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    check_environment()
    
    # Create directories
    create_directories()
    
    print("\n🎯 Starting Enhanced Backend...")
    print("Features:")
    print("✅ LLM-powered queries with LangChain")
    print("✅ FAISS vector indexing with LlamaIndex")
    print("✅ Dynamic database connections")
    print("✅ Intelligent visualizations")
    print("✅ RAG-based context retrieval")
    print("=" * 50)
    
    # Start the enhanced backend
    try:
        import uvicorn
        from enhanced_backend import app
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed correctly")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
