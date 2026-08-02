"""Database connector - manages connections to PostgreSQL and SQLite"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Optional, Dict, Any, List, Generator
from contextlib import contextmanager
import logging
from datetime import datetime, timedelta
from ..config import settings

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """Production-ready database connector with connection pooling"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or settings.DATABASE_URL
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize database engine with connection pooling"""
        
        if 'sqlite' in self.database_url:
            # SQLite configuration
            self.engine = create_engine(
                self.database_url,
                connect_args={'check_same_thread': False},
                echo=False
            )
        else:
            # PostgreSQL configuration
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False
            )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info(f"✅ Database connected: {self.database_url.split('@')[-1] if '@' in self.database_url else self.database_url}")
    
    @contextmanager
    def get_session(self) -> Session:
        """Get database session with context manager"""
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute raw SQL query and return results"""
        
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            
            if result.returns_rows:
                return [dict(row._mapping) for row in result]
            return []
    
    def execute_many(self, query: str, params_list: List[Dict]) -> int:
        """Execute batch insert/update"""
        
        with self.get_session() as session:
            for params in params_list:
                session.execute(text(query), params)
            return len(params_list)
    
    def check_health(self) -> Dict:
        """Check database health"""
        
        try:
            with self.get_session() as session:
                if 'sqlite' in self.database_url:
                    session.execute(text("SELECT 1"))
                else:
                    session.execute(text("SELECT 1"))
            
            return {
                'status': 'healthy',
                'type': 'sqlite' if 'sqlite' in self.database_url else 'postgresql',
                'url': self.database_url.split('@')[-1] if '@' in self.database_url else 'connected'
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def get_table_info(self, table_name: str) -> List[Dict]:
        """Get table schema information"""
        
        if 'sqlite' in self.database_url:
            query = f"PRAGMA table_info({table_name})"
        else:
            query = """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = :table_name
            """
        
        return self.execute_query(query, {'table_name': table_name})
    
    def vacuum(self):
        """Optimize database (SQLite specific)"""
        
        if 'sqlite' in self.database_url:
            self.execute_query("VACUUM")
            logger.info("Database vacuum completed")
    
    def backup(self, backup_path: str) -> bool:
        """Create database backup"""
        
        if 'sqlite' in self.database_url:
            import shutil
            try:
                shutil.copy2(self.database_url.replace('sqlite:///', ''), backup_path)
                logger.info(f"Database backed up to {backup_path}")
                return True
            except Exception as e:
                logger.error(f"Backup failed: {e}")
                return False
        else:
            logger.warning("PostgreSQL backup not implemented in this connector")
            return False


class CacheConnector:
    """Simple in-memory cache (can be replaced with Redis)"""
    
    def __init__(self):
        self.cache = {}
        self.ttl = {}
    
    def set(self, key: str, value: Any, expire_seconds: int = 3600):
        """Set cache value with TTL"""
        
        self.cache[key] = value
        self.ttl[key] = datetime.now() + timedelta(seconds=expire_seconds)
    
    def get(self, key: str) -> Optional[Any]:
        """Get cache value if not expired"""
        
        if key in self.cache:
            if datetime.now() < self.ttl[key]:
                return self.cache[key]
            else:
                del self.cache[key]
                del self.ttl[key]
        return None
    
    def delete(self, key: str):
        """Delete cache key"""
        
        if key in self.cache:
            del self.cache[key]
            del self.ttl[key]
    
    def clear(self):
        """Clear all cache"""
        
        self.cache.clear()
        self.ttl.clear()
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        
        return {
            'size': len(self.cache),
            'keys': list(self.cache.keys())
        }