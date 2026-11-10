"""
================================================================================
DATASET ELIGIBILITY & QUARANTINE MANAGER
Part B - Step 3: Secure Backend Question & Evaluation Engine
Project: AI Interview Analyzer
Workspace: D:\\AI-Interview-Analyzer
================================================================================

This module safely updates question eligibility in the MySQL database:
- `academic_train` (1,264 records): Set `is_active = 1` (eligible for active interviews).
- `academic_val` (270 records): Set `is_active = 0` (quarantined for offline validation).
- `academic_test` (272 records): Set `is_active = 0` (quarantined for academic testing).
- `curated_seed` (10 records): Set `is_active = 0` (quarantined until provenance approval).

Zero records are deleted. Atomic transactions with rollback are enforced.
"""

import os
import argparse
import pymysql
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DEFAULT_DB_NAME = os.getenv("DB_NAME", "ai_interview_analyzer")

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


def update_dataset_eligibility(db_name: str = DEFAULT_DB_NAME) -> dict:
    print(f"\n========================================================")
    print(f" DATASET ELIGIBILITY UPDATE: TARGET DB '{db_name}'")
    print(f" Host: {DB_HOST}:{DB_PORT}")
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

    summary = {
        "database": db_name,
        "initial_counts": {},
        "affected_rows": {},
        "final_counts": {},
        "status": "IN_PROGRESS"
    }

    try:
        with conn.cursor() as cursor:
            # Step 1: Pre-update verification
            cursor.execute("SELECT source_dataset, is_active, COUNT(*) FROM `questions` GROUP BY source_dataset, is_active;")
            pre_rows = cursor.fetchall()
            for ds, active, count in pre_rows:
                summary["initial_counts"][f"{ds} (active={active})"] = count

            print("Initial Status Breakdown:")
            for k, v in summary["initial_counts"].items():
                print(f"  • {k}: {v} rows")

            # Step 2: Set academic_train active
            cursor.execute("UPDATE `questions` SET `is_active` = 1 WHERE `source_dataset` = 'academic_train';")
            train_affected = cursor.rowcount
            summary["affected_rows"]["academic_train_activated"] = train_affected

            # Step 3: Set academic_val inactive
            cursor.execute("UPDATE `questions` SET `is_active` = 0 WHERE `source_dataset` = 'academic_val';")
            val_affected = cursor.rowcount
            summary["affected_rows"]["academic_val_deactivated"] = val_affected

            # Step 4: Set academic_test inactive
            cursor.execute("UPDATE `questions` SET `is_active` = 0 WHERE `source_dataset` = 'academic_test';")
            test_affected = cursor.rowcount
            summary["affected_rows"]["academic_test_deactivated"] = test_affected

            # Step 5: Set curated_seed inactive
            cursor.execute("UPDATE `questions` SET `is_active` = 0 WHERE `source_dataset` = 'curated_seed';")
            seed_affected = cursor.rowcount
            summary["affected_rows"]["curated_seed_deactivated"] = seed_affected

            # Step 6: Post-update verification
            cursor.execute("SELECT source_dataset, is_active, COUNT(*) FROM `questions` GROUP BY source_dataset, is_active;")
            post_rows = cursor.fetchall()
            for ds, active, count in post_rows:
                summary["final_counts"][f"{ds} (active={active})"] = count

            cursor.execute("SELECT COUNT(*) FROM `questions`;")
            total_after = cursor.fetchone()[0]
            summary["total_questions"] = total_after

            # Check that total questions is unchanged (no records deleted)
            cursor.execute("SELECT COUNT(*) FROM `questions` WHERE `is_active` = 1;")
            active_total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM `questions` WHERE `is_active` = 0;")
            inactive_total = cursor.fetchone()[0]

            assert total_after == 1816, f"Expected 1,816 total questions, found {total_after}"
            assert active_total == 1264, f"Expected 1,264 active questions, found {active_total}"
            assert inactive_total == (270 + 272 + 10), f"Expected 552 inactive questions, found {inactive_total}"

            conn.commit()
            summary["status"] = "SUCCESS"
            print("\nPost-Update Verification Successful:")
            print(f"  • Active academic_train: {active_total} (100% eligible)")
            print(f"  • Quarantined inactive:  {inactive_total} (val=270, test=272, seed=10)")
            print(f"  • Total questions:       {total_after} (0 deleted)")

    except Exception as e:
        conn.rollback()
        summary["status"] = "FAILED"
        summary["error"] = str(e)
        print(f"Transaction rolled back due to error: {e}")
        raise e
    finally:
        conn.close()

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update dataset eligibility for active interviews.")
    parser.add_argument("--target-db", default=DEFAULT_DB_NAME, help="Target MySQL database name")
    args = parser.parse_args()

    update_dataset_eligibility(db_name=args.target_db)

