"""Check all users and their roles"""
import sys
from pathlib import Path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.db.models.user import User

def check_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"\n📋 Total users: {len(users)}\n")
        
        for user in users:
            role_value = user.__dict__.get('role', 'NO ROLE COLUMN')
            print(f"ID {user.id}: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Role (raw db value): {role_value}")
            print(f"  Role (enum): {user.role}")
            print(f"  Role type: {type(user.role)}")
            print()
        
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
