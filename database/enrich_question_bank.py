"""
================================================================================
QUESTION BANK METADATA ENRICHMENT ENGINE
Part B: Category, Difficulty, Role & Technical Skill Classification
Project: AI Interview Analyzer
Workspace: D:\\AI-Interview-Analyzer
================================================================================

This module performs deterministic, rule-based NLP classification across all
records in the MySQL `questions` table to enrich:
1. `category`: Normalized technical domain (9 canonical categories)
2. `difficulty`: Calibrated cognitive depth (Easy, Medium, Hard)
3. `role`: Target job role alignment matching frontend setup dropdowns
4. `skill`: Primary technical skill / technology extracted from the prompt
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
from collections import Counter
import pymysql
from dotenv import load_dotenv

# Ensure root directory is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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

# Auto-detect MySQL port
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
# 1. CANONICAL DOMAIN TAXONOMY & ROLE MAPPING
# ------------------------------------------------------------------------------

TAXONOMY_RULES = [
    (
        "Frontend & Web Development",
        "Frontend Developer",
        [
            r"\b(css|html|dom|javascript|typescript|react|vue|angular|webpack|vite|browser|responsive|flexbox|grid|specificity|frontend|ui|ux|aria|accessibility|cors|localstorage|sessionstorage|cookies|async/await|promises?|promise\.all|promise\.race|webrtc|closure|event loop|fetch api|virtual dom|state management|redux|spa|svg|canvas|repaint|reflow|shadow dom|web components)\b"
        ],
        "JavaScript"
    ),
    (
        "Machine Learning & AI",
        "Machine Learning Engineer",
        [
            r"\b(machine learning|deep learning|neural network|bias-variance|gradient descent|regression|classification|federated learning|overfitting|underfitting|nlp|llm|embeddings?|clustering|supervised|unsupervised|transformer|epochs?|loss function|random forest|hyperparameters?|regularization|lasso|ridge|cross-validation|kmeans|pca|backpropagation|activation function|relu|softmax|dataset|feature engineering|computer vision|reinforcement learning|bert|gpt|gan|generative ai|gru|lstm|autoencoder|vae|convolutional|cnn|rnn|roc-auc|precision-recall|f1-score|molecular docking)\b"
        ],
        "Machine Learning"
    ),
    (
        "Data Science & Analytics",
        "Data Analyst",
        [
            r"\b(data science|hypothesis testing|correlation|p-value|statistical|ab test|a/b testing|sankey|data visualization|matplotlib|seaborn|tableau|power bi|powerbi|descriptive statistics|inferential|data storytelling|eda|exploratory data|pandas|dataframe|numpy|business intelligence|bi dashboard|central limit theorem|z-score|chi-square|anova|distribution)\b"
        ],
        "Data Analysis"
    ),
    (
        "Data Engineering & Governance",
        "Data Analyst",
        [
            r"\b(data observability|data catalog|data governance|data lineage|metadata management|data quality|etl|elt|data pipeline|data lake|lakehouse|data warehouse|bigquery|snowflake|databricks|apache spark|pyspark|hadoop|dbt|apache airflow|data mesh|watermarking|anonymization|pseudonymization)\b"
        ],
        "Data Engineering"
    ),
    (
        "Cloud & Cybersecurity",
        "DevOps Engineer",
        [
            r"\b(security|threat|vulnerability|oauth2?|auth|cipher|encryption|decryption|firewall|pki|zero trust|penetration|incident|soc|siem|attack|phishing|iam|tls|ssl|access control|compromise|exploit|credential|jwt|csrf|xss|sql injection|dos|ddos|hashing|integrity|confidentiality|authorization|authentication|mfa|rbac|sbom|software bill of materials|dlp|data loss prevention|data masking|gdpr|hipaa|secure configuration|governance|audit|compliance|cve|mitre|cryptography|symmetric|asymmetric|hmac|signature|key exchange|diffie-hellman|rsa|elliptic curve|blockchain|smart contract|liquidity pool)\b"
        ],
        "Cybersecurity"
    ),
    (
        "Database & Storage Architecture",
        "Backend Developer",
        [
            r"\b(database|sql|nosql|acid|transactions?|index|indexing|sharding|replication|query optimization|postgres|postgresql|mysql|redis|mongodb|rdbms|b-tree|schema|storage engine|wal|write-ahead|normalization|denormalization|foreign key|primary key|isolation levels?|concurrency control|deadlocks?|optimistic locking|pessimistic locking|cap theorem|olap|oltp|connection pool|caching|memcached|distributed storage|bloom filter|lsm tree)\b"
        ],
        "SQL & Databases"
    ),
    (
        "Operating Systems & Systems",
        "Software Engineer",
        [
            r"\b(context switch|operating system|kernel|virtual memory|paging|segmentation|threads?|mutex|semaphore|syscall|device drivers?|interrupts?|process|cpu scheduling|concurrency|race conditions?|ipc|inter-process|sockets?|memory pool|buffer overflow|heap|stack|io multiplexing|epoll|kqueue|file system|inode|posix|fork|exec|signals?|producer-consumer|out-of-order execution|raid|gustafson|amdahl|cpu cache|instruction pipelining|cache coherence|multiprocessing|multithreading|clock skew|hardware|firmware)\b"
        ],
        "Operating Systems"
    ),
    (
        "DevOps & Cloud Infrastructure",
        "DevOps Engineer",
        [
            r"\b(docker|containers?|kubernetes|k8s|ci/cd|pipeline|terraform|ansible|git|rebase|merge|branch|observability|prometheus|grafana|helm|deployments?|infrastructure as code|iac|cloudformation|aws|azure|gcp|serverless|lambda|nginx|load balancing|reverse proxy|monitoring|telemetry|logging|elk|datadog|chaos engineering|disaster recovery|rpo|rto|site reliability|sre|slo|sla|sli|failover|zero-downtime|blue-green|canary)\b"
        ],
        "DevOps & Cloud"
    ),
    (
        "Backend & Distributed Systems",
        "Backend Developer",
        [
            r"\b(microservices|rest|apis?|grpc|graphql|kafka|message queue|rabbitmq|event-driven|distributed systems?|consensus|raft|paxos|rate limit|latency|throughput|saga|orchestrat(or|ion)|choreography|circuit breaker|pub/sub|webhook|idempotency|eventual consistency|service mesh|rpc|web socket|websockets?|tcp|udp|http/2|http/3|service locator|load balancer|api gateway)\b"
        ],
        "Backend Architecture"
    ),
    (
        "Software Engineering & Architecture",
        "Software Engineer",
        [
            r"\b(polymorphism|inheritance|encapsulation|abstraction|design patterns?|singleton|factory|solid principles?|unit tests?|integration tests?|refactoring|code review|agile|scrum|data structures?|algorithms?|complexity|o\(n\)|recursion|binary tree|graphs?|linked list|sorting|hash table|hash collision|chaining|open addressing|interfaces?|abstract class|composition|stream api|entity|value object|high cohesion|loose coupling|domain-driven|bounded context|hexagonal architecture|clean architecture|dependency injection|dry|kiss|yagni|oop|object-oriented)\b"
        ],
        "Software Engineering"
    )
]

# Primary Technical Skills Extractor patterns
SKILL_PATTERNS = [
    (r"\b(python|gil|asyncio|flask|django|fastapi|pandas|numpy)\b", "Python"),
    (r"\b(java|jvm|spring|spring boot|garbage collection|stream api)\b", "Java"),
    (r"\b(javascript|typescript|node\.?js|react|vue|angular|dom|css|html)\b", "JavaScript / Web"),
    (r"\b(c\+\+|cpp|pointers?|raii|memory pool|valgrind)\b", "C++ / Systems"),
    (r"\b(sql|postgres|postgresql|mysql|database|nosql|mongodb|redis|acid)\b", "SQL & Databases"),
    (r"\b(docker|kubernetes|k8s|container)\b", "Docker / Kubernetes"),
    (r"\b(git|rebase|merge|branch)\b", "Git Version Control"),
    (r"\b(aws|azure|gcp|cloud|serverless|s3|ec2)\b", "Cloud Architecture"),
    (r"\b(oauth2?|jwt|encryption|cipher|pki|tls|ssl|security|vulnerability|firewall)\b", "Cybersecurity"),
    (r"\b(linux|unix|posix|bash|kernel|syscall|/proc)\b", "Linux & Systems"),
    (r"\b(machine learning|deep learning|neural|nlp|llm|transformer|random forest)\b", "Machine Learning"),
    (r"\b(kafka|rabbitmq|grpc|rest|microservices|api)\b", "Distributed Systems & APIs"),
    (r"\b(data structures?|algorithms?|binary tree|graph|sorting|hash table)\b", "Data Structures & Algorithms")
]

# Difficulty Keywords
HARD_KEYWORDS = {
    "consensus", "raft", "paxos", "distributed", "concurrency", "race condition",
    "deadlock", "mutex", "semaphore", "low level", "internals", "kernel", "virtual memory",
    "memory pool", "paging", "segmentation", "context switch", "bias-variance",
    "regularization", "federated", "sharding", "replication", "b-tree", "wal",
    "acid", "isolation level", "zero trust", "mitigate", "vulnerability", "exploit",
    "chaos engineering", "disaster recovery", "rpo", "rto", "exhaustion", "microservices",
    "saga", "orchestrat", "trade-off", "tradeoff", "bottleneck", "latency", "throughput",
    "cipher", "encryption", "pki", "oauth2", "under the hood", "failure mode", "threat model",
    "clock skew", "byzantine", "memory leak", "cache coherence", "out-of-order execution"
}

MEDIUM_KEYWORDS = {
    "how does", "how do", "explain", "describe", "difference between", "compare",
    "what happens", "role of", "purpose of", "when would", "best practice",
    "implement", "advantages", "disadvantages", "distinction", "strategies", "workflow"
}


# ------------------------------------------------------------------------------
# 2. CLASSIFICATION LOGIC
# ------------------------------------------------------------------------------

def classify_question_record(
    question_text: str,
    reference_answer: str
) -> Dict[str, str]:
    """
    Classifies a question-answer pair into category, difficulty, role, and skill.
    Guarantees deterministic, reproducible, non-null outputs.
    """
    q_clean = question_text.strip()
    a_clean = reference_answer.strip()
    q_lower = q_clean.lower()
    full_text = f"{q_clean} {a_clean}".lower()

    # 1. Category & Role Classification
    assigned_category = None
    assigned_role = None
    default_skill = "Software Engineering"

    for cat_name, role_name, patterns, skill_label in TAXONOMY_RULES:
        if any(re.search(pat, full_text) for pat in patterns):
            assigned_category = cat_name
            assigned_role = role_name
            default_skill = skill_label
            break

    if not assigned_category:
        assigned_category = "Software Engineering & Architecture"
        assigned_role = "Software Engineer"
        default_skill = "Software Engineering"

    # 2. Primary Technical Skill Extraction
    extracted_skill = None
    for pat, skill_name in SKILL_PATTERNS:
        if re.search(pat, full_text):
            extracted_skill = skill_name
            break

    final_skill = extracted_skill or default_skill

    # 3. Difficulty Classification
    has_hard_kw = any(k in q_lower for k in HARD_KEYWORDS)
    has_medium_kw = any(k in q_lower for k in MEDIUM_KEYWORDS)

    if has_hard_kw or (has_medium_kw and len(q_clean) >= 65):
        assigned_difficulty = "Hard"
    elif has_medium_kw or len(q_clean) >= 42:
        assigned_difficulty = "Medium"
    else:
        assigned_difficulty = "Easy"

    return {
        "category": assigned_category,
        "difficulty": assigned_difficulty,
        "role": assigned_role,
        "skill": final_skill
    }


# ------------------------------------------------------------------------------
# 3. DATABASE ENRICHMENT EXECUTOR
# ------------------------------------------------------------------------------

def enrich_database_questions(
    db_name: str = DEFAULT_DB_NAME,
    dry_run: bool = False,
    force_all: bool = False
) -> Dict[str, Any]:
    """
    Connects to MySQL, scans all rows in `questions` table, and applies
    enriched metadata (category, difficulty, role, skill).
    """
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=db_name,
        charset="utf8mb4",
        autocommit=False
    )

    report = {
        "target_database": db_name,
        "dry_run": dry_run,
        "total_records": 0,
        "updated_records": 0,
        "category_counts": {},
        "difficulty_counts": {},
        "role_counts": {},
        "skill_counts": {},
        "status": "IN_PROGRESS"
    }

    try:
        with conn.cursor() as cursor:
            # Check row count
            cursor.execute("SELECT COUNT(*) FROM `questions`;")
            total = cursor.fetchone()[0]
            report["total_records"] = total

            if total == 0:
                print(f"[ENRICH] questions table in '{db_name}' is empty.")
                report["status"] = "EMPTY_TABLE"
                return report

            # Query rows requiring enrichment
            if force_all:
                cursor.execute("SELECT id, question_text, reference_answer FROM `questions`;")
            else:
                cursor.execute("""
                    SELECT id, question_text, reference_answer FROM `questions`
                    WHERE category IS NULL OR difficulty IS NULL OR role IS NULL OR skill IS NULL;
                """)

            rows = cursor.fetchall()
            print(f"[ENRICH] Identified {len(rows)} records requiring metadata enrichment (total in table: {total}).")

            update_sql = """
                UPDATE `questions`
                SET category = %s, difficulty = %s, role = %s, skill = %s, updated_at = NOW()
                WHERE id = %s;
            """

            update_batch = []
            cat_counter = Counter()
            diff_counter = Counter()
            role_counter = Counter()
            skill_counter = Counter()

            for r_id, q_text, ref_ans in rows:
                meta = classify_question_record(q_text, ref_ans)
                cat_counter[meta["category"]] += 1
                diff_counter[meta["difficulty"]] += 1
                role_counter[meta["role"]] += 1
                skill_counter[meta["skill"]] += 1

                update_batch.append((
                    meta["category"],
                    meta["difficulty"],
                    meta["role"],
                    meta["skill"],
                    r_id
                ))

            report["category_counts"] = dict(cat_counter.most_common())
            report["difficulty_counts"] = dict(diff_counter.most_common())
            report["role_counts"] = dict(role_counter.most_common())
            report["skill_counts"] = dict(skill_counter.most_common(10))

            if not dry_run and update_batch:
                print(f"[ENRICH] Executing batch update on {len(update_batch)} records in MySQL...")
                cursor.executemany(update_sql, update_batch)
                conn.commit()
                report["updated_records"] = len(update_batch)
                print(f"[ENRICH] Successfully committed {len(update_batch)} enriched rows.")
            else:
                report["updated_records"] = 0
                if dry_run:
                    print(f"[ENRICH] DRY RUN active: 0 records committed.")

            report["status"] = "SUCCESS"

    except Exception as e:
        conn.rollback()
        report["status"] = "FAILED"
        report["error"] = str(e)
        raise
    finally:
        conn.close()

    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Enrich question bank metadata in MySQL")
    parser.add_argument("--db", default=DEFAULT_DB_NAME, help="Target database name")
    parser.add_argument("--dry-run", action="store_true", help="Inspect classifications without writing to DB")
    parser.add_argument("--force", action="store_true", help="Re-classify all records even if already set")
    args = parser.parse_args()

    result = enrich_database_questions(db_name=args.db, dry_run=args.dry_run, force_all=args.force)
    print("\n--- ENRICHMENT REPORT ---")
    print("Database:", result["target_database"])
    print("Status:", result["status"])
    print("Total Records in DB:", result["total_records"])
    print("Updated Records:", result["updated_records"])
    print("\nCategories:")
    for k, v in result["category_counts"].items():
        print(f"  • {k}: {v}")
    print("\nDifficulties:")
    for k, v in result["difficulty_counts"].items():
        print(f"  • {k}: {v}")
    print("\nRoles:")
    for k, v in result["role_counts"].items():
        print(f"  • {k}: {v}")
    print("\nTop Skills:")
    for k, v in result["skill_counts"].items():
        print(f"  • {k}: {v}")

