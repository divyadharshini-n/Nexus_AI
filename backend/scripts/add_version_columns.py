"""Script to add version tracking columns to stages table"""
import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'plc_platform.db')

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(stages)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Add version_number column if it doesn't exist
    if 'version_number' not in columns:
        cursor.execute("ALTER TABLE stages ADD COLUMN version_number VARCHAR(50) DEFAULT '1.0.0'")
        print("Added column: version_number")
    else:
        print("Column version_number already exists")
    
    # Add last_action column if it doesn't exist
    if 'last_action' not in columns:
        cursor.execute("ALTER TABLE stages ADD COLUMN last_action VARCHAR(100)")
        print("Added column: last_action")
    else:
        print("Column last_action already exists")
    
    # Add last_action_timestamp column if it doesn't exist
    if 'last_action_timestamp' not in columns:
        cursor.execute("ALTER TABLE stages ADD COLUMN last_action_timestamp DATETIME")
        print("Added column: last_action_timestamp")
    else:
        print("Column last_action_timestamp already exists")
    
    # Update existing stages to have version 1.0.0
    cursor.execute("UPDATE stages SET version_number = '1.0.0' WHERE version_number IS NULL")
    
    conn.commit()
    print("\nDatabase schema updated successfully!")
    
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
finally:
    conn.close()
