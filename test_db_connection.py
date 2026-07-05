# test_db_connection.py
# Run this once to confirm MySQL is connected and tables exist.
# Delete this file before deploying.

import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

def test_connection():
    print("\n--- SecureMed QR: MySQL Connection Test ---\n")

    try:
        conn = mysql.connector.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=int(os.environ.get("DB_PORT", 3306)),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD", ""),
            database=os.environ.get("DB_NAME", "securemed"),
        )
        print("✅ Connected to MySQL successfully")
        print(f"   Host     : {os.environ.get('DB_HOST')}")
        print(f"   Database : {os.environ.get('DB_NAME')}")
        print(f"   User     : {os.environ.get('DB_USER')}")

        cursor = conn.cursor()

        # Confirm tables exist
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\n✅ Tables found: {tables}")

        for expected in ["patients", "access_logs"]:
            if expected in tables:
                print(f"   ✅ {expected} — exists")
            else:
                print(f"   ❌ {expected} — MISSING")

        # Confirm columns on patients table
        print("\n--- patients table columns ---")
        cursor.execute("DESCRIBE patients;")
        for col in cursor.fetchall():
            print(f"   {col[0]:<20} {col[1]}")

        # Confirm columns on access_logs table
        print("\n--- access_logs table columns ---")
        cursor.execute("DESCRIBE access_logs;")
        for col in cursor.fetchall():
            print(f"   {col[0]:<20} {col[1]}")

        cursor.close()
        conn.close()
        print("\n✅ All checks passed. Database is ready for Phase 3.\n")

    except mysql.connector.Error as e:
        print(f"\n❌ Connection failed: {e}")
        print("   Check your .env credentials and confirm MySQL is running.\n")

if __name__ == "__main__":
    test_connection()