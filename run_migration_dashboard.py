"""
Helper script to display the migration SQL for easy copy-paste into Supabase Dashboard.
This is the recommended way to run migrations on remote Supabase instances.
"""
from pathlib import Path

def display_migration():
    """Display the migration SQL with instructions."""
    migration_file = Path(__file__).parent / "supabase" / "migrations" / "001_initial_schema.sql"
    
    if not migration_file.exists():
        print(f"Error: Migration file not found at {migration_file}")
        return
    
    print("=" * 80)
    print("SUPABASE MIGRATION: 001_initial_schema.sql")
    print("=" * 80)
    print("\nINSTRUCTIONS:")
    print("1. Go to your Supabase Dashboard: https://supabase.com/dashboard")
    print("2. Select your project: pdkyyrvikbnizgtmzzhz")
    print("3. Navigate to: SQL Editor (left sidebar)")
    print("4. Click: 'New Query'")
    print("5. Copy and paste the SQL below into the editor")
    print("6. Click: 'Run' (or press Ctrl+Enter)")
    print("\n" + "=" * 80)
    print("SQL TO COPY:")
    print("=" * 80 + "\n")
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print(sql_content)
    
    print("\n" + "=" * 80)
    print("MIGRATION SUMMARY:")
    print("=" * 80)
    print("This migration will create:")
    print("  - research_jobs table (stores research job information)")
    print("  - research_iterations table (tracks each step of research)")
    print("  - research_sources table (stores research sources/URLs)")
    print("  - Indexes for better query performance")
    print("  - Automatic timestamp update function and trigger")
    print("  - Row Level Security (RLS) enabled on all tables")
    print("\nAfter running, remember to create RLS policies as needed!")
    print("=" * 80)

if __name__ == "__main__":
    display_migration()

