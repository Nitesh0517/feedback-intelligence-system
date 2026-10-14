from typing import Generator, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
from app.core.logging import logger

engine_kwargs = {
    "pool_pre_ping": True,
}

if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
    engine_kwargs["pool_recycle"] = 1800

engine = create_engine(
    settings.DATABASE_URL,
    **engine_kwargs,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator:
    """Dependency for obtaining database sessions per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Checks whether the database is responsive."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database readiness check failed: {str(e)}")
        return False


def check_redis_connection() -> Optional[bool]:
    """Checks whether Redis is responsive if configured and not running under testing mode."""
    if not settings.REDIS_URL or settings.ENVIRONMENT == "testing":
        return None
    try:
        import redis
        client = redis.Redis.from_url(settings.REDIS_URL, socket_timeout=1.0)
        return bool(client.ping())
    except Exception as e:
        logger.warning(f"Redis readiness ping failed: {str(e)}")
        return False
