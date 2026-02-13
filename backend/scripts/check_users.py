"""Check and create test user if needed"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.base import SessionLocal
from app.db.models import User
from app.utils.security_utils import get_password_hash

db = SessionLocal()

# Check existing users
users = db.query(User).all()
print(f"Users in database: {len(users)}")
for u in users:
    print(f"  - {u.username} ({u.email})")

# Create test user if none exists
if len(users) == 0:
    print("\nNo users found. Creating test user...")
    test_user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        is_active=True,
        is_superuser=False
    )
    db.add(test_user)
    db.commit()
    print("✅ Test user created!")
    print("   Username: testuser")
    print("   Password: password123")
else:
    print("\n✅ Users already exist")

db.close()
