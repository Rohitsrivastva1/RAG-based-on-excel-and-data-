"""
Embeddings and Vector Index Management
Handles FAISS vector store creation and management for RAG
"""

import os
import pickle
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import faiss
    # Try different import paths for LlamaIndex
    try:
        from llama_index.core import VectorStoreIndex, Document, StorageContext
    except ImportError:
        try:
            from llama_index import VectorStoreIndex, Document, StorageContext
        except ImportError:
            from llama_index.core.indices import VectorStoreIndex
            from llama_index.core.schema import Document
            from llama_index.core.storage import StorageContext
    
    try:
        from llama_index.vector_stores.faiss import FaissVectorStore
    except ImportError:
        from llama_index.vector_stores import FaissVectorStore
    
    try:
        from llama_index.embeddings.openai import OpenAIEmbedding
    except ImportError:
        from llama_index.embeddings import OpenAIEmbedding
    
    try:
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    except ImportError:
        from llama_index.embeddings import HuggingFaceEmbedding
    
    FAISS_AVAILABLE = True
    print("✅ FAISS and LlamaIndex loaded successfully")
except ImportError as e:
    FAISS_AVAILABLE = False
    raise RuntimeError(
        f"❌ FAISS or LlamaIndex not available: {e}\n"
        "Please install required packages:\n"
        "  pip install faiss-cpu llama-index\n"
        "Or for GPU support:\n"
        "  pip install faiss-gpu llama-index"
    )

from dotenv import load_dotenv
load_dotenv()

class EmbeddingManager:
    """Manages embeddings and vector indices for RAG"""
    
    def __init__(self, embedding_model: str = "huggingface", dimension: int = 384):
        self.embedding_model = embedding_model
        self.dimension = dimension
        self.indices = {}  # Store indices by session_id
        self.documents = {}  # Store documents by session_id
        
        # Initialize embedding model - use HuggingFace by default (no API key needed)
        if embedding_model == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and api_key != "your_openai_api_key_here":
                self.embedder = OpenAIEmbedding(api_key=api_key)
            else:
                print("Warning: OpenAI API key not found or invalid. Using HuggingFace fallback.")
                self.embedder = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        else:
            self.embedder = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    def create_documents_from_dataframe(self, df: pd.DataFrame, session_id: str) -> List[Document]:
        """Convert DataFrame to LlamaIndex Documents"""
        documents = []
        
        # Create document for schema information
        schema_doc = Document(
            text=f"Dataset schema: Columns are {', '.join(df.columns.tolist())}. "
                 f"Data types: {dict(df.dtypes)}. "
                 f"Sample data: {df.head(3).to_string()}",
            metadata={"type": "schema", "session_id": session_id}
        )
        documents.append(schema_doc)
        
        # Create documents for each row (for small datasets)
        if len(df) <= 1000:  # Only for small datasets
            for idx, row in df.iterrows():
                row_text = f"Row {idx}: " + " ".join([f"{col}={val}" for col, val in row.items()])
                doc = Document(
                    text=row_text,
                    metadata={"type": "row", "row_id": idx, "session_id": session_id}
                )
                documents.append(doc)
        
        # Create summary statistics document
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            stats = df[numeric_cols].describe()
            stats_text = f"Statistical summary: {stats.to_string()}"
            stats_doc = Document(
                text=stats_text,
                metadata={"type": "statistics", "session_id": session_id}
            )
            documents.append(stats_doc)
        
        # Create category analysis documents
        text_cols = df.select_dtypes(include=['object']).columns
        for col in text_cols:
            unique_values = df[col].unique()
            if len(unique_values) <= 20:  # Only for reasonable number of categories
                cat_text = f"Column {col} has categories: {', '.join(map(str, unique_values))}"
                cat_doc = Document(
                    text=cat_text,
                    metadata={"type": "categories", "column": col, "session_id": session_id}
                )
                documents.append(cat_doc)
        
        return documents
    
    def build_index(self, df: pd.DataFrame, session_id: str) -> bool:
        """Build FAISS vector index from DataFrame"""
        try:
            if not FAISS_AVAILABLE:
                raise RuntimeError("FAISS is not available. Please install required packages.")
            
            # Create documents
            documents = self.create_documents_from_dataframe(df, session_id)
            self.documents[session_id] = documents
            
            # Create FAISS vector store
            vector_store = FaissVectorStore(faiss_index=faiss.IndexFlatL2(self.dimension))
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Build index
            index = VectorStoreIndex.from_documents(
                documents, 
                storage_context=storage_context,
                embed_model=self.embedder
            )
            
            self.indices[session_id] = index
            print(f"Built FAISS index for session {session_id} with {len(documents)} documents")
            return True
            
        except Exception as e:
            print(f"Error building index: {e}")
            # Fallback: store documents without indexing
            self.documents[session_id] = self.create_documents_from_dataframe(df, session_id)
            return False
    
    def query_index(self, session_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query the vector index for relevant documents"""
        try:
            if session_id not in self.indices:
                return []
            
            index = self.indices[session_id]
            query_engine = index.as_query_engine(similarity_top_k=top_k)
            response = query_engine.query(query)
            
            results = []
            for node in response.source_nodes:
                results.append({
                    "text": node.text,
                    "score": node.score,
                    "metadata": node.metadata
                })
            
            return results
            
        except Exception as e:
            print(f"Error querying index: {e}")
            return []
    
    def get_context_for_query(self, session_id: str, query: str) -> str:
        """Get relevant context for a query"""
        results = self.query_index(session_id, query, top_k=3)
        
        if not results:
            return "No relevant context found."
        
        context_parts = []
        for result in results:
            context_parts.append(f"Context: {result['text']}")
        
        return "\n".join(context_parts)
    
    def clear_session(self, session_id: str):
        """Clear index and documents for a session"""
        if session_id in self.indices:
            del self.indices[session_id]
        if session_id in self.documents:
            del self.documents[session_id]
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a session's index"""
        info = {
            "has_index": session_id in self.indices,
            "document_count": len(self.documents.get(session_id, [])),
            "embedding_model": self.embedding_model
        }
        return info

# Global instance
embedding_manager = EmbeddingManager()
