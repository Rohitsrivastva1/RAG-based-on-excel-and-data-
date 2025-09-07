"""
Tests for document ingestion functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Import the modules we want to test
try:
    from managers.embedding_manager import EmbeddingManager
    from utils.types import Document, DocumentType
    DOCUMENT_PROCESSING_AVAILABLE = True
except ImportError:
    DOCUMENT_PROCESSING_AVAILABLE = False
    pytest.skip("Document processing not available", allow_module_level=True)


class TestDocumentIngestion:
    """Test document ingestion functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.embedding_manager = EmbeddingManager()
        self.session_id = "test-session-123"
    
    def test_pdf_processing(self):
        """Test PDF document processing."""
        # Create a temporary PDF file for testing
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            # Create a simple PDF content (this would normally be a real PDF)
            # For testing, we'll mock the PDF processing
            tmp_file_path = tmp_file.name
        
        try:
            with patch('fitz.open') as mock_fitz:
                # Mock PDF document
                mock_doc = Mock()
                mock_doc.page_count = 2
                mock_doc.close = Mock()
                
                # Mock pages
                mock_page1 = Mock()
                mock_page1.get_text.return_value = "This is page 1 content"
                mock_page2 = Mock()
                mock_page2.get_text.return_value = "This is page 2 content"
                
                mock_doc.__getitem__.side_effect = [mock_page1, mock_page2]
                mock_fitz.return_value = mock_doc
                
                # Test PDF processing
                documents = self.embedding_manager.process_pdf(tmp_file_path, self.session_id)
                
                # Assertions
                assert len(documents) == 2
                assert all(isinstance(doc, Document) for doc in documents)
                assert all(doc.metadata['session_id'] == self.session_id for doc in documents)
                assert all(doc.metadata['type'] == 'pdf_page' for doc in documents)
                
        finally:
            # Clean up
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    def test_docx_processing(self):
        """Test DOCX document processing."""
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
            tmp_file_path = tmp_file.name
        
        try:
            with patch('docx.Document') as mock_docx:
                # Mock DOCX document
                mock_doc = Mock()
                mock_para1 = Mock()
                mock_para1.text = "This is paragraph 1"
                mock_para2 = Mock()
                mock_para2.text = "This is paragraph 2"
                mock_doc.paragraphs = [mock_para1, mock_para2]
                mock_docx.return_value = mock_doc
                
                # Test DOCX processing
                documents = self.embedding_manager.process_docx(tmp_file_path, self.session_id)
                
                # Assertions
                assert len(documents) > 0
                assert all(isinstance(doc, Document) for doc in documents)
                assert all(doc.metadata['session_id'] == self.session_id for doc in documents)
                assert all(doc.metadata['type'] == 'docx_chunk' for doc in documents)
                
        finally:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    def test_markdown_processing(self):
        """Test Markdown document processing."""
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False, mode='w') as tmp_file:
            tmp_file.write("# Test Markdown\n\nThis is a test markdown file.\n\n## Section 2\n\nMore content here.")
            tmp_file_path = tmp_file.name
        
        try:
            # Test Markdown processing
            documents = self.embedding_manager.process_markdown(tmp_file_path, self.session_id)
            
            # Assertions
            assert len(documents) > 0
            assert all(isinstance(doc, Document) for doc in documents)
            assert all(doc.metadata['session_id'] == self.session_id for doc in documents)
            assert all(doc.metadata['type'] == 'markdown_chunk' for doc in documents)
            
        finally:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    def test_website_processing(self):
        """Test website URL processing."""
        test_url = "https://example.com/test"
        
        with patch('requests.get') as mock_get:
            # Mock HTTP response
            mock_response = Mock()
            mock_response.content = b"<html><body><h1>Test Page</h1><p>This is test content.</p></body></html>"
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            with patch('bs4.BeautifulSoup') as mock_soup:
                # Mock BeautifulSoup
                mock_soup_instance = Mock()
                mock_soup_instance.get_text.return_value = "Test Page This is test content."
                mock_soup.return_value = mock_soup_instance
                
                # Test website processing
                documents = self.embedding_manager.process_website(test_url, self.session_id)
                
                # Assertions
                assert len(documents) > 0
                assert all(isinstance(doc, Document) for doc in documents)
                assert all(doc.metadata['session_id'] == self.session_id for doc in documents)
                assert all(doc.metadata['type'] == 'website_chunk' for doc in documents)
                assert all(doc.metadata['url'] == test_url for doc in documents)
    
    def test_document_indexing(self):
        """Test adding documents to index."""
        # Create test documents
        test_documents = [
            Document(
                text="Test document 1",
                metadata={"type": "test", "session_id": self.session_id}
            ),
            Document(
                text="Test document 2",
                metadata={"type": "test", "session_id": self.session_id}
            )
        ]
        
        # Test adding documents to index
        with patch.object(self.embedding_manager, 'embeddings', None):
            # Mock the case where embeddings are not available
            result = self.embedding_manager.add_documents_to_index(test_documents, self.session_id)
            assert result is False
        
        # Test with simple storage
        result = self.embedding_manager._add_documents_simple(test_documents, self.session_id)
        assert result is True
        assert self.session_id in self.embedding_manager.documents
        assert len(self.embedding_manager.documents[self.session_id]) == 2
    
    def test_unsupported_file_type(self):
        """Test handling of unsupported file types."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_file_path = tmp_file.name
        
        try:
            # This should raise an exception for unsupported file types
            with pytest.raises(Exception):
                self.embedding_manager.process_pdf(tmp_file_path, self.session_id)
                
        finally:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    def test_document_metadata(self):
        """Test document metadata structure."""
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False, mode='w') as tmp_file:
            tmp_file.write("# Test\n\nContent here.")
            tmp_file_path = tmp_file.name
        
        try:
            documents = self.embedding_manager.process_markdown(tmp_file_path, self.session_id)
            
            for doc in documents:
                assert 'session_id' in doc.metadata
                assert 'type' in doc.metadata
                assert 'chunk_index' in doc.metadata
                assert 'file_path' in doc.metadata
                assert 'word_count' in doc.metadata
                
        finally:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)


if __name__ == "__main__":
    pytest.main([__file__])
