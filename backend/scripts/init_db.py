"""
Initialize Database
Creates all tables from models
"""
import sys
sys.path.append(".")

from app.database import Base, engine
from app.models import User, AuthToken, Meeting

def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
