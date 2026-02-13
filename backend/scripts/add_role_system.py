"""Add role system and project sharing to database"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.db.base import engine, SessionLocal

def add_role_columns():
    """Add role and sharing columns to database"""
    db = SessionLocal()
    try:
        # Add role column to users table
        try:
            db.execute(text("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'employee'"))
            print("✓ Added role column to users table")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("✓ Role column already exists")
            else:
                print(f"Error adding role column: {e}")
        
        # Add created_by column to users table
        try:
            db.execute(text("ALTER TABLE users ADD COLUMN created_by INTEGER"))
            print("✓ Added created_by column to users table")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("✓ Created_by column already exists")
            else:
                print(f"Error adding created_by column: {e}")
        
        # Create project_shares table
        try:
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS project_shares (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    shared_with_user_id INTEGER NOT NULL,
                    shared_by_user_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    FOREIGN KEY (shared_with_user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (shared_by_user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(project_id, shared_with_user_id)
                )
            """))
            print("✓ Created project_shares table")
        except Exception as e:
            print(f"Error creating project_shares table: {e}")
        
        # Set first user as admin if exists
        try:
            result = db.execute(text("SELECT id FROM users ORDER BY id LIMIT 1"))
            first_user = result.fetchone()
            if first_user:
                db.execute(text(f"UPDATE users SET role = 'admin' WHERE id = {first_user[0]}"))
                print(f"✓ Set user ID {first_user[0]} as admin")
        except Exception as e:
            print(f"Error setting admin: {e}")
        
        db.commit()
        print("\n Database migration completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Migration failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_role_columns()
