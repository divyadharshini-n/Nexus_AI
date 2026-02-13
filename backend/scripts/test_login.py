"""Test login credentials"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.base import SessionLocal
from app.db.models import User
from app.utils.security_utils import verify_password

db = SessionLocal()

# Get test user
user = db.query(User).filter(User.username == "testuser").first()

if user:
    print(f"✅ User found: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Active: {user.is_active}")
    print(f"   Hashed password exists: {bool(user.hashed_password)}")
    
    # Test password verification
    test_passwords = ["password123", "Password123", "testpassword", "test123"]
    
    print("\nTesting passwords:")
    for pwd in test_passwords:
        result = verify_password(pwd, user.hashed_password)
        status = "✅ CORRECT" if result else "❌ Wrong"
        print(f"  {status}: '{pwd}'")
        if result:
            print(f"\n🎉 Working password found: '{pwd}'")
            break
else:
    print("❌ User 'testuser' not found")

db.close()
