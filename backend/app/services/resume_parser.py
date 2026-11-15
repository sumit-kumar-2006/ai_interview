import re
import os
from typing import Dict, Any, List, Optional, Tuple, Union
from pypdf import PdfReader
import docx

ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_RESUME_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

# Comprehensive Skill Catalog by Category
SKILL_TAXONOMY: Dict[str, List[str]] = {
    "Programming Languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "C", "Go", "Golang",
        "Rust", "Ruby", "PHP", "Swift", "Kotlin", "SQL", "HTML", "HTML5", "CSS", "CSS3",
        "Bash", "Shell", "R", "Dart", "Scala", "MATLAB", "Perl"
    ],
    "Frameworks & Web Technologies": [
        "React", "React.js", "Next.js", "Vue", "Vue.js", "Angular", "Node.js", "Express",
        "Express.js", "Django", "FastAPI", "Flask", "Spring", "Spring Boot", "ASP.NET",
        "ASP.NET Core", "Laravel", "Ruby on Rails", "Tailwind CSS", "Bootstrap", "Redux",
        "Zustand", "GraphQL", "REST", "RESTful APIs", "WebSockets", "jQuery"
    ],
    "Databases & Caching": [
        "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Oracle", "Microsoft SQL Server",
        "MSSQL", "Cassandra", "DynamoDB", "Elasticsearch", "Firebase", "Supabase", "Prisma",
        "SQLAlchemy", "Hibernate", "Kafka", "Apache Kafka", "RabbitMQ"
    ],
    "Cloud & DevOps": [
        "AWS", "Amazon Web Services", "Azure", "Microsoft Azure", "GCP", "Google Cloud",
        "Docker", "Kubernetes", "CI/CD", "GitHub Actions", "GitLab CI", "Jenkins",
        "Terraform", "Linux", "Ubuntu", "Nginx", "Apache", "Ansible", "Prometheus", "Grafana"
    ],
    "AI, ML & Data Science": [
        "Machine Learning", "Deep Learning", "Artificial Intelligence", "NLP", "Natural Language Processing",
        "Computer Vision", "PyTorch", "TensorFlow", "Keras", "Scikit-Learn", "Pandas", "NumPy",
        "OpenCV", "Hugging Face", "Transformers", "Whisper", "MediaPipe", "LLM", "Generative AI",
        "Data Analysis", "Matplotlib", "Seaborn"
    ],
    "Cybersecurity": [
        "Cybersecurity", "Network Security", "Penetration Testing", "Ethical Hacking",
        "OWASP", "Cryptography", "Vulnerability Assessment", "SIEM", "SOC", "Firewall",
        "Wireshark", "Kali Linux", "Burp Suite", "Identity and Access Management", "IAM",
        "Incident Response", "Malware Analysis"
    ],
    "Developer Tools & Practices": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Postman", "Jira", "Figma", "VS Code",
        "Docker Compose", "Microservices", "System Design", "OOP", "Object Oriented Programming",
        "Data Structures", "Algorithms", "Agile", "Scrum", "TDD", "Unit Testing", "PyTest", "Jest"
    ]
}


def sanitize_filename(filename: str) -> str:
    """Strip dangerous characters and path traversal indicators from filename."""
    base = os.path.basename(filename or "resume.txt")
    clean = re.sub(r'[^a-zA-Z0-9_.-]', '_', base)
    return clean[:120]


def extract_text_from_file_bytes(file_bytes: Union[bytes, str], filename: str) -> str:
    """Extract clean text from PDF, DOCX, or TXT file bytes with scanned PDF detection."""
    if isinstance(file_bytes, str):
        return file_bytes

    ext = os.path.splitext(filename.lower())[1]

    if ext == ".pdf":
        import io
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
        except Exception as e:
            raise ValueError(f"Scanned PDF or corrupt document with no extractable text: {e}")

        total_pages = len(reader.pages)
        if total_pages == 0:
            raise ValueError("The uploaded PDF has no pages.")

        pages_text = []
        for page in reader.pages:
            t = page.extract_text() or ""
            if t.strip():
                pages_text.append(t)

        extracted = "\n\n".join(pages_text).strip()
        if not extracted and total_pages > 0:
            raise ValueError(
                "The uploaded PDF appears to be a scanned document or image without a selectable text layer. "
                "Please upload a PDF with selectable text, a DOCX file, or enter your profile details."
            )
        return extracted

    elif ext == ".docx":
        import io
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(c.text.strip() for c in row.cells if c.text.strip())
                if row_text:
                    paragraphs.append(row_text)
        return "\n".join(paragraphs)

    elif ext in [".txt", ".text", ""]:
        for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                return file_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
        return file_bytes.decode("utf-8", errors="replace")

    else:
        raise ValueError(f"Unsupported resume file extension '{ext}'. Supported extensions: .pdf, .docx, .txt")


def extract_contact_info(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Extracts candidate name, email, and phone from resume text."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # 1. Email
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    email_match = re.search(email_pattern, text)
    email = email_match.group(0).strip().lower() if email_match else None

    # 2. Phone
    phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phone_match = re.search(phone_pattern, text)
    phone = phone_match.group(0).strip() if phone_match else None

    # 3. Name (typically the first non-empty, non-contact line)
    name = None
    for line in lines[:5]:
        cleaned = re.sub(r'[^a-zA-Z\s]', '', line).strip()
        words = cleaned.split()
        if 2 <= len(words) <= 4 and not any(w.lower() in ["resume", "curriculum", "vitae", "cv", "page", "profile", "contact", "email"] for w in words):
            name = " ".join(w.capitalize() for w in words)
            break

    return name, email, phone


def extract_skills_from_text(text: str) -> Dict[str, Any]:
    """
    Identifies technical skills across categories using exact word boundaries
    and case-sensitive / case-insensitive heuristics.
    """
    detected_by_category: Dict[str, List[str]] = {}
    all_detected_skills: List[str] = []
    seen = set()

    for category, skills in SKILL_TAXONOMY.items():
        cat_matches = []
        for skill in skills:
            # Special handling for single/short letters like C, R, Go
            if skill in ["C", "R"]:
                pattern = rf'(?:\b|(?<=\s)){re.escape(skill)}(?=\s*[,;/]|\s+(?:programming|language|\+\+|#))'
                flags = 0  # Case-sensitive
            elif skill in ["C++", "C#"]:
                pattern = rf'{re.escape(skill)}'
                flags = re.IGNORECASE
            elif skill in ["Go", "Golang"]:
                pattern = r'\b(Go|Golang)\b'
                flags = 0 if skill == "Go" else re.IGNORECASE
            elif skill in ["HTML", "CSS", "SQL", "AWS", "GCP", "CI/CD"]:
                pattern = rf'\b{re.escape(skill)}\b'
                flags = re.IGNORECASE
            else:
                pattern = rf'\b{re.escape(skill)}\b'
                flags = re.IGNORECASE

            if re.search(pattern, text, flags):
                standardized_name = skill
                if standardized_name.lower() not in seen:
                    cat_matches.append(standardized_name)
                    all_detected_skills.append(standardized_name)
                    seen.add(standardized_name.lower())

        if cat_matches:
            detected_by_category[category] = cat_matches

    # Key language and framework strings for quick prompts
    langs = detected_by_category.get("Programming Languages", [])
    frameworks = detected_by_category.get("Frameworks & Web Technologies", [])
    databases = detected_by_category.get("Databases & Caching", [])
    cloud = detected_by_category.get("Cloud & DevOps", [])
    ai = detected_by_category.get("AI, ML & Data Science", [])
    cyber = detected_by_category.get("Cybersecurity", [])
    tools = detected_by_category.get("Developer Tools & Practices", [])

    # Pure technical skills excluding programming languages to prevent duplication
    langs_lower = set(l.lower() for l in langs)
    tech_skills = [s for s in all_detected_skills if s.lower() not in langs_lower]

    return {
        "categorized": detected_by_category,
        "all_skills": all_detected_skills,
        "tech_skills": tech_skills,
        "languages": langs,
        "frameworks": frameworks,
        "databases": databases,
        "cloud_devops": cloud,
        "ai_data_science": ai,
        "cybersecurity": cyber,
        "developer_tools": tools,
        "total_skills_count": len(all_detected_skills)
    }


def extract_sections(text: str) -> Dict[str, str]:
    """Splits resume text into logical sections based on common headings."""
    section_patterns = {
        "education": r'\b(education|academic background|academics|qualifications)\b',
        "experience": r'\b(work experience|professional experience|experience|internships|employment history|employment)\b',
        "projects": r'\b(projects|technical projects|academic projects|personal projects|key projects)\b',
        "skills": r'\b(technical skills|skills & tools|skills|core competencies|technologies)\b',
        "certifications": r'\b(certifications|certificates|licenses|achievements|honors|awards)\b'
    }

    lines = text.split("\n")
    current_section = "summary"
    sections: Dict[str, List[str]] = {"summary": []}

    for line in lines:
        cleaned_line = line.strip().lower()
        matched_section = None
        # Check if line looks like a header (short, matches section keyword)
        if len(cleaned_line) < 45:
            for sec, pat in section_patterns.items():
                if re.search(pat, cleaned_line):
                    matched_section = sec
                    break

        if matched_section:
            current_section = matched_section
            if current_section not in sections:
                sections[current_section] = []
        else:
            sections[current_section].append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()}


def extract_projects(projects_text: str, full_text: str) -> List[Dict[str, Any]]:
    """Identifies individual projects, their technologies, and key implementation points."""
    target_text = projects_text if len(projects_text) > 100 else full_text
    projects = []

    # Look for project blocks separated by blank lines or bullet headers
    lines = [line.strip() for line in target_text.split("\n") if line.strip()]
    curr_proj = None

    for i, line in enumerate(lines):
        # Heuristic: line starts with a title like "Project Name - Tech Stack" or looks like a title
        is_title = False
        tech_in_line = []

        # Check for title patterns
        if " - " in line or " | " in line or ":" in line:
            parts = re.split(r' - | \| |:', line, maxsplit=1)
            candidate_title = parts[0].strip()
            if 1 <= len(candidate_title.split()) <= 7 and not candidate_title.lower().startswith(("http", "github", "key", "responsibilities", "tools", "technologies", "note")):
                is_title = True
        elif 1 <= len(line.split()) <= 6 and not line.startswith(("-", "•", "*", "–")) and not line.lower().startswith(("responsibilities", "key highlights", "overview", "technologies", "tools")):
            # Check next line has bullet points or starts with action verb
            if i + 1 < len(lines) and lines[i + 1].startswith(("-", "•", "*", "–", "Developed", "Built", "Engineered", "Implemented", "Designed", "Created")):
                is_title = True

        if is_title:
            if curr_proj:
                projects.append(curr_proj)
            curr_proj = {
                "title": line.split(" - ")[0].split(" | ")[0].split(":")[0].strip(),
                "full_title": line,
                "description": [],
                "technologies": []
            }
        elif curr_proj:
            curr_proj["description"].append(line)

    if curr_proj:
        projects.append(curr_proj)

    # Process each project to detect tools/technologies
    results = []
    for p in projects[:5]:  # Top 5 projects
        desc_text = " ".join(p["description"])
        full_proj_str = p["full_title"] + " " + desc_text
        detected = extract_skills_from_text(full_proj_str)["all_skills"]
        results.append({
            "name": p["title"],
            "title": p["title"],
            "description": " ".join(p["description"][:3]),
            "technologies": detected,
            "tech_summary": ", ".join(detected[:6]) if detected else "General Technical Stack"
        })

    # Fallback if no structured projects found
    if not results and projects_text:
        detected = extract_skills_from_text(projects_text)["all_skills"]
        results.append({
            "name": "Primary Technical Project",
            "title": "Primary Technical Project",
            "description": projects_text[:250].replace("\n", " "),
            "technologies": detected,
            "tech_summary": ", ".join(detected[:6]) if detected else "Extracted from Resume"
        })

    return results


def extract_experience(exp_text: str) -> List[Dict[str, Any]]:
    """Extracts work experience and internships."""
    if not exp_text or len(exp_text.strip()) < 30:
        return []

    lines = [line.strip() for line in exp_text.split("\n") if line.strip()]
    experiences = []
    curr_exp = None

    date_pattern = r'(?:\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\b\d{4})\s*(?:-|to|–)\s*(?:\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\b\d{4}|Present|Current)'

    for line in lines:
        has_date = bool(re.search(date_pattern, line, re.IGNORECASE))
        if has_date or (len(line.split()) <= 6 and ("intern" in line.lower() or "developer" in line.lower() or "engineer" in line.lower() or "associate" in line.lower())):
            if curr_exp:
                experiences.append(curr_exp)

            title = line
            company = "Organization"
            if " | " in line:
                parts = line.split(" | ", 1)
                title = parts[0].strip()
                company = parts[1].split("(")[0].strip()
            elif " at " in line.lower():
                parts = re.split(r'\s+at\s+', line, maxsplit=1, flags=re.IGNORECASE)
                title = parts[0].strip()
                company = parts[1].split("(")[0].strip()
            elif " - " in line:
                parts = line.split(" - ", 1)
                title = parts[0].strip()
                company = parts[1].split("(")[0].strip()

            curr_exp = {
                "role_header": line,
                "title": title,
                "company": company,
                "details": []
            }
        elif curr_exp:
            curr_exp["details"].append(line)

    if curr_exp:
        experiences.append(curr_exp)

    return experiences[:4]


def extract_education(edu_text: str) -> List[Dict[str, Any]]:
    """Extracts degree, college, and graduation info."""
    if not edu_text:
        return []

    lines = [line.strip() for line in edu_text.split("\n") if line.strip()]
    degrees = []

    degree_patterns = [
        r'\b(?:B\.?Tech|Bachelor of Technology|B\.?E\.?|B\.?S\.?|Bachelor of Science|BCA|M\.?Tech|Master of Technology|M\.?S\.?|Master of Science|MCA|MBA|Diploma)\b'
    ]

    for line in lines:
        for pat in degree_patterns:
            if re.search(pat, line, re.IGNORECASE):
                degrees.append({
                    "degree": line,
                    "field": "Computer Science / Engineering" if "computer" in line.lower() or "tech" in line.lower() else "Engineering / Sciences"
                })
                break

    if not degrees and lines:
        degrees.append({"degree": lines[0], "field": "Relevant Academic Degree"})

    return degrees


def infer_experience_level_and_role(
    skills_data: Dict[str, Any],
    exp_list: List[Dict[str, Any]],
    text: str
) -> Tuple[str, float, str]:
    """
    Infers experience_type (Fresher, Mid Level, Senior),
    years_of_experience (float), and target_role.
    """
    # 1. Experience Type & Years
    exp_count = len(exp_list)
    years = 0.0

    # Look for explicit years mentions (e.g. "3+ years of experience", "3 years building")
    yrs_match = re.search(r'(\d+(?:\.\d+)?)\+?\s*years?(?:\s+(?:of\s+)?(?:experience|working|building|developing|in))?', text, re.IGNORECASE)
    if yrs_match:
        try:
            years = float(yrs_match.group(1))
        except ValueError:
            years = float(exp_count)
    else:
        years = min(10.0, float(exp_count * 1.5))

    if years < 1.5:
        exp_type = "Fresher / Entry Level"
    elif years <= 4.0:
        exp_type = "Mid Level"
    else:
        exp_type = "Senior"

    # 2. Target Role Inference
    text_lower = text.lower()
    ai_skills = skills_data.get("ai_data_science", [])
    cyber_skills = skills_data.get("cybersecurity", [])
    web_skills = skills_data.get("frameworks", [])
    langs = [l.lower() for l in skills_data.get("languages", [])]

    if len(cyber_skills) >= 2 or "cybersecurity" in text_lower or "penetration testing" in text_lower or "soc analyst" in text_lower:
        target_role = "Cybersecurity Engineer / Analyst"
    elif len(ai_skills) >= 3 or "machine learning" in text_lower or "data science" in text_lower:
        target_role = "Machine Learning Engineer"
    elif any(k in text_lower for k in ["react", "next.js", "vue", "frontend", "angular"]):
        if any(b in text_lower for b in ["django", "node", "express", "fastapi", "spring", "asp.net", "laravel"]):
            target_role = "Full Stack Developer"
        else:
            target_role = "Frontend Developer"
    elif "spring" in text_lower or "java" in langs:
        target_role = "Java / Backend Developer"
    elif "c#" in langs or ".net" in text_lower or "asp.net" in text_lower:
        target_role = ".NET / Backend Developer"
    elif "php" in langs or "laravel" in text_lower:
        target_role = "PHP / Backend Developer"
    elif any(b in text_lower for b in ["django", "fastapi", "flask", "backend", "microservices"]):
        target_role = "Backend Developer"
    elif any(d in text_lower for d in ["docker", "kubernetes", "aws", "devops", "ci/cd"]):
        target_role = "DevOps Engineer"
    else:
        target_role = "Software Engineer"

    return exp_type, years, target_role


def parse_resume(file_input: Union[bytes, str], filename: str) -> Dict[str, Any]:
    """
    Complete Resume Analysis Pipeline:
    Extracts text -> Identifies entities (Skills, Projects, Experience, Education) ->
    Generates clean structured candidate profile.
    """
    safe_name = sanitize_filename(filename)
    if isinstance(file_input, str):
        raw_text = file_input
    else:
        raw_text = extract_text_from_file_bytes(file_input, safe_name)

    if not raw_text or len(raw_text.strip()) < 20:
        raise ValueError("Could not extract readable text from the uploaded resume file.")

    # 1. Contact Info
    cand_name, email, phone = extract_contact_info(raw_text)

    # 2. Section Segmentation
    sections = extract_sections(raw_text)

    # 3. Technical Skills Extraction
    skills_data = extract_skills_from_text(raw_text)

    # 4. Projects Extraction
    projects_text = sections.get("projects", "")
    projects = extract_projects(projects_text, raw_text)

    # 5. Experience / Internships
    exp_text = sections.get("experience", "")
    experiences = extract_experience(exp_text)

    # 6. Education
    edu_text = sections.get("education", "")
    education = extract_education(edu_text)

    # 7. Inferred Profile Attributes
    exp_type, years_exp, target_role = infer_experience_level_and_role(skills_data, experiences, raw_text)

    # 8. Profile Summary
    skills_preview = ", ".join(skills_data["all_skills"][:8]) if skills_data["all_skills"] else "Software Engineering"
    proj_preview = projects[0]["title"] if projects else "Core Technical Systems"
    summary = (
        f"{exp_type} with focus on {target_role}. Technical profile highlights proficiency in {skills_preview}, "
        f"with practical implementation demonstrated in projects like '{proj_preview}'."
    )

    tech_skills = skills_data.get("all_skills", [])

    return {
        "filename": safe_name,
        "candidate_name": cand_name,
        "email": email,
        "phone": phone,
        "target_role": target_role,
        "experience_type": exp_type,
        "experience_level": exp_type,
        "years_of_experience": years_exp,
        "skills": tech_skills,
        "skills_text": ", ".join(tech_skills),
        "programming_languages": ", ".join(skills_data["languages"]),
        "frameworks": ", ".join(skills_data["frameworks"]),
        "databases": ", ".join(skills_data["databases"]),
        "cloud_devops": ", ".join(skills_data["cloud_devops"]),
        "ai_data_science": ", ".join(skills_data["ai_data_science"]),
        "cybersecurity": ", ".join(skills_data["cybersecurity"]),
        "categorized_skills": skills_data["categorized"],
        "all_skills_list": skills_data["all_skills"],
        "all_skills_text": ", ".join(skills_data["all_skills"]),
        "projects": projects,
        "projects_summary": "; ".join(f"{p['title']} ({p['tech_summary']})" for p in projects[:3]),
        "experiences": experiences,
        "education": education,
        "education_summary": education[0]["degree"] if education else "Technical Degree",
        "profile_summary": summary,
        "raw_text": raw_text,
        "char_count": len(raw_text),
        "word_count": len(raw_text.split())
    }
