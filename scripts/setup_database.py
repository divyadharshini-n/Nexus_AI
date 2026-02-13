import sys
from pathlib import Path
from dotenv import load_dotenv

# Get the root directory
root_dir = Path(__file__).parent.parent
backend_dir = root_dir / "backend"

# Load .env file from backend directory
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

# Add backend to path
sys.path.append(str(backend_dir))

from app.db.base import Base, engine
from app.db.models import *

def init_db():
    """Create all database tables"""
    print(f"Loading environment from: {env_path}")
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    init_db()