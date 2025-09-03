"""
Database management module for RAG Analytics System
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    data_source_type = Column(String)  # 'excel', 'database'
    data_source_info = Column(Text)  # JSON string
    schema_info = Column(Text)  # JSON string
    last_activity = Column(DateTime, default=datetime.utcnow)

class Query(Base):
    __tablename__ = "queries"
    
    id = Column(String, primary_key=True)
    session_id = Column(String)
    question = Column(Text)
    generated_query = Column(Text)
    query_type = Column(String)  # 'sql', 'pandas'
    execution_time = Column(Integer)  # milliseconds
    row_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    result_data = Column(Text)  # JSON string

class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./rag_analytics.db")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # Initialize SQLAlchemy
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
        
        # Initialize Redis
        try:
            self.redis_client = redis.from_url(self.redis_url)
            self.redis_client.ping()
        except:
            self.redis_client = None
    
    def get_db(self):
        """Get database session"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    async def create_session(self, data_source_type: str, data_source_info: Dict, schema_info: Dict) -> str:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        
        db = self.SessionLocal()
        try:
            session = Session(
                id=session_id,
                data_source_type=data_source_type,
                data_source_info=json.dumps(data_source_info),
                schema_info=json.dumps(schema_info)
            )
            db.add(session)
            db.commit()
            
            # Cache session data in Redis
            if self.redis_client:
                cache_data = {
                    "data_source_type": data_source_type,
                    "data_source_info": data_source_info,
                    "schema_info": schema_info
                }
                self.redis_client.setex(
                    f"session:{session_id}",
                    3600,  # 1 hour
                    json.dumps(cache_data)
                )
            
            return session_id
        finally:
            db.close()
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        # Try Redis first
        if self.redis_client:
            cached = self.redis_client.get(f"session:{session_id}")
            if cached:
                return json.loads(cached)
        
        # Fallback to database
        db = self.SessionLocal()
        try:
            session = db.query(Session).filter(Session.id == session_id).first()
            if session:
                return {
                    "id": session.id,
                    "data_source_type": session.data_source_type,
                    "data_source_info": json.loads(session.data_source_info),
                    "schema_info": json.loads(session.schema_info),
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat()
                }
            return None
        finally:
            db.close()
    
    async def save_query(self, session_id: str, question: str, generated_query: str, 
                        query_type: str, execution_time: int, row_count: int, 
                        result_data: List[Dict]) -> str:
        """Save query execution result"""
        query_id = str(uuid.uuid4())
        
        db = self.SessionLocal()
        try:
            query = Query(
                id=query_id,
                session_id=session_id,
                question=question,
                generated_query=generated_query,
                query_type=query_type,
                execution_time=execution_time,
                row_count=row_count,
                result_data=json.dumps(result_data)
            )
            db.add(query)
            
            # Update session last activity
            session = db.query(Session).filter(Session.id == session_id).first()
            if session:
                session.last_activity = datetime.utcnow()
            
            db.commit()
            return query_id
        finally:
            db.close()
    
    async def get_dashboard_data(self, session_id: str) -> Dict:
        """Get dashboard data for a session"""
        db = self.SessionLocal()
        try:
            # Get session info
            session = db.query(Session).filter(Session.id == session_id).first()
            if not session:
                raise ValueError("Session not found")
            
            # Get recent queries
            queries = db.query(Query).filter(
                Query.session_id == session_id
            ).order_by(Query.created_at.desc()).limit(10).all()
            
            query_history = []
            for query in queries:
                query_history.append({
                    "id": query.id,
                    "question": query.question,
                    "query_type": query.query_type,
                    "execution_time": query.execution_time,
                    "row_count": query.row_count,
                    "created_at": query.created_at.isoformat()
                })
            
            return {
                "session": {
                    "id": session.id,
                    "data_source_type": session.data_source_type,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat()
                },
                "query_history": query_history,
                "schema_info": json.loads(session.schema_info)
            }
        finally:
            db.close()
    
    async def list_sessions(self) -> List[Dict]:
        """List all sessions"""
        db = self.SessionLocal()
        try:
            sessions = db.query(Session).order_by(Session.last_activity.desc()).limit(50).all()
            
            session_list = []
            for session in sessions:
                session_list.append({
                    "id": session.id,
                    "data_source_type": session.data_source_type,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat()
                })
            
            return session_list
        finally:
            db.close()
    
    async def get_query_result(self, query_id: str) -> Optional[Dict]:
        """Get specific query result"""
        db = self.SessionLocal()
        try:
            query = db.query(Query).filter(Query.id == query_id).first()
            if query:
                return {
                    "id": query.id,
                    "session_id": query.session_id,
                    "question": query.question,
                    "generated_query": query.generated_query,
                    "query_type": query.query_type,
                    "execution_time": query.execution_time,
                    "row_count": query.row_count,
                    "result_data": json.loads(query.result_data),
                    "created_at": query.created_at.isoformat()
                }
            return None
        finally:
            db.close()
