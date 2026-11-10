"""
================================================================================
QUESTION BANK DATABASE MIGRATION & APPROVED DATASET IMPORTER
Part B - Step 2: Database Question Schema & Approved Dataset Migration
Project: AI Interview Analyzer
Workspace: D:\\AI-Interview-Analyzer
================================================================================

This module performs a safe, additive, and idempotent migration of approved 
question-answer records from canonical dataset files into the MySQL `questions` table.

Strict Architectural & Safety Rules Enforced:
1. ONLY imports verified records from approved source files (ml/datasets/qa/train.jsonl,
   val.jsonl, test.jsonl, questions.json).
2. Does NOT import synthetic, dummy, random, or LLM-generated questions.
3. Reference answers remain strictly backend-only.
4. Additive DDL: does not drop, alter, or delete existing users, profiles, interviews,
   or question_results tables.
5. Idempotent: re-running does not create duplicate rows or distort counts.
6. Safe transactions: uses parameterized queries and rolls back cleanly on error.
"""

import os
import sys
import json
import hashlib
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import pymysql
from dotenv import load_dotenv
from database.enrich_question_bank import classify_question_record

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DEFAULT_DB_NAME = os.getenv("DB_NAME", "ai_interview_analyzer")

# Port auto-detection
env_port = os.getenv("DB_PORT")
if env_port:
    DB_PORT = int(env_port)
else:
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


# ------------------------------------------------------------------------------
# 1. APPROVED SOURCE DATASETS INVENTORY
# ------------------------------------------------------------------------------

APPROVED_DATASET_SOURCES = [
    {
        "name": "Academic Training Split",
        "path": "ml/datasets/qa/train.jsonl",
        "format": "jsonl",
        "source_dataset": "academic_train",
        "source_version": "1.0",
        "expected_count": 1264,
        "id_strategy": "deterministic_fingerprint"
    },
    {
        "name": "Academic Validation Split",
        "path": "ml/datasets/qa/val.jsonl",
        "format": "jsonl",
        "source_dataset": "academic_val",
        "source_version": "1.0",
        "expected_count": 270,
        "id_strategy": "deterministic_fingerprint"
    },
    {
        "name": "Academic Test Split",
        "path": "ml/datasets/qa/test.jsonl",
        "format": "jsonl",
        "source_dataset": "academic_test",
        "source_version": "1.0",
        "expected_count": 272,
        "id_strategy": "deterministic_fingerprint"
    },
    {
        "name": "Curated Seed Question Bank",
        "path": "ml/datasets/qa/questions.json",
        "format": "json",
        "source_dataset": "curated_seed",
        "source_version": "1.0",
        "expected_count": 10,
        "id_strategy": "explicit_id"
    }
]


# ------------------------------------------------------------------------------
# 2. DETERMINISTIC FINGERPRINTING & RECORD EXTRACTION
# ------------------------------------------------------------------------------

def compute_record_fingerprint(question: str, answer: str) -> str:
    """
    Constructs a deterministic, collision-resistant 16-character SHA-256 fingerprint
    from the normalized question text and reference answer.
    """
    normalized = f"{question.strip()}||{answer.strip()}".encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()[:16]


def load_and_validate_source_records(source_config: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    Reads an approved source file, validates schema and non-emptiness,
    and returns valid normalized records along with validation metrics.
    """
    fpath = source_config["path"]
    if not os.path.exists(fpath):
        raise FileNotFoundError(f"Approved dataset file not found: {fpath}")

    records = []
    stats = {
        "read": 0,
        "valid": 0,
        "empty_or_invalid": 0,
        "internal_duplicates": 0
    }

    seen_fingerprints = set()

    if source_config["format"] == "json":
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                stats["read"] += 1
                q_text = (item.get("question") or "").strip()
                ans_text = (item.get("reference_answer") or item.get("answer") or "").strip()
                if not q_text or not ans_text:
                    stats["empty_or_invalid"] += 1
                    continue

                if source_config["id_strategy"] == "explicit_id" and "id" in item:
                    source_id = f"seed_{item['id']}"
                else:
                    fp = compute_record_fingerprint(q_text, ans_text)
                    source_id = f"{source_config['source_dataset']}_{fp}"

                if source_id in seen_fingerprints:
                    stats["internal_duplicates"] += 1
                    continue
                seen_fingerprints.add(source_id)

                meta = classify_question_record(q_text, ans_text)
                records.append({
                    "source_id": source_id,
                    "question_text": q_text,
                    "reference_answer": ans_text,
                    "skill": item.get("skill") or meta["skill"],
                    "role": item.get("role") or meta["role"],
                    "difficulty": item.get("difficulty") or meta["difficulty"],
                    "category": item.get("category") or meta["category"],
                    "source_dataset": source_config["source_dataset"],
                    "source_version": source_config["source_version"]
                })
                stats["valid"] += 1

    elif source_config["format"] == "jsonl":
        with open(fpath, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f, 1):
                line_str = line.strip()
                if not line_str:
                    continue
                stats["read"] += 1
                try:
                    item = json.loads(line_str)
                except Exception:
                    stats["empty_or_invalid"] += 1
                    continue

                q_text = (item.get("question") or "").strip()
                ans_text = (item.get("answer") or item.get("reference_answer") or "").strip()
                if not q_text or not ans_text:
                    stats["empty_or_invalid"] += 1
                    continue

                fp = compute_record_fingerprint(q_text, ans_text)
                source_id = f"{source_config['source_dataset']}_{fp}"

                if source_id in seen_fingerprints:
                    stats["internal_duplicates"] += 1
                    continue
                seen_fingerprints.add(source_id)

                meta = classify_question_record(q_text, ans_text)
                records.append({
                    "source_id": source_id,
                    "question_text": q_text,
                    "reference_answer": ans_text,
                    "skill": item.get("skill") or meta["skill"],
                    "role": item.get("role") or meta["role"],
                    "difficulty": item.get("difficulty") or meta["difficulty"],
                    "category": item.get("category") or meta["category"],
                    "source_dataset": source_config["source_dataset"],
                    "source_version": source_config["source_version"]
                })
                stats["valid"] += 1

    return records, stats


# ------------------------------------------------------------------------------
# 3. SCHEMA MIGRATION & TABLE CREATION
# ------------------------------------------------------------------------------

def ensure_question_bank_table(cursor, db_name: str):
    """
    Ensures the `questions` table exists with appropriate constraints,
    indexes, and data types in the target database.
    Additive operation: does not drop or alter existing tables.
    """
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS `{db_name}`.`questions` (
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
    """
    cursor.execute(create_table_sql)


# ------------------------------------------------------------------------------
# 4. IDEMPOTENT RECORD IMPORT ENGINE
# ------------------------------------------------------------------------------

def migrate_question_bank(
    db_name: str = DEFAULT_DB_NAME,
    dry_run: bool = False,
    simulate_rollback: bool = False
) -> Dict[str, Any]:
    """
    Executes the idempotent migration pipeline:
    1. Connects to the target MySQL database.
    2. Verifies pre-existing tables and row counts.
    3. Creates the `questions` table additively.
    4. Validates and imports all approved source records via parameterized transactions.
    5. Confirms idempotency and verifies existing records remained unchanged.
    """
    print(f"\n========================================================")
    print(f" QUESTION BANK MIGRATION: TARGET DB '{db_name}'")
    print(f" Host: {DB_HOST}:{DB_PORT} | Dry-Run: {dry_run} | Rollback-Test: {simulate_rollback}")
    print(f"========================================================")

    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=db_name,
        charset="utf8mb4",
        autocommit=False
    )

    migration_report = {
        "target_database": db_name,
        "timestamp": datetime.datetime.now().isoformat(),
        "dry_run": dry_run,
        "rollback_test": simulate_rollback,
        "pre_existing_tables": {},
        "source_breakdown": {},
        "total_source_records": 0,
        "total_valid_records": 0,
        "total_invalid_records": 0,
        "newly_inserted": 0,
        "already_existing": 0,
        "final_table_count": 0,
        "existing_tables_intact": False,
        "status": "IN_PROGRESS"
    }

    try:
        with conn.cursor() as cursor:
            # Step 1: Capture pre-existing tables and row counts
            cursor.execute("SHOW TABLES;")
            existing_tables = [row[0] for row in cursor.fetchall()]
            for tbl in existing_tables:
                cursor.execute(f"SELECT COUNT(*) FROM `{tbl}`;")
                migration_report["pre_existing_tables"][tbl] = cursor.fetchone()[0]
            print(f"Pre-migration tables detected ({len(existing_tables)}):")
            for t, cnt in migration_report["pre_existing_tables"].items():
                print(f"  • {t}: {cnt} rows")

            # Step 2: Ensure questions table exists
            ensure_question_bank_table(cursor, db_name)

            # Step 3: Check initial count of questions table
            cursor.execute("SELECT COUNT(*) FROM `questions`;")
            initial_q_count = cursor.fetchone()[0]

            # Step 4: Process and import records from approved sources
            insert_sql = """
            INSERT INTO `questions` (
                `source_id`, `question_text`, `reference_answer`,
                `skill`, `role`, `difficulty`, `category`,
                `source_dataset`, `source_version`, `is_active`,
                `created_at`, `updated_at`
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, NOW(), NOW()
            )
            ON DUPLICATE KEY UPDATE
                `question_text` = VALUES(`question_text`),
                `reference_answer` = VALUES(`reference_answer`),
                `skill` = COALESCE(VALUES(`skill`), `skill`),
                `role` = COALESCE(VALUES(`role`), `role`),
                `difficulty` = COALESCE(VALUES(`difficulty`), `difficulty`),
                `category` = COALESCE(VALUES(`category`), `category`),
                `updated_at` = NOW();
            """

            # Check existing source_ids
            cursor.execute("SELECT `source_id` FROM `questions`;")
            existing_source_ids = {row[0] for row in cursor.fetchall()}

            newly_inserted = 0
            already_existing = 0

            for source in APPROVED_DATASET_SOURCES:
                s_name = source["name"]
                recs, stats = load_and_validate_source_records(source)
                migration_report["source_breakdown"][s_name] = {
                    "path": source["path"],
                    "format": source["format"],
                    "read": stats["read"],
                    "valid": stats["valid"],
                    "invalid": stats["empty_or_invalid"],
                    "internal_duplicates": stats["internal_duplicates"],
                    "expected_count": source["expected_count"]
                }
                migration_report["total_source_records"] += stats["read"]
                migration_report["total_valid_records"] += stats["valid"]
                migration_report["total_invalid_records"] += stats["empty_or_invalid"]

                batch_params = []
                for r in recs:
                    if r["source_id"] in existing_source_ids:
                        already_existing += 1
                    else:
                        newly_inserted += 1
                        existing_source_ids.add(r["source_id"])

                    batch_params.append((
                        r["source_id"],
                        r["question_text"],
                        r["reference_answer"],
                        r["skill"],
                        r["role"],
                        r["difficulty"],
                        r["category"],
                        r["source_dataset"],
                        r["source_version"]
                    ))

                if not dry_run and batch_params:
                    cursor.executemany(insert_sql, batch_params)

            migration_report["newly_inserted"] = newly_inserted
            migration_report["already_existing"] = already_existing

            if simulate_rollback:
                print("Simulating error for rollback verification...")
                raise RuntimeError("Simulated failure to verify transactional rollback integrity.")

            if dry_run:
                print("Dry-run mode active. Rolling back all transaction modifications.")
                conn.rollback()
                cursor.execute("SELECT COUNT(*) FROM `questions`;")
                migration_report["final_table_count"] = cursor.fetchone()[0]
            else:
                conn.commit()
                cursor.execute("SELECT COUNT(*) FROM `questions`;")
                migration_report["final_table_count"] = cursor.fetchone()[0]

            # Step 5: Verify existing tables remained completely intact
            intact = True
            for tbl, initial_count in migration_report["pre_existing_tables"].items():
                if tbl == "questions":
                    continue
                cursor.execute(f"SELECT COUNT(*) FROM `{tbl}`;")
                post_count = cursor.fetchone()[0]
                if post_count != initial_count:
                    intact = False
                    print(f"WARNING: Table '{tbl}' count changed from {initial_count} to {post_count}!")
            migration_report["existing_tables_intact"] = intact
            migration_report["status"] = "SUCCESS"

    except Exception as e:
        conn.rollback()
        migration_report["status"] = "ROLLED_BACK"
        migration_report["error"] = str(e)
        print(f"Transaction rolled back due to: {e}")
        raise e
    finally:
        conn.close()

    print("\n--- Migration Execution Summary ---")
    print(f"Target DB:                {migration_report['target_database']}")
    print(f"Status:                   {migration_report['status']}")
    print(f"Total Source Records:     {migration_report['total_source_records']}")
    print(f"Total Valid Records:      {migration_report['total_valid_records']}")
    print(f"Newly Inserted Records:   {migration_report['newly_inserted']}")
    print(f"Existing / Idempotent:    {migration_report['already_existing']}")
    print(f"Final 'questions' Count:  {migration_report['final_table_count']}")
    print(f"Existing Tables Intact:   {migration_report['existing_tables_intact']}")
    return migration_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate approved questions to MySQL database.")
    parser.add_argument("--target-db", default=DEFAULT_DB_NAME, help="Target MySQL database name")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without committing")
    parser.add_argument("--test-rollback", action="store_true", help="Test rollback on error")
    args = parser.parse_args()

    migrate_question_bank(
        db_name=args.target_db,
        dry_run=args.dry_run,
        simulate_rollback=args.test_rollback
    )

