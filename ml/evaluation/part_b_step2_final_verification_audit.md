# PART B – STEP 2: FINAL VERIFICATION AUDIT (READ-ONLY)

**Project:** AI Interview Analyzer  
**Workspace:** `D:\AI-Interview-Analyzer`  
**Audit Date:** November 2026  
**Auditor:** Senior Full-Stack Developer, ML Engineer & Database Auditor  
**Audit Scope:** Read-Only Verification of Database Question-Bank Migration  
**Status:** AUDIT COMPLETE (Read-Only – Zero Code or Database Modifications)

---

## 1. EXECUTIVE SUMMARY

An independent, read-only verification audit was conducted on the completed Part B Step 2 database question-bank migration. The audit evaluated four specific areas: **Dataset Split Integrity & Evaluation Leakage**, **Seed Bank Provenance**, **Reference-Answer Security**, and **Database Environment Verification**.

### High-Level Audit Findings & Status Matrix:
| Verification Area | Focus | Audit Finding | Status |
|---|---|---|:---:|
| **1. Dataset Split Integrity** | Train/Val/Test Separation & Leakage | All 1,806 records (including 270 val and 272 test records) were imported with `is_active = 1`. Serving val/test records in live interviews introduces academic evaluation leakage. | **WARNING / FAIL** |
| **2. Seed Bank Provenance** | `questions.json` (10 records) | All 10 records verified, but no formal provenance, authorship, or explicit academic sign-off exists in documentation. | **NOT VERIFIED** |
| **3. Reference-Answer Security** | Client Exposure & Authorization | Public endpoints `GET /interview/questions` and `POST /interview/questions` return `reference_answer` and `evaluation_spec` in plaintext to unauthenticated callers. | **FAIL (CRITICAL)** |
| **4. Database Environment** | Staging vs Production & Backup | Both `ai_interview_analyzer` and `ai_interview_analyzer_staging` hold 1,816 records. Pristine pre-migration backup verified. | **PASS** |

---

## 2. AREA 1: DATASET SPLIT INTEGRITY & EVALUATION LEAKAGE RISK

### 2.1 Source Files & Partition Breakdown
The 1,806 academic records imported into the MySQL `questions` table originate from three exact files in `ml/datasets/qa/`:

| Split Name | Source File Path | Record Count | Format | Verified MySQL Tag (`source_dataset`) |
|---|---|:---:|:---:|---|
| **Training Set** | `ml/datasets/qa/train.jsonl` | 1,264 | JSONL | `academic_train` |
| **Validation Set** | `ml/datasets/qa/val.jsonl` | 270 | JSONL | `academic_val` |
| **Test Set** | `ml/datasets/qa/test.jsonl` | 272 | JSONL | `academic_test` |
| **Total Academic Corpus** | — | **1,806** | — | — |

### 2.2 Current Operational Status
- **Current Database State:** In `ai_interview_analyzer.questions`, all 1,806 academic records are currently flagged with `is_active = 1`.
- **Finding:** The operational question bank currently includes **all three splits** (`academic_train`, `academic_val`, and `academic_test`) without operational partition filtering.

### 2.3 Evaluation Leakage Analysis
In Part A (Academic Machine Learning Module), supervised models (KNN, SVM, Decision Tree) and the academic feature scaler were fitted strictly on the 1,264 training records, while model generalization and syllabus metrics (Confusion Matrix, Precision, Recall, F1, ROC-AUC) were calculated against `val_processed.csv` (270 records) and `test_processed.csv` (272 records).

**Academic Evaluation Leakage Risk:**
1. If validation and test questions are served to candidates in live mock interviews, the held-out test partition is no longer isolated from user practice and operational feedback.
2. If candidate answers collected during live interviews are ever incorporated into model re-tuning or syllabus demonstrations, test-set contamination occurs.
3. Out-of-sample validity is compromised if questions intended for academic model auditing are actively practiced by candidates.

### 2.4 Status: **WARNING / FAIL (Test Contamination in Operational Pool)**

### 2.5 Recommended Safe Separation Strategy (To Be Implemented in Step 3):
1. **Quarantine Validation and Test Records:** Update the `questions` table so that records where `source_dataset IN ('academic_val', 'academic_test')` have `is_active = 0` (or add a dedicated `split_type ENUM('train', 'val', 'test') DEFAULT 'train'` column).
2. **Operational Pool Restriction:** Ensure the live question selection engine queries strictly `WHERE is_active = 1 AND source_dataset = 'academic_train'` (providing an ample pool of 1,264 verified technical questions).
3. **Academic Benchmark Isolation:** Reserve `academic_val` and `academic_test` exclusively for offline ML benchmarking and university syllabus practical verification.

---

## 3. AREA 2: SEED BANK PROVENANCE (`questions.json`)

### 3.1 Inventory of Exact Records in `ml/datasets/qa/questions.json`
The file `ml/datasets/qa/questions.json` (2,179 bytes, created Tue Aug 25 20:44:58 2026) was inspected record by record:

| ID | Verified Question Text | Reference Answer Text |
|:---:|---|---|
| **1** | What is polymorphism in object oriented programming? | Polymorphism allows the same interface or method to behave differently for different objects. |
| **2** | What is inheritance in object oriented programming? | Inheritance allows a class to acquire properties and methods from another class. |
| **3** | What is encapsulation? | Encapsulation is the concept of bundling data and methods together and restricting direct access to internal data. |
| **4** | What is abstraction? | Abstraction hides unnecessary implementation details and exposes only the essential functionality. |
| **5** | What is a primary key in a database? | A primary key uniquely identifies each record in a database table. |
| **6** | What is normalization in a database? | Normalization organizes database data to reduce redundancy and improve data integrity. |
| **7** | What is an API? | An API is an interface that allows different software applications to communicate with each other. |
| **8** | What is REST API? | A REST API is an API that follows REST architectural principles and commonly uses HTTP methods to operate on resources. |
| **9** | What is machine learning? | Machine learning is a method where computers learn patterns from data to make predictions or decisions. |
| **10** | What is overfitting in machine learning? | Overfitting occurs when a model learns the training data too closely and performs poorly on unseen data. |

### 3.2 Provenance & History Audit
- **Codebase Usage:** The file is referenced in early exploratory scripts:
  - `ml/extract_qa.py` (matches video transcript lines against these 10 questions).
  - `ml/qa_analyzer.py` (early test script testing SentenceTransformer cosine similarity against question 0).
  - `ml/qa_engine.py` (early scoring prototype).
- **Documentation & Attribution:** `ml/datasets/README.md` contains no mention of `questions.json`, its authors, origin, or license.
- **Academic Approval Status in Part A:** In Part A Step 1 (Dataset Audit) and Step 2 (Dataset Preprocessing), the academic committee/guidelines explicitly evaluated and approved the 1,806 records in `train.jsonl`, `val.jsonl`, and `test.jsonl`. `questions.json` was not part of the Part A supervised/unsupervised ML pipeline.

### 3.3 Status: **NOT VERIFIED (Unverified Provenance)**

### 3.4 Recommended Correction (To Be Decided Before Step 3):
- Either document formal academic advisor approval to retain these 10 foundational seed questions, OR
- Set `is_active = 0` for `source_dataset = 'curated_seed'` so the live application relies 100% on the verified 1,264 academic training questions.

---

## 4. AREA 3: REFERENCE-ANSWER SECURITY & CLIENT EXPOSURE

An empirical security test of the live backend API was executed using `fastapi.testclient.TestClient`.

### 4.1 Empirical Findings on Existing Question Endpoints
When an unauthenticated HTTP GET or POST request is made to `/interview/questions`:
- **Endpoint Tested:** `GET /interview/questions?count=2`
- **HTTP Status:** `200 OK` (No authentication required)
- **Response Keys Returned:** `['status', 'personalized', 'questions']`
- **Item Keys in `questions[0]`:**
  ```json
  [
    "id", "question", "topic", "category", "difficulty",
    "expected_answer", "reference_answer", "required_concepts",
    "optional_concepts", "acceptable_alternatives",
    "common_misconceptions", "rubric", "follow_up_criteria",
    "targetTime", "track", "evaluation_spec"
  ]
  ```
- **Evidence of Data Leak:**
  ```
  CRITICAL: 'reference_answer' IS RETURNED IN GET /interview/questions!
  Sample reference_answer: "The Python GIL is a mutex that prevents multiple native threads from executing P..."
  ```
- **Identical Behavior in POST:** `POST /interview/questions` returns the exact same payload containing `reference_answer` and `evaluation_spec`.

### 4.2 Frontend Security & Network Flow Inspection
1. **Plaintext Answers in Client Code:** `frontend/script.js` (lines 24–180) contains a hardcoded array `const QUESTIONS = [...]` with 10 questions and their complete model answers.
2. **Client-Supplied Grading Payload:** When a user completes an answer in the UI, `frontend/script.js` (lines 2910–2926) executes:
   ```javascript
   body: JSON.stringify({
       question_id: q.id,
       question: q.question,
       candidate_answer: answerText,
       reference_answer: q.reference_answer,  // <--- CLIENT INJECTS MODEL ANSWER
       evaluation_spec: q.evaluation_spec     // <--- CLIENT INJECTS RUBRICS & CRITERIA
   })
   ```
3. **New `questions` Table Security Status:**
   - The newly migrated `questions` table currently has **no public REST route**.
   - The new schema `QuestionPublic` in `backend/app/schemas.py` correctly omits `reference_answer`.
   - However, the legacy endpoints (`/interview/questions` in `backend/app/main.py`) continue to leak answers from `backend/app/questions.py`.

### 4.3 Status: **FAIL (Critical Security & Evaluation Integrity Vulnerability)**

### 4.4 Recommended Correction (Mandatory for Part B Step 3):
1. **Refactor `/interview/questions`:** Query only `id`, `question_text`, `skill`, `role`, `difficulty`, `category` from the `questions` table using `QuestionPublic`. Completely omit `reference_answer`, `expected_answer`, and `evaluation_spec` from the response.
2. **Secure `/evaluate-answer`:** Update `EvaluateAnswerRequest` in `main.py` so the client sends ONLY `question_id` and `candidate_answer`. The server must query `reference_answer` securely from the MySQL database using `question_id`.
3. **Purge Frontend Question Array:** Remove `const QUESTIONS = [...]` from `frontend/script.js`.

---

## 5. AREA 4: DATABASE ENVIRONMENT VERIFICATION

### 5.1 Host & Connection Details
- **MySQL Host:** `127.0.0.1` (localhost)
- **Port:** `3307`
- **Database Engine:** MySQL 8.0 / MariaDB
- **User:** `root`

### 5.2 Database Distinction (Staging vs. Production)
Two distinct databases exist on the server:
1. **`ai_interview_analyzer` (Application / Production Database):**
   - Configured in `.env` and `backend/app/database.py` as the live target database.
   - Holds active user accounts, completed interviews, and the newly populated question bank.
2. **`ai_interview_analyzer_staging` (Staging / Development Database):**
   - Created in Step 2 specifically for dry-run validation, rollback error testing, and idempotency verification before touching production.

### 5.3 Live Record Count Verification (Read-Only)
Direct read-only inspection confirmed identical question-bank data across both environments without data loss:

| Table Name | `ai_interview_analyzer` (Live) | `ai_interview_analyzer_staging` (Staging) | Verification Status |
|---|:---:|:---:|:---:|
| `users` | 33 rows | 28 rows | **PASS** (Additional test users from pytest) |
| `user_profiles` | 4 rows | 4 rows | **PASS** (Intact) |
| `interviews` | 14 rows | 12 rows | **PASS** (Additional test interviews from pytest) |
| `question_results` | 14 rows | 12 rows | **PASS** (Additional test results from pytest) |
| **`questions` (Total)** | **1,816 rows** | **1,816 rows** | **PASS (Exact Match)** |
| ↳ `academic_train` | 1,264 rows | 1,264 rows | **PASS (Exact Match)** |
| ↳ `academic_test` | 272 rows | 272 rows | **PASS (Exact Match)** |
| ↳ `academic_val` | 270 rows | 270 rows | **PASS (Exact Match)** |
| ↳ `curated_seed` | 10 rows | 10 rows | **PASS (Exact Match)** |

### 5.4 Pre-Migration Backup Verification
- **Backup File Path:** [`database/backups/backup_ai_interview_analyzer_20261105_194709.sql`](file:///D:/AI-Interview-Analyzer/database/backups/backup_ai_interview_analyzer_20261105_194709.sql)
- **File Size:** 53,333 bytes
- **Creation Timestamp:** `2026-11-05T19:47:09.315033`
- **Database Represented:** `ai_interview_analyzer`
- **Tables Dumped:** `interviews` (12 rows), `question_results` (12 rows), `user_profiles` (4 rows), `users` (28 rows).
- **Pre-Migration Integrity:** Confirmed that `CREATE TABLE questions` is **not** in the backup, verifying that the backup captured the pristine pre-migration database state.

### 5.5 Status: **PASS**

---

## 6. CONSOLIDATED AUDIT SUMMARY & ACTIONABLE RECOMMENDATIONS

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PART B STEP 2 FINAL AUDIT SCORECARD                             │
├─────────────────────────────────────────────────┬──────────────┬───────────────────────┤
│ Verification Area                               │ Status       │ Core Action for Step 3│
├─────────────────────────────────────────────────┼──────────────┼───────────────────────┤
│ 1. Dataset Split Integrity & Leakage            │ WARNING/FAIL │ Quarantine Val/Test   │
│ 2. Seed Bank Provenance (questions.json)        │ NOT VERIFIED │ Advisor sign-off/Flag │
│ 3. Reference-Answer Public Exposure             │ FAIL (CRIT)  │ Server-side lookup    │
│ 4. Database Environment & Backup Verification   │ PASS         │ Clean dual DBs & dump │
└─────────────────────────────────────────────────┴──────────────┴───────────────────────┘
```

### Action Plan for Part B Step 3 (Pending User Approval):
1. **Split Quarantining:** In `questions` table, set `is_active = 0` for `academic_val` and `academic_test`, restricting live question selection strictly to `academic_train` (1,264 questions).
2. **Server-Side Reference Lookup:** Migrate `backend/app/main.py` (`POST /evaluate-answer`) to fetch `reference_answer` securely from MySQL by `question_id`.
3. **Data Leak Elimination:** Update `GET /interview/questions` and `POST /interview/questions` to serialize questions using `QuestionPublic`, ensuring reference answers and rubrics never leave the server.
4. **Frontend Hardening:** Remove hardcoded `QUESTIONS` array in `frontend/script.js` and eliminate client-side reference answer transmission.

---
*Report autonomously compiled by Senior Full-Stack & ML Auditor. Zero application files or databases were altered during this audit.*
