"""
Session store for managing user sessions and data.
Supports in-memory storage with optional Redis backend for production.
"""

import uuid
import time
import pickle
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pandas as pd
import logging

logger = logging.getLogger(__name__)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available. Using in-memory session storage.")


class SessionData:
    """Container for session data."""
    
    def __init__(
        self,
        session_id: str,
        data_source: str,
        data: Optional[pd.DataFrame] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None
    ):
        self.session_id = session_id
        self.data_source = data_source
        self.data = data
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.last_accessed = datetime.utcnow()
        self.access_count = 0
    
    def touch(self):
        """Update last accessed time and increment access count."""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'session_id': self.session_id,
            'data_source': self.data_source,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'access_count': self.access_count,
            'has_data': self.data is not None
        }
    
    def get_data_info(self) -> Dict[str, Any]:
        """Get information about the data without loading it."""
        if self.data is None:
            return {'rows': 0, 'columns': 0, 'column_names': []}
        
        return {
            'rows': len(self.data),
            'columns': len(self.data.columns),
            'column_names': self.data.columns.tolist(),
            'dtypes': self.data.dtypes.to_dict(),
            'memory_usage': self.data.memory_usage(deep=True).sum()
        }


class InMemorySessionStore:
    """In-memory session store implementation."""
    
    def __init__(self, max_sessions: int = 1000, session_ttl_hours: int = 24):
        self.sessions: Dict[str, SessionData] = {}
        self.max_sessions = max_sessions
        self.session_ttl = timedelta(hours=session_ttl_hours)
        self._cleanup_interval = 3600  # 1 hour
        self._last_cleanup = time.time()
    
    def create(
        self,
        session_id: Optional[str] = None,
        data: Optional[pd.DataFrame] = None,
        data_source: str = "file",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new session."""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if session_id in self.sessions:
            logger.warning(f"Session {session_id} already exists. Updating.")
        
        # Cleanup old sessions if needed
        self._cleanup_if_needed()
        
        # Check session limit
        if len(self.sessions) >= self.max_sessions:
            self._evict_oldest_session()
        
        session_data = SessionData(
            session_id=session_id,
            data_source=data_source,
            data=data,
            metadata=metadata or {}
        )
        
        self.sessions[session_id] = session_data
        
        logger.info(f"Created session {session_id}", extra={
            'session_id': session_id,
            'data_source': data_source,
            'has_data': data is not None
        })
        
        return session_id
    
    def get(self, session_id: str) -> Optional[SessionData]:
        """Get session data."""
        session = self.sessions.get(session_id)
        if session:
            session.touch()
            logger.debug(f"Accessed session {session_id}")
        return session
    
    def update(
        self,
        session_id: str,
        data: Optional[pd.DataFrame] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update session data."""
        session = self.sessions.get(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found for update")
            return False
        
        if data is not None:
            session.data = data
        if metadata is not None:
            session.metadata.update(metadata)
        
        session.touch()
        logger.info(f"Updated session {session_id}")
        return True
    
    def delete(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session {session_id}")
            return True
        return False
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions."""
        return [session.to_dict() for session in self.sessions.values()]
    
    def get_session_count(self) -> int:
        """Get total number of sessions."""
        return len(self.sessions)
    
    def _cleanup_if_needed(self):
        """Clean up expired sessions if needed."""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        
        self._last_cleanup = now
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if datetime.utcnow() - session.last_accessed > self.session_ttl:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"Cleaned up expired session {session_id}")
    
    def _evict_oldest_session(self):
        """Evict the oldest session to make room."""
        if not self.sessions:
            return
        
        oldest_session = min(
            self.sessions.values(),
            key=lambda s: s.last_accessed
        )
        
        del self.sessions[oldest_session.session_id]
        logger.info(f"Evicted oldest session {oldest_session.session_id}")


class RedisSessionStore:
    """Redis-based session store implementation."""
    
    def __init__(self, redis_url: str, session_ttl_hours: int = 24):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis is required for RedisSessionStore")
        
        self.redis_client = redis.from_url(redis_url)
        self.session_ttl = timedelta(hours=session_ttl_hours)
        self.key_prefix = "session:"
    
    def _get_key(self, session_id: str) -> str:
        """Get Redis key for session."""
        return f"{self.key_prefix}{session_id}"
    
    def create(
        self,
        session_id: Optional[str] = None,
        data: Optional[pd.DataFrame] = None,
        data_source: str = "file",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new session."""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        session_data = SessionData(
            session_id=session_id,
            data_source=data_source,
            data=data,
            metadata=metadata or {}
        )
        
        # Serialize session data
        session_dict = {
            'session_id': session_data.session_id,
            'data_source': session_data.data_source,
            'metadata': session_data.metadata,
            'created_at': session_data.created_at.isoformat(),
            'last_accessed': session_data.last_accessed.isoformat(),
            'access_count': session_data.access_count
        }
        
        # Store session metadata
        self.redis_client.setex(
            f"{self._get_key(session_id)}:meta",
            int(self.session_ttl.total_seconds()),
            json.dumps(session_dict)
        )
        
        # Store DataFrame if provided
        if data is not None:
            # For large DataFrames, we might want to store as parquet
            # For now, we'll pickle it
            pickled_data = pickle.dumps(data)
            self.redis_client.setex(
                f"{self._get_key(session_id)}:data",
                int(self.session_ttl.total_seconds()),
                pickled_data
            )
        
        logger.info(f"Created Redis session {session_id}")
        return session_id
    
    def get(self, session_id: str) -> Optional[SessionData]:
        """Get session data."""
        # Get metadata
        meta_key = f"{self._get_key(session_id)}:meta"
        meta_data = self.redis_client.get(meta_key)
        
        if not meta_data:
            return None
        
        try:
            session_dict = json.loads(meta_data)
            
            # Get DataFrame if it exists
            data_key = f"{self._get_key(session_id)}:data"
            data_bytes = self.redis_client.get(data_key)
            data = None
            
            if data_bytes:
                data = pickle.loads(data_bytes)
            
            # Create SessionData object
            session = SessionData(
                session_id=session_dict['session_id'],
                data_source=session_dict['data_source'],
                data=data,
                metadata=session_dict['metadata'],
                created_at=datetime.fromisoformat(session_dict['created_at'])
            )
            session.last_accessed = datetime.fromisoformat(session_dict['last_accessed'])
            session.access_count = session_dict['access_count']
            
            # Update access time
            session.touch()
            self.redis_client.setex(
                meta_key,
                int(self.session_ttl.total_seconds()),
                json.dumps(session.to_dict())
            )
            
            return session
            
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return None
    
    def update(
        self,
        session_id: str,
        data: Optional[pd.DataFrame] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update session data."""
        session = self.get(session_id)
        if not session:
            return False
        
        if data is not None:
            session.data = data
            # Update data in Redis
            pickled_data = pickle.dumps(data)
            self.redis_client.setex(
                f"{self._get_key(session_id)}:data",
                int(self.session_ttl.total_seconds()),
                pickled_data
            )
        
        if metadata is not None:
            session.metadata.update(metadata)
        
        # Update metadata in Redis
        self.redis_client.setex(
            f"{self._get_key(session_id)}:meta",
            int(self.session_ttl.total_seconds()),
            json.dumps(session.to_dict())
        )
        
        return True
    
    def delete(self, session_id: str) -> bool:
        """Delete a session."""
        meta_key = f"{self._get_key(session_id)}:meta"
        data_key = f"{self._get_key(session_id)}:data"
        
        # Delete both metadata and data
        deleted = self.redis_client.delete(meta_key, data_key)
        return deleted > 0
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions."""
        pattern = f"{self.key_prefix}*:meta"
        keys = self.redis_client.keys(pattern)
        
        sessions = []
        for key in keys:
            meta_data = self.redis_client.get(key)
            if meta_data:
                try:
                    session_dict = json.loads(meta_data)
                    sessions.append(session_dict)
                except Exception as e:
                    logger.error(f"Error loading session from {key}: {e}")
        
        return sessions
    
    def get_session_count(self) -> int:
        """Get total number of sessions."""
        pattern = f"{self.key_prefix}*:meta"
        return len(self.redis_client.keys(pattern))


class SessionStore:
    """Main session store interface."""
    
    def __init__(self, redis_url: Optional[str] = None, **kwargs):
        if redis_url and REDIS_AVAILABLE:
            self.store = RedisSessionStore(redis_url, **kwargs)
            self.store_type = "redis"
        else:
            self.store = InMemorySessionStore(**kwargs)
            self.store_type = "memory"
        
        logger.info(f"Initialized {self.store_type} session store")
    
    def create(
        self,
        session_id: Optional[str] = None,
        data: Optional[pd.DataFrame] = None,
        data_source: str = "file",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new session."""
        return self.store.create(session_id, data, data_source, metadata)
    
    def get(self, session_id: str) -> Optional[SessionData]:
        """Get session data."""
        return self.store.get(session_id)
    
    def update(
        self,
        session_id: str,
        data: Optional[pd.DataFrame] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update session data."""
        return self.store.update(session_id, data, metadata)
    
    def delete(self, session_id: str) -> bool:
        """Delete a session."""
        return self.store.delete(session_id)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions."""
        return self.store.list_sessions()
    
    def get_session_count(self) -> int:
        """Get total number of sessions."""
        return self.store.get_session_count()
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information without loading data."""
        session = self.get(session_id)
        if not session:
            return None
        
        info = session.to_dict()
        info['data_info'] = session.get_data_info()
        return info


# Global session store instance
session_store: Optional[SessionStore] = None


def initialize_session_store(redis_url: Optional[str] = None, **kwargs) -> SessionStore:
    """Initialize the global session store."""
    global session_store
    session_store = SessionStore(redis_url, **kwargs)
    return session_store


def get_session_store() -> SessionStore:
    """Get the global session store instance."""
    if session_store is None:
        raise RuntimeError("Session store not initialized. Call initialize_session_store() first.")
    return session_store


# Example usage and testing
if __name__ == "__main__":
    import pandas as pd
    
    # Test in-memory store
    store = InMemorySessionStore()
    
    # Create test data
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': [10, 20, 30]
    })
    
    # Create session
    session_id = store.create(
        data=df,
        data_source="file",
        metadata={"file_name": "test.csv"}
    )
    
    print(f"Created session: {session_id}")
    
    # Get session
    session = store.get(session_id)
    if session:
        print(f"Session info: {session.to_dict()}")
        print(f"Data info: {session.get_data_info()}")
    
    # List sessions
    sessions = store.list_sessions()
    print(f"Total sessions: {len(sessions)}")
    
    # Delete session
    store.delete(session_id)
    print(f"Sessions after deletion: {store.get_session_count()}")
