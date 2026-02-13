"""Fix role values to use uppercase (ADMIN/EMPLOYEE instead of admin/employee)"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.db.base import SessionLocal

def fix_role_values():
    """Update role values from uppercase to lowercase to match enum values"""
    db = SessionLocal()
    try:
        # Update uppercase 'ADMIN' to lowercase 'admin'
        result = db.execute(text("UPDATE users SET role = 'admin' WHERE role = 'ADMIN'"))
        admin_count = result.rowcount
        
        # Update uppercase 'EMPLOYEE' to lowercase 'employee'
        result = db.execute(text("UPDATE users SET role = 'employee' WHERE role = 'EMPLOYEE'"))
        employee_count = result.rowcount
        
        # Set default role for any NULL values
        result = db.execute(text("UPDATE users SET role = 'employee' WHERE role IS NULL"))
        null_count = result.rowcount
        
        db.commit()
        
        print("✅ Role values updated successfully!")
        print(f"   - Updated {admin_count} ADMIN roles to 'admin'")
        print(f"   - Updated {employee_count} EMPLOYEE roles to 'employee'")
        print(f"   - Set {null_count} NULL roles to 'employee'")
        
        # Show current users with roles
        result = db.execute(text("SELECT id, username, role FROM users"))
        users = result.fetchall()
        
        print("\n📋 Current users:")
        for user in users:
            print(f"   ID {user[0]}: {user[1]} -> {user[2]}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Failed to update roles: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_role_values()
