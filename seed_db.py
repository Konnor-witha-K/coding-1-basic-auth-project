#!/usr/bin/env python3
# Seed the database with sample data.
# Run this script once with: python seed_db.py

# Once you have seeded your data, you can run sqlite3 users.db in the terminal
# This opens a sqlite3 shell and you can run commands like:
# - .tables to see all tables
# - SELECT * FROM users; to see all users
# - .exit to exit the shell
# *Note: If you try to seed data and get an error about "UNIQUE constraint failed: users.username", it means you have already seeded the database.
# If you need to seed the database again, simply delete the users.db file and run the seed script again.

from database import get_db, init_db
import bcrypt

def seed_database():
    """Add sample users to the database"""
    init_db()  # Ensure tables are created
    
    conn = get_db()
    
    # Sample users with passwords
    sample_users = [
        ("alice", "Password123!"),
        ("bob", "SecurePass456@"),
        ("charlie", "MyPassword789#"),
    ]
    
    # Sample holidays with dates
    sample_holidays = [
        ("Christmas Day", "December 25th"),
        ("New Year's Day", "January 1st"),
        ("Independence Day", "July 4th"),
    ]

    try:
        for username, password in sample_users:
            hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            conn.execute(
                "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
                (username, hashed_pw)
            )
            print(f"Created user: {username}")

        for name, date in sample_holidays:
            conn.execute(
                "INSERT OR IGNORE INTO holidays (name, date) VALUES (?, ?)",
                (name, date)
            )
            print(f"Added holiday: {name}")

        conn.commit()
        print("\nDatabase seeding complete!")
    
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    seed_database()