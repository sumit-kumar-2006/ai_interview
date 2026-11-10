import os
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root .env if present
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "ai_interview_analyzer")

# Determine DB port: default to DB_PORT env var, or test 3306 / 3307 if not explicitly set
env_port = os.getenv("DB_PORT")
if env_port:
    DB_PORT = int(env_port)
else:
    # Auto-detect whether 3306 or 3307 accepts connection
    DB_PORT = 3306
    for port_candidate in [3306, 3307]:
        try:
            test_conn = pymysql.connect(
                host=DB_HOST,
                port=port_candidate,
                user=DB_USER,
                password=DB_PASSWORD,
                connect_timeout=2
            )
            test_conn.close()
            DB_PORT = port_candidate
            break
        except Exception:
            continue

# Database URL for SQLAlchemy + PyMySQL
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

def create_database_if_not_exists():
    """Ensure the target MySQL database exists prior to SQLAlchemy metadata creation."""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            autocommit=True
        )
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
        connection.close()
        print(f"Database '{DB_NAME}' checked/created successfully.")
    except Exception as e:
        print(f"Error ensuring database '{DB_NAME}' exists: {e}")
        raise e

def ensure_schema_updates():
    """Ensure existing tables have required columns (e.g. user_id column in interviews table)."""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            autocommit=True
        )
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'interviews' AND COLUMN_NAME = 'user_id'",
                (DB_NAME,)
            )
            count = cursor.fetchone()[0]
            if count == 0:
                print("Adding missing 'user_id' column to 'interviews' table...")
                cursor.execute(
                    "ALTER TABLE interviews ADD COLUMN user_id INT NULL, ADD INDEX idx_interviews_user_id (user_id);"
                )
                print("'user_id' column added successfully.")

            # Check resume columns on user_profiles
            for col_name, col_type in [("resume_filename", "VARCHAR(255) NULL"), ("parsed_resume", "JSON NULL")]:
                cursor.execute(
                    "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'user_profiles' AND COLUMN_NAME = %s",
                    (DB_NAME, col_name)
                )
                if cursor.fetchone()[0] == 0:
                    print(f"Adding missing '{col_name}' column to 'user_profiles' table...")
                    cursor.execute(f"ALTER TABLE user_profiles ADD COLUMN {col_name} {col_type};")
                    print(f"'{col_name}' column added successfully.")

            # Check columns on interviews
            interview_cols = [
                ("resume_filename", "VARCHAR(255) NULL"),
                ("parsed_resume", "JSON NULL"),
                ("target_role", "VARCHAR(255) NULL"),
                ("experience_level", "VARCHAR(100) NULL"),
                ("technical_score", "FLOAT NULL"),
                ("communication_score", "FLOAT NULL")
            ]
            for col_name, col_type in interview_cols:
                cursor.execute(
                    "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'interviews' AND COLUMN_NAME = %s",
                    (DB_NAME, col_name)
                )
                if cursor.fetchone()[0] == 0:
                    print(f"Adding missing '{col_name}' column to 'interviews' table...")
                    cursor.execute(f"ALTER TABLE interviews ADD COLUMN {col_name} {col_type};")
                    print(f"'{col_name}' column added successfully.")

            # Check columns on question_results
            qr_cols = [
                ("evaluation_spec", "JSON NULL"),
                ("correct_concepts", "JSON NULL"),
                ("missing_concepts", "JSON NULL"),
                ("incorrect_claims", "JSON NULL"),
                ("rubric_scores", "JSON NULL"),
                ("attempt_count", "INT DEFAULT 1 NULL")
            ]
            for col_name, col_type in qr_cols:
                cursor.execute(
                    "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'question_results' AND COLUMN_NAME = %s",
                    (DB_NAME, col_name)
                )
                if cursor.fetchone()[0] == 0:
                    print(f"Adding missing '{col_name}' column to 'question_results' table...")
                    cursor.execute(f"ALTER TABLE question_results ADD COLUMN {col_name} {col_type};")
                    print(f"'{col_name}' column added successfully.")

            # Check questions table exists
            cursor.execute(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'questions'",
                (DB_NAME,)
            )
            if cursor.fetchone()[0] == 0:
                print("Creating 'questions' table...")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS `questions` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `source_id` VARCHAR(64) NOT NULL UNIQUE,
                    `question_text` TEXT NOT NULL,
                    `reference_answer` TEXT NOT NULL,
                    `skill` VARCHAR(100) NULL,
                    `role` VARCHAR(100) NULL,
                    `difficulty` VARCHAR(50) NULL,
                    `category` VARCHAR(100) NULL,
                    `source_dataset` VARCHAR(100) NOT NULL,
                    `source_version` VARCHAR(50) NOT NULL DEFAULT '1.0',
                    `is_active` TINYINT(1) NOT NULL DEFAULT 1,
                    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_questions_source_id` (`source_id`),
                    INDEX `idx_questions_category` (`category`),
                    INDEX `idx_questions_role` (`role`),
                    INDEX `idx_questions_difficulty` (`difficulty`),
                    INDEX `idx_questions_skill` (`skill`),
                    INDEX `idx_questions_is_active` (`is_active`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """)
                print("'questions' table created successfully.")

        connection.close()
    except Exception as e:
        print(f"Schema update notice: {e}")

# Create SQLAlchemy engine with robust connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base
Base = declarative_base()

# FastAPI Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
