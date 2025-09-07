#!/usr/bin/env python3
"""
Test script to verify document processing functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_document_processing():
    """Test if document processing libraries are available."""
    print("Testing document processing libraries...")
    
    try:
        import fitz
        print("✅ PyMuPDF (fitz) - Available")
    except ImportError as e:
        print(f"❌ PyMuPDF (fitz) - Not available: {e}")
    
    try:
        import docx
        print("✅ python-docx - Available")
    except ImportError as e:
        print(f"❌ python-docx - Not available: {e}")
    
    try:
        import markdown
        print("✅ markdown - Available")
    except ImportError as e:
        print(f"❌ markdown - Not available: {e}")
    
    try:
        from bs4 import BeautifulSoup
        print("✅ beautifulsoup4 - Available")
    except ImportError as e:
        print(f"❌ beautifulsoup4 - Not available: {e}")
    
    try:
        import requests
        print("✅ requests - Available")
    except ImportError as e:
        print(f"❌ requests - Not available: {e}")
    
    try:
        import lxml
        print("✅ lxml - Available")
    except ImportError as e:
        print(f"❌ lxml - Not available: {e}")
    
    # Test embedding manager
    try:
        from managers.embedding_manager import EmbeddingManager
        print("✅ EmbeddingManager - Available")
        
        # Test if document processing methods exist
        manager = EmbeddingManager()
        if hasattr(manager, 'process_pdf'):
            print("✅ process_pdf method - Available")
        if hasattr(manager, 'process_docx'):
            print("✅ process_docx method - Available")
        if hasattr(manager, 'process_markdown'):
            print("✅ process_markdown method - Available")
        if hasattr(manager, 'process_website'):
            print("✅ process_website method - Available")
            
    except Exception as e:
        print(f"❌ EmbeddingManager - Error: {e}")

if __name__ == "__main__":
    test_document_processing()
