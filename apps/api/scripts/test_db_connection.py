import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def test_connection():
    if not DATABASE_URL:
        print("[FAIL] DATABASE_URL not found in .env file.")
        return False

    print(f"Testing database connection to: {DATABASE_URL.split('@')[-1]}...")
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();")).fetchone()
            print("==================================================")
            print("[SUCCESS] Connected to Supabase PostgreSQL!")
            print(f"Database Version: {result[0]}")
            print("==================================================")
        return True
    except Exception as e:
        print(f"[FAIL] Database connection error: {str(e)}")
        # Check if direct port 5432 is blocked and suggest connection pooler
        if "timeout" in str(e).lower() or "connection refused" in str(e).lower():
            print("\nTIP: If port 5432 has network timeout on IPv4, use the Supabase connection pooler on port 6543.")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
