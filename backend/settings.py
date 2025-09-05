"""
Centralized configuration management using Pydantic BaseSettings.
Loads environment variables and provides type-safe configuration.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional, List, Union
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys - Only Google/Gemini supported
    google_api_key: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    print("Google api key")
    # Embedding Configuration
    embedding_model: str = Field("sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    faiss_dim: int = Field(384, env="FAISS_DIM")  # Dimension for all-MiniLM-L6-v2
    huggingface_cache_dir: str = Field("./cache/huggingface", env="HUGGINGFACE_CACHE_DIR")
    
    # Database Configuration
    redis_url: Optional[str] = Field(None, env="REDIS_URL")
    database_url: Optional[str] = Field(None, env="DATABASE_URL")
    
    # Resource Limits
    max_rows_indexable: int = Field(10000, env="MAX_ROWS_INDEXABLE")
    max_tokens_llm: int = Field(4000, env="MAX_TOKENS_LLM")
    top_k: int = Field(5, env="TOP_K")
    max_context_length: int = Field(2000, env="MAX_CONTEXT_LENGTH")
    
    # Server Configuration
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    debug: bool = Field(False, env="DEBUG")
    reload: bool = Field(False, env="RELOAD")
    
    # Security Configuration
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:3001",
        env="ALLOWED_ORIGINS"
    )
    max_file_size_mb: int = Field(50, env="MAX_FILE_SIZE_MB")
    execution_timeout_seconds: int = Field(30, env="EXECUTION_TIMEOUT_SECONDS")
    
    # Logging Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_format: str = Field("json", env="LOG_FORMAT")  # json or text
    
    # Feature Flags
    enable_llm_agent: bool = Field(True, env="ENABLE_LLM_AGENT")
    enable_embeddings: bool = Field(True, env="ENABLE_EMBEDDINGS")
    enable_database: bool = Field(True, env="ENABLE_DATABASE")
    enable_visualization: bool = Field(True, env="ENABLE_VISUALIZATION")
    
    # Background Task Configuration
    enable_background_indexing: bool = Field(True, env="ENABLE_BACKGROUND_INDEXING")
    max_background_workers: int = Field(2, env="MAX_BACKGROUND_WORKERS")
    
    @field_validator('allowed_origins', mode='after')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def get_llm_provider(self) -> str:
        """Determine which LLM provider to use based on available API keys."""
        if self.google_api_key:
            return "google"
        else:
            return "none"
    
    def is_llm_available(self) -> bool:
        """Check if any LLM provider is configured."""
        return self.get_llm_provider() != "none"
    
    def get_embedding_provider(self) -> str:
        """Determine which embedding provider to use."""
        return "huggingface"  # Only use HuggingFace embeddings
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration and return list of warnings/errors."""
        warnings = []
        
        if not self.is_llm_available():
            warnings.append("No Google API key configured. LLM features will be disabled.")
        
        if self.max_rows_indexable > 50000:
            warnings.append("MAX_ROWS_INDEXABLE is very high. Consider reducing for better performance.")
        
        if self.top_k > 20:
            warnings.append("TOP_K is high. Consider reducing for better performance.")
        
        if not self.redis_url and self.enable_background_indexing:
            warnings.append("Redis not configured. Background indexing will use in-memory storage.")
        
        return warnings


# Global settings instance
settings = Settings()

# Validate configuration on import
if __name__ == "__main__":
    warnings = settings.validate_configuration()
    if warnings:
        print("Configuration warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("Configuration is valid!")
