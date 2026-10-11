import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def run_migrations():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("[FAIL] DATABASE_URL not found in .env")
        return False

    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    migration_files = [
        base_dir / "supabase" / "migrations" / "20261011000001_initial_enums_and_extensions.sql",
        base_dir / "supabase" / "migrations" / "20261011000002_core_schema.sql",
        base_dir / "supabase" / "migrations" / "20261011000003_rls_policies.sql",
        base_dir / "supabase" / "seed.sql"
    ]

    print(f"Connecting to database at {db_url.split('@')[-1]}...")
    engine = create_engine(db_url, isolation_level="AUTOCOMMIT")

    all_passed = True
    with engine.connect() as conn:
        for file_path in migration_files:
            if not file_path.exists():
                print(f"[MISSING FILE] {file_path}")
                continue

            print(f"\n--- Applying: {file_path.name} ---")
            sql_content = file_path.read_text(encoding="utf-8")
            try:
                conn.execute(text(sql_content))
                print(f"[OK] {file_path.name} applied successfully.")
            except Exception as err:
                print(f"[FAIL] {file_path.name}")
                print(f"Error Details: {str(err)}")
                all_passed = False
                break

    return all_passed

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
