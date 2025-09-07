"""
Unit tests for DocumentAgent functionality.
Tests context chunking, error handling, source attribution, and multi-model support.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import the DocumentAgent and related classes
try:
    from agents.document_agent import DocumentAgent, DocumentAnswerParser, DocumentAgentError
    from utils.types import QueryType
except ImportError:
    # Fallback for test environment
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from agents.document_agent import DocumentAgent, DocumentAnswerParser, DocumentAgentError
    from utils.types import QueryType


class TestDocumentAnswerParser:
    """Test the DocumentAnswerParser class."""
    
    def test_parse_success(self):
        """Test successful parsing of LLM response."""
        parser = DocumentAnswerParser()
        response = "This is a test answer with a quote [\"test quote\"]."
        
        result = parser.parse(response)
        
        assert result["success"] is True
        assert result["answer"] == response
        assert result["query_type"] == QueryType.LLM_AGENT.value
        assert "test quote" in result["source_quotes"]
        assert result["error"] is None
    
    def test_parse_with_quotes(self):
        """Test parsing with multiple quote types."""
        parser = DocumentAnswerParser()
        response = 'Answer with "double quotes" and \'single quotes\' and [brackets].'
        
        result = parser.parse(response)
        
        assert len(result["source_quotes"]) >= 3
        assert "double quotes" in result["source_quotes"]
        assert "single quotes" in result["source_quotes"]
        assert "brackets" in result["source_quotes"]
    
    def test_parse_error_handling(self):
        """Test error handling in parsing."""
        parser = DocumentAnswerParser()
        response = "Valid response"
        
        with patch.object(parser, '_extract_quotes', side_effect=Exception("Test error")):
            result = parser.parse(response)
            
            assert result["success"] is False
            assert "Response parsing failed" in result["error"]
            assert result["source_quotes"] == []
    
    def test_extract_quotes(self):
        """Test quote extraction functionality."""
        parser = DocumentAnswerParser()
        text = 'This has "quote1" and \'quote2\' and [quote3] but not short.'
        
        quotes = parser._extract_quotes(text)
        
        assert "quote1" in quotes
        assert "quote2" in quotes
        assert "quote3" in quotes
        assert len(quotes) <= 3  # Should limit to top 3


class TestDocumentAgent:
    """Test the DocumentAgent class."""
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        settings = Mock()
        settings.google_api_key = "test-key"
        settings.llm_provider = "gemini"
        settings.llm_model = "gemini-1.5-flash"
        return settings
    
    @pytest.fixture
    def document_agent(self, mock_settings):
        """Create a DocumentAgent instance for testing."""
        with patch('agents.document_agent.settings', mock_settings):
            with patch('agents.document_agent.LANGCHAIN_AVAILABLE', True):
                with patch('agents.document_agent.ChatGoogleGenerativeAI') as mock_llm:
                    with patch('agents.document_agent.LLMChain') as mock_chain:
                        agent = DocumentAgent()
                        agent.llm = mock_llm.return_value
                        agent.chain = mock_chain.return_value
                        agent.available = True
                        return agent
    
    def test_initialization_success(self, mock_settings):
        """Test successful agent initialization."""
        with patch('agents.document_agent.settings', mock_settings):
            with patch('agents.document_agent.LANGCHAIN_AVAILABLE', True):
                with patch('agents.document_agent.ChatGoogleGenerativeAI') as mock_llm:
                    with patch('agents.document_agent.LLMChain') as mock_chain:
                        agent = DocumentAgent()
                        
                        assert agent.available is True
                        assert agent.llm is not None
                        assert agent.chain is not None
    
    def test_initialization_no_langchain(self, mock_settings):
        """Test initialization when LangChain is not available."""
        with patch('agents.document_agent.settings', mock_settings):
            with patch('agents.document_agent.LANGCHAIN_AVAILABLE', False):
                agent = DocumentAgent()
                
                assert agent.available is False
                assert agent.llm is None
                assert agent.chain is None
    
    def test_initialization_no_api_key(self, mock_settings):
        """Test initialization when API key is missing."""
        mock_settings.google_api_key = None
        
        with patch('agents.document_agent.settings', mock_settings):
            with patch('agents.document_agent.LANGCHAIN_AVAILABLE', True):
                agent = DocumentAgent()
                
                assert agent.available is False
    
    def test_chunk_context_small_text(self, document_agent):
        """Test chunking with small text."""
        small_text = "This is a small text."
        chunks = document_agent._chunk_context(small_text)
        
        assert len(chunks) == 1
        assert chunks[0] == small_text
    
    def test_chunk_context_large_text(self, document_agent):
        """Test chunking with large text."""
        large_text = "This is a large text. " * 1000  # ~25k characters
        chunks = document_agent._chunk_context(large_text, max_chunk_size=2000)
        
        assert len(chunks) > 1
        assert len(chunks) <= 5  # Should limit to top 5 chunks
        assert all(len(chunk) <= 2000 for chunk in chunks)
    
    def test_chunk_context_error_handling(self, document_agent):
        """Test chunking error handling."""
        with patch('agents.document_agent.RecursiveCharacterTextSplitter', side_effect=Exception("Test error")):
            large_text = "Large text " * 1000
            chunks = document_agent._chunk_context(large_text, max_chunk_size=2000)
            
            assert len(chunks) == 1
            assert len(chunks[0]) <= 2000  # Should fallback to truncation
    
    def test_get_relevant_context_small(self, document_agent):
        """Test getting relevant context for small text."""
        small_context = "Small context"
        result = document_agent._get_relevant_context("question", small_context)
        
        assert result == small_context
    
    def test_get_relevant_context_large(self, document_agent):
        """Test getting relevant context for large text."""
        large_context = "Large context " * 1000
        result = document_agent._get_relevant_context("question", large_context)
        
        assert len(result) <= 2000  # Should be chunked
        assert result != large_context  # Should be different from original
    
    def test_process_document_question_success(self, document_agent):
        """Test successful document question processing."""
        mock_result = {
            "answer": "Test answer",
            "success": True,
            "query_type": QueryType.LLM_AGENT.value,
            "source_quotes": ["quote1", "quote2"]
        }
        
        document_agent.chain.run.return_value = mock_result
        
        result = document_agent.process_document_question(
            question="What is this about?",
            context="This is a test document.",
            document_type="pdf",
            session_id="test-session"
        )
        
        assert result["success"] is True
        assert result["answer"] == "Test answer"
        assert result["document_type"] == "pdf"
        assert result["source_quotes"] == ["quote1", "quote2"]
    
    def test_process_document_question_empty_question(self, document_agent):
        """Test processing with empty question."""
        result = document_agent.process_document_question(
            question="",
            context="Test context",
            document_type="pdf"
        )
        
        assert result["success"] is False
        assert result["error"] == DocumentAgentError.CONTEXT_EMPTY
        assert "Question cannot be empty" in result["answer"]
    
    def test_process_document_question_empty_context(self, document_agent):
        """Test processing with empty context."""
        result = document_agent.process_document_question(
            question="What is this?",
            context="",
            document_type="pdf"
        )
        
        assert result["success"] is False
        assert result["error"] == DocumentAgentError.CONTEXT_EMPTY
        assert "No document content available" in result["answer"]
    
    def test_process_document_question_agent_unavailable(self, document_agent):
        """Test processing when agent is unavailable."""
        document_agent.available = False
        
        result = document_agent.process_document_question(
            question="What is this?",
            context="Test context",
            document_type="pdf"
        )
        
        assert result["success"] is False
        assert result["error"] == DocumentAgentError.LLM_UNAVAILABLE
    
    def test_process_document_question_document_too_large(self, document_agent):
        """Test processing with document that's too large."""
        large_context = "Large context " * 10000  # Very large context
        
        result = document_agent.process_document_question(
            question="What is this?",
            context=large_context,
            document_type="pdf"
        )
        
        assert result["success"] is False
        assert result["error"] == DocumentAgentError.DOC_TOO_LARGE
    
    def test_process_document_question_llm_error(self, document_agent):
        """Test processing when LLM call fails."""
        document_agent.chain.run.side_effect = Exception("API timeout")
        
        result = document_agent.process_document_question(
            question="What is this?",
            context="Test context",
            document_type="pdf"
        )
        
        assert result["success"] is False
        assert result["error"] == DocumentAgentError.LLM_TIMEOUT
    
    def test_classify_error_api_key(self, document_agent):
        """Test error classification for API key errors."""
        error = Exception("Invalid API key")
        error_code = document_agent._classify_error(error)
        
        assert error_code == DocumentAgentError.API_KEY_INVALID
    
    def test_classify_error_timeout(self, document_agent):
        """Test error classification for timeout errors."""
        error = Exception("Request timed out")
        error_code = document_agent._classify_error(error)
        
        assert error_code == DocumentAgentError.LLM_TIMEOUT
    
    def test_classify_error_document_size(self, document_agent):
        """Test error classification for document size errors."""
        error = Exception("Document too large")
        error_code = document_agent._classify_error(error)
        
        assert error_code == DocumentAgentError.DOC_TOO_LARGE
    
    def test_classify_error_parsing(self, document_agent):
        """Test error classification for parsing errors."""
        error = Exception("JSON parsing failed")
        error_code = document_agent._classify_error(error)
        
        assert error_code == DocumentAgentError.PARSING_ERROR
    
    def test_create_error_response(self, document_agent):
        """Test error response creation."""
        response = document_agent._create_error_response(
            DocumentAgentError.API_KEY_INVALID,
            "API key is invalid"
        )
        
        assert response["success"] is False
        assert response["error"] == DocumentAgentError.API_KEY_INVALID
        assert response["answer"] == "API key is invalid"
        assert response["query_type"] == QueryType.LLM_AGENT.value
        assert response["source_quotes"] == []
    
    def test_normalize_response(self, document_agent):
        """Test response normalization."""
        raw_result = {
            "answer": "Test answer",
            "success": True,
            "source_quotes": ["quote1"]
        }
        
        normalized = document_agent._normalize_response(raw_result, "pdf")
        
        assert normalized["success"] is True
        assert normalized["answer"] == "Test answer"
        assert normalized["document_type"] == "pdf"
        assert normalized["query_type"] == QueryType.LLM_AGENT.value
        assert normalized["source_quotes"] == ["quote1"]
    
    def test_get_agent_info(self, document_agent):
        """Test agent info retrieval."""
        info = document_agent.get_agent_info()
        
        assert info["available"] is True
        assert info["type"] == "document_agent"
        assert "document_qa" in info["features"]
        assert "context_chunking" in info["features"]
        assert "source_attribution" in info["features"]
        assert "pdf" in info["supported_formats"]
        assert info["max_context_size"] == 10000
        assert info["chunking_enabled"] is True


class TestDocumentAgentIntegration:
    """Integration tests for DocumentAgent."""
    
    def test_full_processing_flow(self):
        """Test the complete document processing flow."""
        with patch('agents.document_agent.settings') as mock_settings:
            mock_settings.google_api_key = "test-key"
            mock_settings.llm_provider = "gemini"
            mock_settings.llm_model = "gemini-1.5-flash"
            
            with patch('agents.document_agent.LANGCHAIN_AVAILABLE', True):
                with patch('agents.document_agent.ChatGoogleGenerativeAI') as mock_llm:
                    with patch('agents.document_agent.LLMChain') as mock_chain:
                        # Mock the chain to return a realistic response
                        mock_chain_instance = Mock()
                        mock_chain_instance.run.return_value = {
                            "answer": "This document is about machine learning [\"ML algorithms\"] and data science [\"data analysis\"]. It covers various topics including neural networks and statistical methods.",
                            "success": True,
                            "query_type": QueryType.LLM_AGENT.value,
                            "source_quotes": ["ML algorithms", "data analysis"]
                        }
                        mock_chain.return_value = mock_chain_instance
                        
                        agent = DocumentAgent()
                        agent.available = True
                        agent.chain = mock_chain_instance
                        
                        # Test with a realistic document context
                        context = """
                        Machine Learning Fundamentals
                        
                        Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data. 
                        ML algorithms are designed to identify patterns in data and make predictions or decisions.
                        
                        Data Science Applications
                        
                        Data science combines statistical analysis, programming, and domain expertise to extract insights from data.
                        Data analysis involves cleaning, transforming, and modeling data to discover useful information.
                        
                        Neural Networks
                        
                        Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes that process information.
                        """
                        
                        result = agent.process_document_question(
                            question="What is this document about?",
                            context=context,
                            document_type="pdf",
                            session_id="test-session"
                        )
                        
                        assert result["success"] is True
                        assert "machine learning" in result["answer"].lower()
                        assert len(result["source_quotes"]) > 0
                        assert result["document_type"] == "pdf"
                        assert result["query_type"] == QueryType.LLM_AGENT.value


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
