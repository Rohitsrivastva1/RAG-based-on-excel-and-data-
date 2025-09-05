"""
Test settings configuration and validation.
"""

import pytest
import os
from unittest.mock import patch
from backend.settings import Settings, get_settings


class TestSettings:
    """Test settings configuration."""
    
    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        
        # Test default values
        assert settings.log_level == "INFO"
        assert settings.log_format == "json"
        assert settings.max_file_size_mb == 10
        assert settings.max_rows_indexable == 10000
        assert settings.top_k_retrieval == 5
        assert settings.llm_max_tokens == 4096
        assert settings.enable_embeddings is True
        assert settings.enable_llm is True
        assert settings.enable_database is True
        assert settings.enable_visualization is True
        assert settings.enable_background_indexing is True
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.reload is False
    
    def test_environment_variable_override(self):
        """Test settings override from environment variables."""
        with patch.dict(os.environ, {
            'LOG_LEVEL': 'DEBUG',
            'MAX_FILE_SIZE_MB': '20',
            'MAX_ROWS_INDEXABLE': '5000',
            'HOST': '127.0.0.1',
            'PORT': '9000'
        }):
            settings = Settings()
            
            assert settings.log_level == "DEBUG"
            assert settings.max_file_size_mb == 20
            assert settings.max_rows_indexable == 5000
            assert settings.host == "127.0.0.1"
            assert settings.port == 9000
    
    def test_api_key_validation(self):
        """Test API key validation."""
        # Test with no API keys
        settings = Settings()
        assert settings.openai_api_key is None
        assert settings.google_api_key is None
        
        # Test with OpenAI key
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            settings = Settings()
            assert settings.openai_api_key == 'test-key'
        
        # Test with Google key
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test-google-key'}):
            settings = Settings()
            assert settings.google_api_key == 'test-google-key'
    
    def test_database_url_validation(self):
        """Test database URL validation."""
        # Test with no database URL
        settings = Settings()
        assert settings.database_url is None
        
        # Test with PostgreSQL URL
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/db'
        }):
            settings = Settings()
            assert settings.database_url == 'postgresql://user:pass@localhost:5432/db'
        
        # Test with MySQL URL
        with patch.dict(os.environ, {
            'DATABASE_URL': 'mysql://user:pass@localhost:3306/db'
        }):
            settings = Settings()
            assert settings.database_url == 'mysql://user:pass@localhost:3306/db'
    
    def test_redis_url_validation(self):
        """Test Redis URL validation."""
        # Test default Redis URL
        settings = Settings()
        assert settings.redis_url == "redis://localhost:6379/0"
        
        # Test custom Redis URL
        with patch.dict(os.environ, {
            'REDIS_URL': 'redis://user:pass@localhost:6379/1'
        }):
            settings = Settings()
            assert settings.redis_url == 'redis://user:pass@localhost:6379/1'
    
    def test_cors_origins_parsing(self):
        """Test CORS origins parsing."""
        # Test default CORS origins
        settings = Settings()
        assert settings.allowed_origins == ["*"]
        
        # Test single origin
        with patch.dict(os.environ, {'CORS_ORIGINS': 'http://localhost:3000'}):
            settings = Settings()
            assert settings.allowed_origins == ["http://localhost:3000"]
        
        # Test multiple origins
        with patch.dict(os.environ, {
            'CORS_ORIGINS': 'http://localhost:3000,https://example.com,https://app.com'
        }):
            settings = Settings()
            assert settings.allowed_origins == [
                "http://localhost:3000",
                "https://example.com", 
                "https://app.com"
            ]
    
    def test_embedding_model_configuration(self):
        """Test embedding model configuration."""
        # Test default embedding model
        settings = Settings()
        assert settings.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
        assert settings.faiss_dim == 384
        
        # Test custom embedding model
        with patch.dict(os.environ, {
            'EMBEDDING_MODEL': 'sentence-transformers/all-mpnet-base-v2',
            'FAISS_DIM': '768'
        }):
            settings = Settings()
            assert settings.embedding_model == 'sentence-transformers/all-mpnet-base-v2'
            assert settings.faiss_dim == 768
    
    def test_limits_validation(self):
        """Test limits validation."""
        # Test valid limits
        settings = Settings()
        assert settings.max_file_size_mb > 0
        assert settings.max_rows_indexable > 0
        assert settings.top_k_retrieval > 0
        assert settings.llm_max_tokens > 0
        
        # Test with custom limits
        with patch.dict(os.environ, {
            'MAX_FILE_SIZE_MB': '50',
            'MAX_ROWS_INDEXABLE': '50000',
            'TOP_K_RETRIEVAL': '10',
            'LLM_MAX_TOKENS': '8192'
        }):
            settings = Settings()
            assert settings.max_file_size_mb == 50
            assert settings.max_rows_indexable == 50000
            assert settings.top_k_retrieval == 10
            assert settings.llm_max_tokens == 8192
    
    def test_feature_flags(self):
        """Test feature flags configuration."""
        # Test all features enabled by default
        settings = Settings()
        assert settings.enable_embeddings is True
        assert settings.enable_llm is True
        assert settings.enable_database is True
        assert settings.enable_visualization is True
        assert settings.enable_background_indexing is True
        
        # Test disabling features
        with patch.dict(os.environ, {
            'ENABLE_EMBEDDINGS': 'false',
            'ENABLE_LLM': 'false',
            'ENABLE_DATABASE': 'false'
        }):
            settings = Settings()
            assert settings.enable_embeddings is False
            assert settings.enable_llm is False
            assert settings.enable_database is False
    
    def test_get_settings_singleton(self):
        """Test get_settings returns singleton instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2
    
    def test_validate_configuration(self):
        """Test configuration validation."""
        settings = Settings()
        warnings = settings.validate_configuration()
        
        # Should have warnings for missing API keys
        assert len(warnings) > 0
        assert any("API key" in warning for warning in warnings)
    
    def test_validate_configuration_with_keys(self):
        """Test configuration validation with API keys."""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-key',
            'GOOGLE_API_KEY': 'test-google-key'
        }):
            settings = Settings()
            warnings = settings.validate_configuration()
            
            # Should have fewer warnings with API keys
            assert len(warnings) < 3
    
    def test_get_llm_provider(self):
        """Test LLM provider detection."""
        # Test with no API keys
        settings = Settings()
        assert settings.get_llm_provider() == "none"
        
        # Test with OpenAI key
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            settings = Settings()
            assert settings.get_llm_provider() == "openai"
        
        # Test with Google key
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test-google-key'}):
            settings = Settings()
            assert settings.get_llm_provider() == "google"
        
        # Test with both keys (OpenAI takes precedence)
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-key',
            'GOOGLE_API_KEY': 'test-google-key'
        }):
            settings = Settings()
            assert settings.get_llm_provider() == "openai"
    
    def test_development_mode(self):
        """Test development mode configuration."""
        # Test production mode
        settings = Settings()
        assert settings.reload is False
        
        # Test development mode
        with patch.dict(os.environ, {'ENVIRONMENT': 'development'}):
            settings = Settings()
            assert settings.reload is True
    
    def test_logging_configuration(self):
        """Test logging configuration."""
        # Test default logging
        settings = Settings()
        assert settings.log_level == "INFO"
        assert settings.log_format == "json"
        
        # Test custom logging
        with patch.dict(os.environ, {
            'LOG_LEVEL': 'DEBUG',
            'LOG_FORMAT': 'text'
        }):
            settings = Settings()
            assert settings.log_level == "DEBUG"
            assert settings.log_format == "text"
    
    def test_server_configuration(self):
        """Test server configuration."""
        # Test default server config
        settings = Settings()
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        
        # Test custom server config
        with patch.dict(os.environ, {
            'HOST': '127.0.0.1',
            'PORT': '9000'
        }):
            settings = Settings()
            assert settings.host == "127.0.0.1"
            assert settings.port == 9000
    
    def test_negative_values_handling(self):
        """Test handling of negative values."""
        with patch.dict(os.environ, {
            'MAX_FILE_SIZE_MB': '-1',
            'MAX_ROWS_INDEXABLE': '-100',
            'TOP_K_RETRIEVAL': '-5'
        }):
            # Should not raise error, but values should be handled appropriately
            settings = Settings()
            # The actual behavior depends on Pydantic validation
            # This test ensures no exceptions are raised
            assert settings is not None
    
    def test_empty_string_handling(self):
        """Test handling of empty strings."""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': '',
            'GOOGLE_API_KEY': '',
            'DATABASE_URL': ''
        }):
            settings = Settings()
            assert settings.openai_api_key is None
            assert settings.google_api_key is None
            assert settings.database_url is None
