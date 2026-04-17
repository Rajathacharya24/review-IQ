"""
ReviewIQ — Database Migration Guide
Updates database schema to support multilingual features.

This guide provides SQL statements for adding new columns to the Review table
to store language metadata.
"""

# ════════════════════════════════════════════════════════════════════════════
# SQL Migration Statements
# ════════════════════════════════════════════════════════════════════════════

# For SQLite:
SQLITE_MIGRATIONS = """
-- Add multilingual support columns to reviews table

ALTER TABLE reviews ADD COLUMN original_language_name VARCHAR(100) DEFAULT NULL;
-- Stores human-readable language name (e.g., "Hindi", "Spanish")

ALTER TABLE reviews ADD COLUMN language_confidence FLOAT DEFAULT 0.0;
-- Stores confidence score of language detection (0.0-1.0)

ALTER TABLE reviews ADD COLUMN has_mixed_languages BOOLEAN DEFAULT FALSE;
-- Flag indicating if review contains multiple languages
"""

# For PostgreSQL:
POSTGRESQL_MIGRATIONS = """
-- Add multilingual support columns to reviews table

ALTER TABLE reviews ADD COLUMN original_language_name VARCHAR(100) DEFAULT NULL;
-- Stores human-readable language name (e.g., "Hindi", "Spanish")

ALTER TABLE reviews ADD COLUMN language_confidence NUMERIC(3,2) DEFAULT 0.0;
-- Stores confidence score of language detection (0.0-1.0)

ALTER TABLE reviews ADD COLUMN has_mixed_languages BOOLEAN DEFAULT FALSE;
-- Flag indicating if review contains multiple languages

-- Create index for language analysis queries
CREATE INDEX idx_reviews_language ON reviews(original_language);
CREATE INDEX idx_reviews_mixed_lang ON reviews(has_mixed_languages);
"""

# For MySQL:
MYSQL_MIGRATIONS = """
-- Add multilingual support columns to reviews table

ALTER TABLE reviews ADD COLUMN original_language_name VARCHAR(100) DEFAULT NULL;
-- Stores human-readable language name (e.g., "Hindi", "Spanish")

ALTER TABLE reviews ADD COLUMN language_confidence DECIMAL(3,2) DEFAULT 0.0;
-- Stores confidence score of language detection (0.0-1.0)

ALTER TABLE reviews ADD COLUMN has_mixed_languages BOOLEAN DEFAULT FALSE;
-- Flag indicating if review contains multiple languages

-- Create indexes for language analysis queries
CREATE INDEX idx_reviews_language ON reviews(original_language);
CREATE INDEX idx_reviews_mixed_lang ON reviews(has_mixed_languages);
"""


# ════════════════════════════════════════════════════════════════════════════
# Python Migration Script (Using SQLAlchemy)
# ════════════════════════════════════════════════════════════════════════════

SQLALCHEMY_MIGRATION = """
from sqlalchemy import Column, String, Float, Boolean
from sqlalchemy.schema import CreateColumn
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add new columns to reviews table
    op.add_column('reviews', 
        Column('original_language_name', String(100), nullable=True)
    )
    op.add_column('reviews',
        Column('language_confidence', Float, nullable=False, server_default='0.0')
    )
    op.add_column('reviews',
        Column('has_mixed_languages', sa.Boolean, nullable=False, server_default=sa.false())
    )
    
    # Create indexes
    op.create_index('idx_reviews_language', 'reviews', ['original_language'])
    op.create_index('idx_reviews_mixed_lang', 'reviews', ['has_mixed_languages'])

def downgrade():
    # Remove indexes
    op.drop_index('idx_reviews_language', table_name='reviews')
    op.drop_index('idx_reviews_mixed_lang', table_name='reviews')
    
    # Remove columns
    op.drop_column('reviews', 'original_language_name')
    op.drop_column('reviews', 'language_confidence')
    op.drop_column('reviews', 'has_mixed_languages')
"""


# ════════════════════════════════════════════════════════════════════════════
# Migration Steps
# ════════════════════════════════════════════════════════════════════════════

MIGRATION_STEPS = """
1. BACKUP YOUR DATABASE
   Before running any migration, create a backup:
   
   For SQLite:
   $ cp reviewiq.db reviewiq.db.backup
   
   For PostgreSQL:
   $ pg_dump reviewiq_db > reviewiq_db.backup.sql
   
   For MySQL:
   $ mysqldump -u root -p reviewiq_db > reviewiq_db.backup.sql

2. CHOOSE YOUR DATABASE TYPE

   Option A: SQLite (Default)
   ────────────────────────
   a) Copy the SQLITE_MIGRATIONS SQL from this file
   b) Open your SQLite database in a UI tool (e.g., DB Browser for SQLite)
   c) Execute each ALTER TABLE statement
   OR use CLI:
   $ sqlite3 reviewiq.db < migration.sql

   Option B: PostgreSQL
   ──────────────────
   a) Connect to your database:
   $ psql -U postgres -d reviewiq_db
   
   b) Execute the POSTGRESQL_MIGRATIONS statements:
   \i migration.sql
   
   OR run via command line:
   $ psql -U postgres -d reviewiq_db -f migration.sql

   Option C: MySQL
   ──────────────
   a) Connect to your database:
   $ mysql -u root -p reviewiq_db
   
   b) Execute the MYSQL_MIGRATIONS statements
   
   OR run via command line:
   $ mysql -u root -p reviewiq_db < migration.sql

3. VERIFY MIGRATION

   For SQLite:
   $ sqlite3 reviewiq.db ".schema reviews"
   
   Should show the three new columns:
   - original_language_name TEXT
   - language_confidence REAL
   - has_mixed_languages BOOLEAN

   For PostgreSQL:
   $ psql -U postgres -d reviewiq_db -c "\\d reviews"
   
   For MySQL:
   $ mysql -u root -p -e "DESC reviewiq_db.reviews"

4. UPDATE YOUR APPLICATION

   a) Pull the latest code:
   $ git pull origin main
   
   b) Install updated dependencies:
   $ pip install -r backend/requirements.txt
   
   c) Restart the backend server:
   $ python backend/main.py

5. TEST THE INSTALLATION

   a) Run the test script:
   $ python backend/test_multilingual.py
   
   b) Upload a sample multilingual CSV/JSON file
   
   c) Verify language detection in the response

6. MONITOR LOGS

   Watch for any errors:
   - Check language detection confidence scores
   - Monitor translation API calls
   - Verify mixed-language detection
"""


# ════════════════════════════════════════════════════════════════════════════
# Rollback Instructions
# ════════════════════════════════════════════════════════════════════════════

ROLLBACK_INSTRUCTIONS = """
If you need to rollback the migration:

For SQLite:
──────────
DROP INDEX idx_reviews_language;
DROP INDEX idx_reviews_mixed_lang;
ALTER TABLE reviews DROP COLUMN original_language_name;
ALTER TABLE reviews DROP COLUMN language_confidence;
ALTER TABLE reviews DROP COLUMN has_mixed_languages;

For PostgreSQL:
───────────────
DROP INDEX idx_reviews_language;
DROP INDEX idx_reviews_mixed_lang;
ALTER TABLE reviews DROP COLUMN original_language_name;
ALTER TABLE reviews DROP COLUMN language_confidence;
ALTER TABLE reviews DROP COLUMN has_mixed_languages;

For MySQL:
──────────
DROP INDEX idx_reviews_language ON reviews;
DROP INDEX idx_reviews_mixed_lang ON reviews;
ALTER TABLE reviews DROP COLUMN original_language_name;
ALTER TABLE reviews DROP COLUMN language_confidence;
ALTER TABLE reviews DROP COLUMN has_mixed_languages;

Then restore from backup:
$ cp reviewiq.db.backup reviewiq.db  (SQLite)
$ psql reviewiq_db < backup.sql  (PostgreSQL)
$ mysql reviewiq_db < backup.sql  (MySQL)
"""


# ════════════════════════════════════════════════════════════════════════════
# Column Definitions
# ════════════════════════════════════════════════════════════════════════════

COLUMN_DEFINITIONS = """
1. original_language_name
   Type: VARCHAR(100) / String
   Default: NULL
   Purpose: Stores human-readable language name
   Examples: "English", "Hindi", "Spanish", "Kannada"
   Note: Complementary to existing 'original_language' field (which uses ISO codes)

2. language_confidence
   Type: FLOAT / NUMERIC(3,2) / DECIMAL(3,2)
   Default: 0.0
   Range: 0.0 - 1.0
   Purpose: Stores confidence score of language detection
   Examples: 0.95 (very confident), 0.65 (somewhat confident)
   Note: Higher score = more certain detection

3. has_mixed_languages
   Type: BOOLEAN
   Default: FALSE
   Purpose: Flags reviews containing multiple languages
   Examples: TRUE for "Great phone! बहुत अच्छा है!"
   Note: Useful for analytics and reporting
"""


# ════════════════════════════════════════════════════════════════════════════
# Existing Fields (For Reference)
# ════════════════════════════════════════════════════════════════════════════

EXISTING_FIELDS_INFO = """
The following existing fields are used in multilingual processing:

1. original_language
   Type: VARCHAR(50) / String
   Stores: ISO 639-1 language code (e.g., "en", "hi", "es")
   ALREADY EXISTS - No migration needed

2. translated_text
   Type: TEXT
   Stores: English translation of the review
   ALREADY EXISTS - No migration needed

3. review_text
   Type: TEXT
   Stores: Original review text in any language
   ALREADY EXISTS - No migration needed

These fields work together with the new multilingual columns:
original_language + original_language_name + language_confidence = Full language metadata
translated_text = Translated content for analysis
"""


# ════════════════════════════════════════════════════════════════════════════
# Troubleshooting
# ════════════════════════════════════════════════════════════════════════════

TROUBLESHOOTING = """
Common Migration Issues:

1. "Column already exists" Error
   ────────────────────────────
   - This column might have been added previously
   - Check if the column exists before adding
   - For SQLite: sqlite3 db.sqlite "PRAGMA table_info(reviews);"
   - For PostgreSQL: \\d reviews in psql
   - If it exists, skip that ALTER TABLE statement

2. "Table 'reviews' doesn't exist" Error
   ───────────────────────────────────
   - Make sure you're connected to the correct database
   - For PostgreSQL: Make sure you're in the right database (\\c reviewiq_db)
   - For MySQL: Make sure you selected the right database (USE reviewiq_db;)

3. Migration Hangs or Takes Too Long
   ─────────────────────────────────
   - Normal for large databases (millions of rows)
   - Be patient - adding columns takes time
   - Don't interrupt the migration
   - For very large databases, add columns separately

4. Foreign Key Constraint Errors
   ─────────────────────────────
   - Temporarily disable foreign key checks (if applicable)
   - For SQLite: PRAGMA foreign_keys = OFF;
   - For MySQL: SET FOREIGN_KEY_CHECKS=0;
   - For PostgreSQL: Not an issue usually

5. "Permission Denied" Error
   ───────────────────────
   - Make sure you have the right database user permissions
   - For PostgreSQL: Use a superuser or owner of the table
   - For MySQL: Ensure user has ALTER permissions
   - For SQLite: Check file permissions on the database file
"""


if __name__ == "__main__":
    print("\n" + "="*70)
    print("ReviewIQ Database Migration Guide - Multilingual Support")
    print("="*70)
    
    print("\n" + "─"*70)
    print("MIGRATION STEPS")
    print("─"*70)
    print(MIGRATION_STEPS)
    
    print("\n" + "─"*70)
    print("TROUBLESHOOTING")
    print("─"*70)
    print(TROUBLESHOOTING)
    
    print("\n" + "─"*70)
    print("ROLLBACK INSTRUCTIONS")
    print("─"*70)
    print(ROLLBACK_INSTRUCTIONS)
    
    print("\n" + "="*70)
    print("For your specific database type, see the SQL statements above.")
    print("="*70 + "\n")
