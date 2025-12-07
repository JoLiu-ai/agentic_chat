"""
Database connection and session management
"""
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from app.db.models import Base
from app.core.config import settings
import logging
import time

logger = logging.getLogger(__name__)

# Create engine with appropriate settings
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if 'sqlite' in settings.DATABASE_URL else {},
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # 连接前ping，确保连接有效
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 慢查询监控
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """记录SQL执行开始时间"""
    conn.info.setdefault('query_start_time', []).append(time.time())


@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """记录SQL执行时间并检测慢查询"""
    if not conn.info.get('query_start_time'):
        return
    
    total = time.time() - conn.info['query_start_time'].pop(-1)
    
    if total > settings.SLOW_QUERY_THRESHOLD:
        request_id = "system"
        if context:
            request_id = getattr(context, "request_id", "system")
        
        logger.warning(
            f"慢查询检测: {total:.3f}s\n"
            f"SQL: {statement[:200]}...",
            extra={"request_id": request_id}
        )


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database initialized with SQLAlchemy ORM")


def close_db():
    """关闭数据库连接"""
    try:
        engine.dispose()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


@contextmanager
def get_db() -> Session:
    """
    Get database session context manager
    
    Usage:
        with get_db() as db:
            # Your database operations
            db.query(...)
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
