import pytest
from backend.app.services.resume_parser import (
    extract_skills_from_text,
    infer_experience_level_and_role,
    parse_resume,
    extract_text_from_file_bytes
)
from backend.app.questions import (
    is_duplicate_question,
    synthesize_project_question,
    generate_personalized_questions
)

def test_resume_parsing_python_stack():
    """Verify skill extraction and profile structuring for a Python/Django/MySQL resume."""
    resume_text = """
    John Doe
    Email: john@example.com
    Target Role: Backend Engineer
    Skills: Python, Django, FastAPI, REST APIs, MySQL, Redis, Docker, Git.
    Experience: 3 years building microservices at TechCorp.
    Projects:
    - E-Commerce API: Built high-throughput product catalog using Python, Django, and MySQL.
    Education: B.Tech in Computer Science, 2021.
    """
    parsed = parse_resume(resume_text, "resume.pdf")
    skills = parsed["skills"]
    assert "Python" in skills
    assert "Django" in skills
    assert "FastAPI" in skills
    assert "MySQL" in skills
    assert "Redis" in skills
    # Never invent unmentioned skills
    assert "Java" not in skills
    assert "PHP" not in skills
    assert "C#" not in skills
    assert len(parsed["projects"]) >= 1
    assert "Mid Level" in parsed["experience_level"]

def test_resume_parsing_java_stack():
    """Verify skill extraction and profile structuring for a Java/Spring Boot/Oracle resume."""
    resume_text = """
    Jane Smith - Senior Java Developer
    Email: jane@example.com
    Technical Skills: Java, Spring Boot, Hibernate, Microservices, Oracle, Kafka, Kubernetes.
    Experience: 6 years developing enterprise banking applications.
    Projects:
    - Banking Core Engine: Scalable payment processing pipeline built with Java and Spring Boot.
    """
    parsed = parse_resume(resume_text, "jane_resume.pdf")
    skills = parsed["skills"]
    assert "Java" in skills
    assert "Spring Boot" in skills
    assert "Oracle" in skills
    assert "Kafka" in skills
    # Never invent unmentioned skills
    assert "Django" not in skills
    assert "PHP" not in skills
    assert "Senior" in parsed["experience_level"]

def test_resume_parsing_cybersecurity_stack():
    """Verify skill extraction for Cybersecurity profile."""
    resume_text = """
    Alex Rivera - Security Analyst
    Skills: Cybersecurity, Penetration Testing, OWASP Top 10, Wireshark, Cryptography, SIEM, Firewalls, Vulnerability Assessment.
    Experience: 2 years conducting web penetration audits.
    """
    parsed = parse_resume(resume_text, "alex_cyber.pdf")
    skills = parsed["skills"]
    assert "Cybersecurity" in skills
    assert "Penetration Testing" in skills
    assert "OWASP" in skills
    assert "Wireshark" in skills

def test_scanned_pdf_detection():
    """Handle scanned PDFs gracefully by showing a helpful message when text cannot be extracted."""
    # A dummy binary that contains PDF header but zero extractable text streams
    dummy_scanned_pdf = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R >>\nendobj\nxref\n0 4\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    
    with pytest.raises(ValueError) as excinfo:
        extract_text_from_file_bytes(dummy_scanned_pdf, "scanned_doc.pdf")
    
    assert "Scanned PDF" in str(excinfo.value) or "no extractable text" in str(excinfo.value)

def test_question_duplicate_prevention():
    """Ensure duplicate or superficial rewordings are rejected."""
    existing_questions = [
        {"question": "What is polymorphism in object oriented programming?"},
        {"question": "How does database normalization reduce redundancy?"}
    ]
    
    # Exact duplicate
    assert is_duplicate_question("What is polymorphism in object oriented programming?", existing_questions) is True
    
    # Lexical / semantic duplicate
    assert is_duplicate_question("Explain polymorphism in object oriented programming with examples.", existing_questions) is True
    
    # Distinct question
    assert is_duplicate_question("What are the advantages of B-Tree indexes in MySQL?", existing_questions) is False

def test_personalized_question_generation_python_vs_java():
    """Verify dynamic question generation generates questions tailored to candidate's actual skills."""
    python_profile = {
        "target_role": "Python Backend Engineer",
        "skills": "Python, Django, MySQL, REST APIs",
        "parsed_resume": {
            "skills": ["Python", "Django", "MySQL", "REST APIs"],
            "projects": [{"title": "Payment Microservice", "description": "Django REST API with MySQL"}]
        }
    }
    
    java_profile = {
        "target_role": "Java Enterprise Engineer",
        "skills": "Java, Spring Boot, Oracle, Microservices",
        "parsed_resume": {
            "skills": ["Java", "Spring Boot", "Oracle", "Microservices"],
            "projects": [{"title": "Trading Platform", "description": "Spring Boot service backed by Oracle"}]
        }
    }
    
    py_questions = generate_personalized_questions(python_profile, num_questions=3)
    java_questions = generate_personalized_questions(java_profile, num_questions=3)
    
    # Python questions must mention Python, Django, MySQL or candidate project
    py_topics = [q.get("category", "") + " " + q.get("question", "") for q in py_questions]
    py_combined = " ".join(py_topics).lower()
    assert "python" in py_combined or "django" in py_combined or "mysql" in py_combined or "payment microservice" in py_combined
    assert "spring boot" not in py_combined
    
    # Java questions must mention Java, Spring Boot, Oracle or candidate project
    java_topics = [q.get("category", "") + " " + q.get("question", "") for q in java_questions]
    java_combined = " ".join(java_topics).lower()
    assert "java" in java_combined or "spring" in java_combined or "oracle" in java_combined or "trading platform" in java_combined
    assert "django" not in java_combined

def test_structured_evaluation_spec_present():
    """Verify each generated question has a full structured evaluation specification."""
    profile = {
        "target_role": "Backend Developer",
        "skills": "Python, Django, MySQL",
        "parsed_resume": {"skills": ["Python", "Django", "MySQL"]}
    }
    questions = generate_personalized_questions(profile, num_questions=3)
    for q in questions:
        assert "question" in q
        assert "evaluation_spec" in q
        spec = q["evaluation_spec"]
        assert "required_concepts" in spec
        assert "rubric" in spec
        assert len(spec["required_concepts"]) > 0
