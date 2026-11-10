"""
================================================================================
PART B - STEP 2: QUESTION BANK MIGRATION & DATASET INTEGRITY TEST SUITE
Project: AI Interview Analyzer
Workspace: D:\\AI-Interview-Analyzer
================================================================================

Tests verifying:
1. Database migration and schema existence
2. Approved dataset record counts (1,816 total: 1,806 academic splits + 10 seed)
3. Data integrity: non-empty questions and reference answers, unique source_ids
4. Existing tables and rows remain intact
5. Idempotent re-run safety
6. Transactional rollback safety
7. Backend-only isolation of reference answers (schema security)
"""

import os
import sys

# Ensure repository root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import pymysql
from typing import Dict, Any
from backend.app.schemas import QuestionPublic, QuestionInternal

from database.migrate_question_bank import (
    migrate_question_bank,
    compute_record_fingerprint,
    APPROVED_DATASET_SOURCES,
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DEFAULT_DB_NAME
)


def get_db_connection(db_name: str = DEFAULT_DB_NAME):
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=db_name,
        charset="utf8mb4"
    )


def test_database_connection_and_questions_table_exists():
    """Verify MySQL connectivity and that `questions` table exists with proper columns."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tables = [r[0] for r in cursor.fetchall()]
            assert "questions" in tables, "Table 'questions' does not exist in database"

            cursor.execute("DESCRIBE `questions`;")
            col_dict = {r[0]: r[1] for r in cursor.fetchall()}
            expected_cols = [
                "id", "source_id", "question_text", "reference_answer",
                "skill", "role", "difficulty", "category",
                "source_dataset", "source_version", "is_active",
                "created_at", "updated_at"
            ]
            for col in expected_cols:
                assert col in col_dict, f"Missing expected column '{col}' in 'questions' table"
    finally:
        conn.close()


def test_imported_record_counts_match_sources():
    """Verify that imported counts match the canonical source splits exactly."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM `questions`;")
            total_count = cursor.fetchone()[0]
            assert total_count == 1816, f"Expected 1,816 questions in DB, found {total_count}"

            # Check counts per source dataset
            cursor.execute("SELECT source_dataset, COUNT(*) FROM `questions` GROUP BY source_dataset;")
            counts_by_source = dict(cursor.fetchall())

            assert counts_by_source.get("academic_train") == 1264, "academic_train count mismatch"
            assert counts_by_source.get("academic_val") == 270, "academic_val count mismatch"
            assert counts_by_source.get("academic_test") == 272, "academic_test count mismatch"
            assert counts_by_source.get("curated_seed") == 10, "curated_seed count mismatch"
    finally:
        conn.close()


def test_source_id_uniqueness_and_integrity():
    """Verify that every source_id is non-null, non-empty, and globally unique."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*), COUNT(DISTINCT source_id) FROM `questions`;")
            total, distinct = cursor.fetchone()
            assert total == distinct, f"Duplicate source_ids found: total={total}, distinct={distinct}"

            cursor.execute("SELECT COUNT(*) FROM `questions` WHERE source_id IS NULL OR TRIM(source_id) = '';")
            empty_sids = cursor.fetchone()[0]
            assert empty_sids == 0, f"Found {empty_sids} null or empty source_ids"
    finally:
        conn.close()


def test_question_and_answer_non_empty():
    """Verify that no question_text or reference_answer is null or empty whitespace."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM `questions` WHERE question_text IS NULL OR TRIM(question_text) = '';")
            empty_q = cursor.fetchone()[0]
            assert empty_q == 0, f"Found {empty_q} empty question texts"

            cursor.execute("SELECT COUNT(*) FROM `questions` WHERE reference_answer IS NULL OR TRIM(reference_answer) = '';")
            empty_a = cursor.fetchone()[0]
            assert empty_a == 0, f"Found {empty_a} empty reference answers"
    finally:
        conn.close()


def test_existing_tables_and_rows_intact():
    """Verify that pre-existing tables (users, user_profiles, interviews, question_results) remain intact."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM `users`;")
            assert cursor.fetchone()[0] >= 24, "Existing 'users' table rows modified or lost"

            cursor.execute("SELECT COUNT(*) FROM `user_profiles`;")
            assert cursor.fetchone()[0] >= 4, "Existing 'user_profiles' table rows modified or lost"

            cursor.execute("SELECT COUNT(*) FROM `interviews`;")
            assert cursor.fetchone()[0] >= 10, "Existing 'interviews' table rows modified or lost"

            cursor.execute("SELECT COUNT(*) FROM `question_results`;")
            assert cursor.fetchone()[0] >= 10, "Existing 'question_results' table rows modified or lost"
    finally:
        conn.close()


def test_migration_idempotency():
    """Verify that running the migration again inserts 0 duplicates and maintains exact count."""
    report = migrate_question_bank(db_name=DEFAULT_DB_NAME, dry_run=False)
    assert report["status"] == "SUCCESS"
    assert report["newly_inserted"] == 0, f"Expected 0 newly inserted rows on re-run, got {report['newly_inserted']}"
    assert report["already_existing"] == 1816, f"Expected 1,816 already existing, got {report['already_existing']}"
    assert report["final_table_count"] == 1816, f"Expected 1,816 final count, got {report['final_table_count']}"
    assert report["existing_tables_intact"] is True


def test_transactional_rollback_on_failure():
    """Verify that an abort/error rolls back cleanly and leaves no partial state."""
    # Test on staging DB
    staging_db = "ai_interview_analyzer_staging"
    conn = get_db_connection(staging_db)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM `questions`;")
            count_before = cursor.fetchone()[0]
    finally:
        conn.close()

    with pytest.raises(RuntimeError):
        migrate_question_bank(db_name=staging_db, simulate_rollback=True)

    conn = get_db_connection(staging_db)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM `questions`;")
            count_after = cursor.fetchone()[0]
            assert count_after == count_before, "Rollback failed: row count altered after simulated failure"
    finally:
        conn.close()


def test_public_schema_excludes_reference_answer():
    """Verify that QuestionPublic schema omits reference_answer while QuestionInternal preserves it."""
    public_fields = set(QuestionPublic.model_fields.keys())
    internal_fields = set(QuestionInternal.model_fields.keys())

    assert "reference_answer" not in public_fields, "Security violation: reference_answer exposed in QuestionPublic schema"
    assert "reference_answer" in internal_fields, "QuestionInternal must contain reference_answer"
    assert "source_dataset" not in public_fields
    assert "source_id" in public_fields


def test_all_questions_have_enriched_metadata():
    """Verify that 100% of rows in questions have non-null, valid category, difficulty, role, and skill."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(category IS NULL OR TRIM(category) = '') as null_cat,
                    SUM(difficulty IS NULL OR TRIM(difficulty) = '') as null_diff,
                    SUM(role IS NULL OR TRIM(role) = '') as null_role,
                    SUM(skill IS NULL OR TRIM(skill) = '') as null_skill
                FROM `questions`;
            """)
            total, null_cat, null_diff, null_role, null_skill = cursor.fetchone()
            assert total == 1816
            assert null_cat == 0, f"Found {null_cat} questions with null/empty category"
            assert null_diff == 0, f"Found {null_diff} questions with null/empty difficulty"
            assert null_role == 0, f"Found {null_role} questions with null/empty role"
            assert null_skill == 0, f"Found {null_skill} questions with null/empty skill"

            # Verify difficulty values
            cursor.execute("SELECT DISTINCT difficulty FROM `questions`;")
            diffs = {r[0] for r in cursor.fetchall()}
            assert diffs.issubset({"Easy", "Medium", "Hard"}), f"Unexpected difficulty values: {diffs}"
            assert len(diffs) == 3, f"Expected Easy, Medium, and Hard in DB, got: {diffs}"

            # Verify categories
            cursor.execute("SELECT COUNT(DISTINCT category) FROM `questions`;")
            cat_count = cursor.fetchone()[0]
            assert cat_count >= 5, f"Expected at least 5 distinct categories, found {cat_count}"
    finally:
        conn.close()


def test_role_and_difficulty_filtering_operates_correctly():
    """Verify that get_academic_questions_from_db accurately filters by role and difficulty."""
    from backend.app.questions import get_academic_questions_from_db

    # Test Frontend Developer + Medium
    deck_frontend = get_academic_questions_from_db(count=3, role="Frontend Developer", difficulty="Medium")
    assert len(deck_frontend) == 3
    for q in deck_frontend:
        assert q["difficulty"] == "Medium"
        assert q["role"] == "Frontend Developer"

    # Test Machine Learning Engineer + Hard
    deck_ml = get_academic_questions_from_db(count=3, role="Machine Learning Engineer", difficulty="Hard")
    assert len(deck_ml) == 3
    for q in deck_ml:
        assert q["difficulty"] == "Hard"
        assert q["role"] == "Machine Learning Engineer"

