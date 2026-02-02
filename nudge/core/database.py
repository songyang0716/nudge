"""Database initialization and session management."""
from pathlib import Path

from platformdirs import user_data_dir
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from nudge.core.models import Base


class Database:
    """Database manager for the Nudge application."""

    def __init__(self, db_path: str | None = None):
        """Initialize database connection.
        
        Args:
            db_path: Optional custom database path. If None, uses default location.
        """
        if db_path is None:
            # Use platform-specific data directory
            data_dir = Path(user_data_dir("Nudge", "Nudge"))
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(data_dir / "nudge.db")
        
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        
        # Create all tables
        Base.metadata.create_all(self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session.
        
        Returns:
            SQLAlchemy session object
        """
        return self.SessionLocal()
    
    def close(self):
        """Close database connection."""
        self.engine.dispose()


# Global database instance
_db_instance: Database | None = None


def get_database(db_path: str | None = None) -> Database:
    """Get or create the global database instance.
    
    Args:
        db_path: Optional custom database path
        
    Returns:
        Database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
    return _db_instance
