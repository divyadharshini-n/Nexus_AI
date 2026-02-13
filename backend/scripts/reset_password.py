"""Reset test user password to a known value"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.base import SessionLocal
from app.db.models import User
from app.utils.security_utils import get_password_hash

db = SessionLocal()

# Get test user
user = db.query(User).filter(User.username == "testuser").first()

if user:
    print(f"Found user: {user.username}")
    
    # Set new password
    new_password = "password123"
    user.hashed_password = get_password_hash(new_password)
    
    db.commit()
    
    print(f"\n✅ Password reset successful!")
    print(f"\n📝 LOGIN CREDENTIALS:")
    print(f"   Username: testuser")
    print(f"   Password: password123")
    print(f"   Email: {user.email}")
    print(f"\nYou can now login with these credentials!")
else:
    print("❌ User 'testuser' not found")
    print("\nCreating new test user...")
    
    new_user = User(
        username="testuser",
        email="testuser@gmail.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        is_active=True,
        is_superuser=False
    )
    db.add(new_user)
    db.commit()
    
    print(f"\n✅ New user created!")
    print(f"\n📝 LOGIN CREDENTIALS:")
    print(f"   Username: testuser")
    print(f"   Password: password123")
    print(f"   Email: testuser@gmail.com")

db.close()
