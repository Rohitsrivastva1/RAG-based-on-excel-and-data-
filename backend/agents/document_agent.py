"""
Document processing agent for handling PDF, DOCX, Markdown, and website content.
This agent is specifically designed for document Q&A, not data analysis.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from utils.types import QueryType
from logging_config import get_logger, log_performance

logger = get_logger(__name__)

# Error codes for better error handling
class DocumentAgentError:
    API_KEY_INVALID = "API_KEY_INVALID"
    LLM_TIMEOUT = "LLM_TIMEOUT"
    DOC_TOO_LARGE = "DOC_TOO_LARGE"
    CONTEXT_EMPTY = "CONTEXT_EMPTY"
    LLM_UNAVAILABLE = "LLM_UNAVAILABLE"
    PARSING_ERROR = "PARSING_ERROR"

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    from langchain_core.output_parsers import BaseOutputParser
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    logger.warning(f"LangChain not available ({e}). Document agent will be disabled.")

try:
    from settings import settings
except ImportError:
    # Fallback for direct execution
    import os
    class Settings:
        google_api_key = os.getenv('GOOGLE_API_KEY', '')
        enable_embeddings = True
        top_k = 3
    settings = Settings()


class DocumentAnswerParser(BaseOutputParser):
    """Parse document Q&A responses with source attribution."""
    
    def parse(self, text: str) -> Dict[str, Any]:
        """Parse the LLM response for document Q&A with quote extraction."""
        try:
            answer = text.strip()
            source_quotes = self._extract_quotes(answer)
            
            return {
                "answer": answer,
                "success": True,
                "query_type": QueryType.LLM_AGENT.value,
                "generated_code": None,  # Documents don't generate code
                "visualization": None,   # Documents don't create visualizations
                "source_quotes": source_quotes,
                "error": None
            }
        except Exception as e:
            logger.error(f"Failed to parse document agent response: {e}")
            return {
                "answer": text.strip(),
                "success": False,
                "query_type": QueryType.LLM_AGENT.value,
                "generated_code": None,
                "visualization": None,
                "source_quotes": [],
                "error": f"Response parsing failed: {str(e)}"
            }
    
    def _extract_quotes(self, text: str) -> List[str]:
        """Extract quoted text from the response."""
        import re
        # Look for quoted text patterns
        quote_patterns = [
            r'"([^"]+)"',  # Double quotes
            r"'([^']+)'",  # Single quotes
            r'\[([^\]]+)\]',  # Square brackets
        ]
        
        quotes = []
        for pattern in quote_patterns:
            matches = re.findall(pattern, text)
            quotes.extend(matches)
        
        # Limit to top 3 quotes and clean them
        return [quote.strip() for quote in quotes[:3] if len(quote.strip()) > 10]


class DocumentAgent:
    """Agent specialized for document Q&A processing."""
    
    def __init__(self):
        self.llm = None
        self.chain = None
        self.available = False
        self.embedding_manager = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the document agent."""
        try:
            if not LANGCHAIN_AVAILABLE:
                logger.warning("LangChain not available. Document agent disabled.")
                return
            
            # Initialize LLM with multi-model support
            self.llm = self._initialize_llm()
            if not self.llm:
                logger.warning("Failed to initialize LLM. Document agent disabled.")
                return
            
            # Initialize embedding manager for session-aware context retrieval
            try:
                from managers.embedding_manager import EmbeddingManager
                self.embedding_manager = EmbeddingManager()
                logger.info("Embedding manager initialized for session-aware document processing")
            except Exception as e:
                logger.warning(f"Failed to initialize embedding manager: {e}")
                self.embedding_manager = None
            
            # Create document-specific prompt template with enhanced source attribution
            prompt_template = PromptTemplate(
                input_variables=["question", "context", "document_type"],
                template="""You are a helpful AI assistant specialized in analyzing and answering questions about documents.

Document Type: {document_type}

Context from documents:
{context}

Question: {question}

Instructions:
1. Answer the question based on the provided document context
2. If the context doesn't contain enough information, say so clearly
3. When providing information, include 1-3 specific quotes from the document in square brackets [like this]
4. Be concise but comprehensive
5. If the question is about data analysis or requires calculations, explain that this is document content, not structured data
6. Focus on factual information from the document rather than general knowledge

Answer:"""
            )
            
            # Create the chain
            self.chain = LLMChain(
                llm=self.llm,
                prompt=prompt_template,
                output_parser=DocumentAnswerParser()
            )
            
            self.available = True
            logger.info("Document agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize document agent: {e}")
            self.available = False
    
    def _initialize_llm(self):
        """Initialize LLM with multi-model support."""
        try:
            # Get model configuration from settings
            llm_provider = getattr(settings, 'llm_provider', 'gemini')
            llm_model = getattr(settings, 'llm_model', 'gemini-1.5-flash')
            
            if llm_provider.lower() == 'gemini':
                if not settings.google_api_key:
                    logger.warning("Google API key not configured for Gemini.")
                    return None
                
                return ChatGoogleGenerativeAI(
                    model=llm_model,
                    google_api_key=settings.google_api_key,
                    temperature=0.1,
                    max_output_tokens=2048
                )
            else:
                logger.warning(f"Unsupported LLM provider: {llm_provider}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            return None
    
    def _chunk_context(self, context: str, max_chunk_size: int = 2000) -> List[str]:
        """Chunk large context into smaller pieces."""
        if len(context) <= max_chunk_size:
            return [context]
        
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=max_chunk_size,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            chunks = text_splitter.split_text(context)
            return chunks[:5]  # Limit to top 5 chunks
        except Exception as e:
            logger.warning(f"Failed to chunk context: {e}")
            return [context[:max_chunk_size]]  # Fallback to truncation
    
    def _get_relevant_context(self, question: str, context: str, session_id: str = None) -> str:
        """Get relevant context chunks based on question and session."""
        try:
            # If context is small, return as is
            if len(context) <= 2000:
                return context
            
            # Try to use embedding manager for better retrieval
            if session_id and self.embedding_manager and self.embedding_manager.embeddings:
                try:
                    # Query the vector store for relevant chunks
                    relevant_docs = self.embedding_manager.query_index(
                        question, session_id, top_k=3
                    )
                    if relevant_docs and len(relevant_docs) > 0:
                        logger.info(f"Retrieved {len(relevant_docs)} relevant documents from vector store")
                        return "\n\n".join([doc.text for doc in relevant_docs])
                    else:
                        logger.info("No relevant documents found in vector store, using chunking")
                except Exception as e:
                    logger.warning(f"Failed to query vector store: {e}")
            
            # Fallback to chunking
            logger.info("Using context chunking as fallback")
            chunks = self._chunk_context(context)
            return "\n\n".join(chunks[:3])  # Use top 3 chunks
            
        except Exception as e:
            logger.warning(f"Failed to get relevant context: {e}")
            return context[:2000]  # Fallback to truncation
    
    def is_available(self) -> bool:
        """Check if the document agent is available."""
        return self.available
    
    def process_document_question(
        self,
        question: str,
        context: str,
        document_type: str = "document",
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Process a document question with enhanced error handling and context processing.
        
        Args:
            question: User question
            context: Relevant document context
            document_type: Type of document (pdf, docx, markdown, url)
            session_id: Session ID for logging and vector store queries
            
        Returns:
            Normalized agent result dictionary with error codes
        """
        print(f"\n📄 DOCUMENT AGENT PROCESSING")
        print(f"   Question: '{question}'")
        print(f"   Document type: {document_type}")
        print(f"   Context length: {len(context)} characters")
        print(f"   Session ID: {session_id}")
        
        # Validate inputs
        if not question or not question.strip():
            return self._create_error_response(
                DocumentAgentError.CONTEXT_EMPTY,
                "Question cannot be empty"
            )
        
        if not self.available:
            print(f"   ❌ Document agent not available")
            return self._create_error_response(
                DocumentAgentError.LLM_UNAVAILABLE,
                "Document processing is not available. Please check the configuration."
            )
        
        # Handle empty context
        if not context or not context.strip():
            return self._create_error_response(
                DocumentAgentError.CONTEXT_EMPTY,
                "No document content available. Please upload a document first."
            )
        
        try:
            start_time = datetime.utcnow()
            print(f"   ⏰ Started processing at: {start_time}")
            
            # Get relevant context chunks
            relevant_context = self._get_relevant_context(question, context, session_id)
            print(f"   📄 Using {len(relevant_context)} characters of context")
            
            # Check for document size limits
            if len(relevant_context) > 10000:  # 10k character limit
                return self._create_error_response(
                    DocumentAgentError.DOC_TOO_LARGE,
                    "Document is too large to process. Please try a smaller document or more specific question."
                )
            
            # Process with the document chain
            result = self.chain.run(
                question=question,
                context=relevant_context,
                document_type=document_type
            )
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # Log performance
            log_performance("document_agent_process", duration_ms=duration * 1000,
                          question_length=len(question),
                          context_length=len(relevant_context),
                          document_type=document_type,
                          session_id=session_id)
            
            print(f"   ✅ Document processing completed")
            print(f"   ⏱️ Processing duration: {duration:.2f} seconds")
            print(f"   📝 Answer preview: {result['answer'][:200]}...")
            
            # Ensure normalized response format
            return self._normalize_response(result, document_type)
            
        except Exception as e:
            error_code = self._classify_error(e)
            logger.error(f"Document agent processing failed: {e}")
            print(f"   ❌ Document processing failed: {e}")
            return self._create_error_response(
                error_code,
                f"Document processing failed: {str(e)}"
            )
    
    def _create_error_response(self, error_code: str, message: str) -> Dict[str, Any]:
        """Create a normalized error response."""
        return {
            "success": False,
            "answer": message,
            "query_type": QueryType.LLM_AGENT.value,
            "generated_code": None,
            "visualization": None,
            "source_quotes": [],
            "error": error_code,
            "document_type": "unknown"
        }
    
    def _classify_error(self, error: Exception) -> str:
        """Classify error types for better error handling."""
        error_str = str(error).lower()
        
        if "api" in error_str and "key" in error_str:
            return DocumentAgentError.API_KEY_INVALID
        elif "timeout" in error_str or "timed out" in error_str:
            return DocumentAgentError.LLM_TIMEOUT
        elif "too large" in error_str or "size" in error_str:
            return DocumentAgentError.DOC_TOO_LARGE
        elif "parse" in error_str or "json" in error_str:
            return DocumentAgentError.PARSING_ERROR
        else:
            return DocumentAgentError.LLM_UNAVAILABLE
    
    def _normalize_response(self, result: Dict[str, Any], document_type: str) -> Dict[str, Any]:
        """Normalize response to ensure consistent schema."""
        return {
            "success": result.get("success", True),
            "answer": result.get("answer", ""),
            "query_type": result.get("query_type", QueryType.LLM_AGENT.value),
            "generated_code": result.get("generated_code"),
            "visualization": result.get("visualization"),
            "source_quotes": result.get("source_quotes", []),
            "error": result.get("error"),
            "document_type": document_type
        }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the document agent."""
        llm_model = "gemini-1.5-flash" if self.llm else None
        if hasattr(settings, 'llm_model'):
            llm_model = settings.llm_model
            
        return {
            "available": self.available,
            "type": "document_agent",
            "llm_model": llm_model,
            "features": [
                "document_qa",
                "text_analysis",
                "context_retrieval",
                "multi_format_support",
                "context_chunking",
                "source_attribution",
                "error_handling",
                "multi_model_support"
            ],
            "supported_formats": ["pdf", "docx", "markdown", "url"],
            "max_context_size": 10000,
            "chunking_enabled": True
        }


# Global document agent instance
document_agent: Optional[DocumentAgent] = None


def initialize_document_agent() -> DocumentAgent:
    """Initialize the global document agent."""
    global document_agent
    document_agent = DocumentAgent()
    return document_agent


def get_document_agent() -> DocumentAgent:
    """Get the global document agent instance."""
    if document_agent is None:
        raise RuntimeError("Document agent not initialized. Call initialize_document_agent() first.")
    return document_agent


# Example usage and testing
if __name__ == "__main__":
    # Test the document agent
    agent = DocumentAgent()
    
    if agent.is_available():
        print("Document agent is available!")
        
        # Test with sample document content
        test_context = """
        This is a sample document about artificial intelligence.
        AI has revolutionized many industries including healthcare, finance, and transportation.
        Machine learning algorithms can process large amounts of data to find patterns.
        Natural language processing allows computers to understand human language.
        """
        
        result = agent.process_document_question(
            question="What are the applications of AI mentioned in this document?",
            context=test_context,
            document_type="pdf"
        )
        
        print(f"Result: {result}")
    else:
        print("Document agent is not available.")
