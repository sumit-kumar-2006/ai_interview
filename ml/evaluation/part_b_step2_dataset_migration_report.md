# PART B – STEP 2: DATABASE QUESTION SCHEMA & APPROVED DATASET MIGRATION REPORT

**Project:** AI Interview Analyzer  
**Workspace:** `D:\AI-Interview-Analyzer`  
**Execution Date:** November 2026  
**Auditor / Engineer:** Senior Full-Stack Developer, Python FastAPI Engineer & Database Architect  
**Status:** COMPLETE & VERIFIED (All 31 Tests Passed)

---

## 1. EXECUTIVE SUMMARY

Part B Step 2 has successfully established a secure, relational database-backed question bank within the existing MySQL database (`ai_interview_analyzer` on port 3307). 

All imported questions and reference answers originate **strictly and exclusively** from the project's verified, canonical dataset files. No synthetic, dummy, random, or LLM-generated questions were introduced. The pre-existing application database tables (`users`, `user_profiles`, `interviews`, `question_results`) were preserved with 100% data integrity and zero record loss.

### High-Level Metrics Summary:
- **Pre-migration Tables Preserved:** 4 tables (`users`, `user_profiles`, `interviews`, `question_results`)
- **New Additive Table Created:** `questions`
- **Total Canonical Source Records Audited:** 1,816 records
- **Valid Source Records Imported:** 1,816 records
- **Invalid / Empty Records Excluded:** 0
- **Internal Duplicate Pairs in Source Files:** 0
- **Total Records in MySQL `questions` Table:** 1,816 records
- **Idempotency Verified:** Re-running migration yielded exactly 0 duplicate insertions and 1,816 matched records.
- **Transactional Rollback Verified:** Abort simulation confirmed 0 partial writes.
- **Test Suite Results:** 31 tests executed, **31 passed** (100% pass rate).

---

## 2. SOURCE DATASET IDENTIFICATION & PROVENANCE

An exhaustive pre-migration audit examined all dataset files in `ml/datasets/qa/`.

### Canonical Approved Datasets (Imported):
| Dataset Name | Exact File Path | Format | Record Count | Features / Keys | Documented Origin / Provenance |
|---|---|:---:|:---:|:---:|---|
| **Academic Training Split** | `ml/datasets/qa/train.jsonl` | JSONL | 1,264 | `question`, `answer` | Foundational academic training split audited and verified in Part A. |
| **Academic Validation Split** | `ml/datasets/qa/val.jsonl` | JSONL | 270 | `question`, `answer` | Foundational academic validation split audited and verified in Part A. |
| **Academic Test Split** | `ml/datasets/qa/test.jsonl` | JSONL | 272 | `question`, `answer` | Foundational academic test split audited and verified in Part A. |
| **Curated Seed Question Bank** | `ml/datasets/qa/questions.json` | JSON | 10 | `id`, `question`, `reference_answer` | Curated technical questions (OOP, DB, API, ML) used by core NLP evaluators. |
| **Total Approved Corpus** | — | — | **1,816** | — | **100% Canonical Repository Datasets** |

### Excluded Dataset Files (Documented Rationale):
1. **`ml/datasets/qa/hf_train.jsonl` (1,104 records) & `hf_val.jsonl` (123 records):**
   - *Origin:* Downloaded via `ml/convert_hf_dataset.py` from Hugging Face repository `shimogerald/interview-coach-dataset`.
   - *Exclusion Rationale:* These files were an experimental external download and were not part of the approved 1,806-record canonical corpus audited in Part A. To strictly comply with the rule against externally sourced questions, they were excluded.
2. **`ml/datasets/qa/qa_pairs.json` (3 records):**
   - *Origin:* Matches between audio video transcripts and `questions.json`.
   - *Exclusion Rationale:* Contains candidate audio transcript mappings, not standalone question bank entities.
3. **`ml/datasets/processed/*_processed.csv`:**
   - *Exclusion Rationale:* Derived tabular ML feature sets; per instructions, processed ML CSV files were not treated as canonical question banks.

---

## 3. DATABASE SCHEMA CHANGES (ADDITIVE DDL)

An additive DDL migration was designed and applied. No existing tables were dropped, truncated, or modified.

### New Table: `questions`
```sql
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
```

### SQLAlchemy ORM Model (`backend/app/models.py`)
```python
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_id = Column(String(64), unique=True, index=True, nullable=False)
    question_text = Column(Text, nullable=False)
    reference_answer = Column(Text, nullable=False)
    skill = Column(String(100), nullable=True, index=True)
    role = Column(String(100), nullable=True, index=True)
    difficulty = Column(String(50), nullable=True, index=True)
    category = Column(String(100), nullable=True, index=True)
    source_dataset = Column(String(100), nullable=False)
    source_version = Column(String(50), default="1.0", nullable=False)
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

### Pydantic Validation Schemas (`backend/app/schemas.py`)
To prevent data leaks, distinct public and internal schemas were established:
- **`QuestionPublic`:** Exposes `id`, `source_id`, `question_text`, `skill`, `role`, `difficulty`, `category`. Explicitly **omits** `reference_answer`.
- **`QuestionInternal`:** Inherits `QuestionPublic` and adds `reference_answer`, `source_dataset`, `source_version`, `is_active`, `created_at`, `updated_at`. Used strictly within backend services.

---

## 4. MIGRATION & IMPORT DETAILS

The migration process was implemented in `database/migrate_question_bank.py`.

### 1. Deterministic Source ID Fingerprinting:
- For `questions.json`: Used explicit seed IDs: `seed_1` through `seed_10`.
- For `train.jsonl`, `val.jsonl`, and `test.jsonl`: Generated collision-resistant 16-character SHA-256 fingerprints from normalized question text and reference answer:
  $$\text{fingerprint} = \text{SHA256}(\text{question.strip()} \parallel \text{answer.strip()})[:16]$$
  $$\text{source\_id} = \text{f"academic\_{split}\_{fingerprint}"}$$
- Uniqueness Check: All 1,816 generated `source_id` keys were verified to be 100% unique across the entire database.

### 2. Duplicate Detection & Cross-Split Analysis:
- **Within Splits:** Zero duplicate questions or answers were found in `train.jsonl` (1,264 unique), `val.jsonl` (270 unique), or `test.jsonl` (272 unique).
- **Between Academic Splits:** Zero cross-split overlap (Train $\cap$ Val = 0, Train $\cap$ Test = 0, Val $\cap$ Test = 0).
- **Between Academic Splits & Seed Bank:** 1 question overlap detected:
  - Question: `"What is overfitting in machine learning?"`
  - Seed answer: *"Overfitting occurs when a model learns the training data too closely and performs poorly on unseen data."*
  - Test answer: *"Overfitting occurs when a model learns training data too well, including noise, resulting in poor generalization to new data."*
  - Resolution: Because the reference answers differ and serve distinct dataset contexts, both records were retained with distinct `source_id` values (`seed_10` and `academic_test_cf2659e99a803975`), preserving full provenance without collision.

### 3. Safe Transactions & Parameterized Execution:
- All database inserts use parameterized SQL with `cursor.executemany()`:
  ```sql
  INSERT INTO `questions` (
      `source_id`, `question_text`, `reference_answer`, `skill`, `role`,
      `difficulty`, `category`, `source_dataset`, `source_version`, `is_active`,
      `created_at`, `updated_at`
  ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1, NOW(), NOW())
  ON DUPLICATE KEY UPDATE
      `question_text` = VALUES(`question_text`),
      `reference_answer` = VALUES(`reference_answer`),
      `updated_at` = NOW();
  ```
- Wrapped in explicit database transactions (`autocommit=False`) with automatic `conn.rollback()` on exceptions.

---

## 5. BACKUP & STAGING VERIFICATION

Strict database safety protocols were enforced prior to modifying the production database:

1. **Production Database Backup:**
   - Full SQL dump generated: `database/backups/backup_ai_interview_analyzer_20261105_194709.sql` (53,333 bytes).
   - All 4 pre-existing tables (`users`, `user_profiles`, `interviews`, `question_results`) dumped and verified.
2. **Staging Environment Creation:**
   - Dedicated staging database `ai_interview_analyzer_staging` created on MySQL 3307.
   - Backup restored into staging; initial row counts verified (`users`: 28, `user_profiles`: 4, `interviews`: 12, `question_results`: 12).
3. **Staging Dry-Run & Rollback Testing:**
   - Dry-run tested on staging: returned 1,816 valid records, rolled back cleanly, table count remained 0.
   - Forced exception rollback tested: verified that an error mid-transaction leaves 0 orphaned records.
   - Migration executed on staging: 1,816 records inserted.
   - Idempotency tested on staging: re-running resulted in 0 new rows, 1,816 already existing, count remained 1,816.
4. **Production Execution:**
   - Following complete staging validation, migration was executed on `ai_interview_analyzer`.
   - Output confirmed: 1,816 newly inserted records, 0 errors, existing tables completely intact.

---

## 6. ROW COUNT VERIFICATION MATRIX

| Table Name | Pre-Migration Count | Post-Migration Count | Status |
|---|:---:|:---:|:---:|
| `users` | 28 | 28 | **Intact (Unchanged)** |
| `user_profiles` | 4 | 4 | **Intact (Unchanged)** |
| `interviews` | 12 | 12 | **Intact (Unchanged)** |
| `question_results` | 12 | 12 | **Intact (Unchanged)** |
| **`questions` (New)** | **0** | **1,816** | **Successfully Populated** |

### Breakdown of `questions` Table by Source Dataset:
| Source Dataset Tag | Source File | Records in DB | Percentage |
|---|---|:---:|:---:|
| `academic_train` | `ml/datasets/qa/train.jsonl` | 1,264 | 69.60% |
| `academic_test` | `ml/datasets/qa/test.jsonl` | 272 | 14.98% |
| `academic_val` | `ml/datasets/qa/val.jsonl` | 270 | 14.87% |
| `curated_seed` | `ml/datasets/qa/questions.json` | 10 | 0.55% |
| **Total Questions in Database** | — | **1,816** | **100.0%** |

---

## 7. SECURITY & INTEGRITY AUDIT

1. **Reference Answer Confidentiality:**
   - `reference_answer` is stored strictly in the backend MySQL database.
   - `QuestionPublic` Pydantic schema excludes `reference_answer`.
   - No frontend code or public endpoint has been granted access to `reference_answer`.
2. **Credential Management:**
   - Database credentials read dynamically from environment variables (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`).
3. **Non-Null Integrity:**
   - Verified that zero records have NULL or empty `question_text` or `reference_answer`.
   - Verified that all 1,816 `source_id` keys are populated and unique.

---

## 8. TEST EXECUTION RESULTS

A dedicated automated test suite was developed in `tests/test_question_bank_migration.py` and executed alongside all existing application tests.

### Test Results (31 of 31 Passed):
```
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\AI-Interview-Analyzer
collected 31 items

tests/test_evaluator_rules.py::test_rule_a_equivalent_correct_wording PASSED [  3%]
tests/test_evaluator_rules.py::test_rule_b_correct_but_incomplete_answer PASSED [  6%]
tests/test_evaluator_rules.py::test_rule_c_misconceptions_penalized PASSED [  9%]
tests/test_evaluator_rules.py::test_rule_d_completely_unrelated_answer PASSED [ 12%]
tests/test_evaluator_rules.py::test_rule_e_empty_or_whitespace_answer PASSED [ 16%]
tests/test_evaluator_rules.py::test_rule_f_alternative_valid_implementation PASSED [ 19%]
tests/test_evaluator_rules.py::test_rule_g_technical_definition_correctness PASSED [ 22%]
tests/test_interview_api.py::test_evaluate_answer_endpoint_accurate_scoring PASSED [ 25%]
tests/test_interview_api.py::test_retry_and_transcript_editing_workflow PASSED [ 29%]
tests/test_interview_api.py::test_jwt_authorization_and_ownership_isolation PASSED [ 32%]
tests/test_interview_api.py::test_mysql_persistence_and_pdf_report PASSED [ 35%]
tests/test_no_answer_detection.py::test_no_answer_detection PASSED       [ 38%]
tests/test_provider_integration.py::test_provider_fallback_when_unconfigured PASSED [ 41%]
tests/test_provider_integration.py::test_gemini_provider_configured PASSED [ 45%]
tests/test_provider_integration.py::test_openai_provider_configured PASSED [ 48%]
tests/test_provider_integration.py::test_mock_structured_question_generation PASSED [ 51%]
tests/test_resume_and_questions.py::test_resume_parsing_python_stack PASSED [ 54%]
tests/test_resume_and_questions.py::test_resume_parsing_java_stack PASSED [ 58%]
tests/test_resume_and_questions.py::test_resume_parsing_cybersecurity_stack PASSED [ 61%]
tests/test_resume_and_questions.py::test_scanned_pdf_detection PASSED    [ 64%]
tests/test_resume_and_questions.py::test_question_duplicate_prevention PASSED [ 67%]
tests/test_resume_and_questions.py::test_personalized_question_generation_python_vs_java PASSED [ 70%]
tests/test_resume_and_questions.py::test_structured_evaluation_spec_present PASSED [ 74%]
tests/test_question_bank_migration.py::test_database_connection_and_questions_table_exists PASSED [ 77%]
tests/test_question_bank_migration.py::test_imported_record_counts_match_sources PASSED [ 80%]
tests/test_question_bank_migration.py::test_source_id_uniqueness_and_integrity PASSED [ 83%]
tests/test_question_bank_migration.py::test_question_and_answer_non_empty PASSED [ 87%]
tests/test_question_bank_migration.py::test_existing_tables_and_rows_intact PASSED [ 90%]
tests/test_question_bank_migration.py::test_migration_idempotency PASSED [ 93%]
tests/test_question_bank_migration.py::test_transactional_rollback_on_failure PASSED [ 96%]
tests/test_question_bank_migration.py::test_public_schema_excludes_reference_answer PASSED [100%]

======================= 31 passed, 8 warnings in 59.32s =======================
```

---

## 9. KNOWN ISSUES & LIMITATIONS

1. **Source Metadata Nullability:** The raw academic JSONL files (`train.jsonl`, `val.jsonl`, `test.jsonl`) only provided `question` and `answer`. As strictly instructed ("Never invent missing metadata"), the optional fields (`skill`, `role`, `difficulty`, `category`) were set to `NULL` for these records. In subsequent steps, domain categorization can be applied via deterministic topic keyword clustering without fabricating synthetic tags.
2. **Active Retrieval Still Inactive:** Per Section 8 ("Strict Scope Limit"), the live question selection engine in `main.py` and frontend question delivery have not yet been switched to read from the new `questions` table. This preserves all existing functionality until Part B Step 3.

---
*Report compiled autonomously by Senior Full-Stack & ML Audit Agent. Migration completed with zero regressions.*
