import sys
from pathlib import Path
from dotenv import load_dotenv

# Setup
root_dir = Path(__file__).parent.parent
backend_dir = root_dir / "backend"
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)
sys.path.append(str(backend_dir))

from app.db.base import SessionLocal
from app.db.repositories.user_repository import UserRepository


def create_test_user():
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        
        # Check if user exists
        existing_user = user_repo.get_by_username("testuser")
        if existing_user:
            print("✅ Test user already exists!")
            print(f"   Username: testuser")
            print(f"   Email: {existing_user.email}")
            return
        
        # Create test user
        user = user_repo.create(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            full_name="Test User"
        )
        
        print("✅ Test user created successfully!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Password: testpassword123")
        
    finally:
        db.close()


if __name__ == "__main__":
    create_test_user()