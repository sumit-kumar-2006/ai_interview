# AI INTERVIEW ANALYZER — 30 UNIVERSITY VIVA VOCE EXAMINATION QUESTIONS & ANSWERS
**Academic Evaluation Guide:** Final Year BCA Major Project Defense  
**Project:** AI Interview Analyzer  
**Examiner Role:** University Professor & External Project Reviewer  
**Date:** November 2026  

---

## SECTION 1: BASIC PROJECT & PROBLEM DEFINITION QUESTIONS (10 Questions)

### Q1. What is the fundamental objective of the AI Interview Analyzer, and what gap does it address?
- **Why the Examiner Asks It:** To evaluate whether the candidate understands the core motivation of their project beyond just writing code.
- **What a Correct Answer Should Contain:** Explain that traditional campus recruitment and technical interviews suffer from interviewer subjectivity, evaluator fatigue during high-volume screening, scheduling bottlenecks, and a lack of granular feedback. The system provides an automated, objective, multimodal simulation that scores answers across four rubric dimensions, tracks speech pacing/fillers, and measures visual attentiveness, generating immediate diagnostic reports.
- **Common Mistakes to Avoid:** Do not say "it replaces human interviewers completely." Instead, frame it as an intelligent preparatory coaching tool and first-round automated assessment aid.

### Q2. Why is your system described as "multimodal"? What modalities does it incorporate?
- **Why the Examiner Asks It:** To test whether the student understands technical terminology.
- **What a Correct Answer Should Contain:** State that the system processes three distinct modalities:
  1. *Text / NLP Modality:* Transcribed answer evaluated against expected reference answer using SentenceTransformers and Random Forest.
  2. *Audio / Speech Modality:* Spoken speech evaluated via Faster-Whisper for fluency, words per minute (Target: 110–160 WPM), and filler words.
  3. *Vision / Video Modality:* Webcam video stream evaluated via MediaPipe FaceMesh (478 3D landmarks) for eye gaze stability and head pose.
- **Common Mistakes to Avoid:** Never claim that the Random Forest model processes audio waveforms or video pixels. Explicitly emphasize that modalities are processed by specialized decoupled pipelines and aggregated at the application gateway.

### Q3. Explain the end-to-end user journey during an interview session.
- **Why the Examiner Asks It:** To verify the student knows the software workflow from a user's perspective.
- **What a Correct Answer Should Contain:** Candidate logs in -> selects Target Job Role & Experience Level (or uploads Resume for keyword extraction) -> undergoes Hardware Device Check (mic & camera) -> questions are generated from curated pool -> candidate records verbal answer while camera tracks facial posture -> Faster-Whisper transcribes speech -> AnswerEvaluator scores response -> immediate feedback is shown -> on interview completion, an interactive summary and downloadable PDF report are synthesized.
- **Common Mistakes to Avoid:** Skipping the hardware device check or failing to mention how questions are selected.

### Q4. How does your resume parser adapt interview questions to the candidate?
- **Why the Examiner Asks It:** To check whether resume upload is a static placeholder or actively influences application logic.
- **What a Correct Answer Should Contain:** Explain that `resume_parser.py` uses PyPDF to extract text from PDF resumes, tokenizes the content, filters against a technical skill taxonomy, and passes identified skills (e.g., Python, React, Docker) to `backend/app/questions.py` (`generate_personalized_questions`), matching questions from the active pool tagged with those specific skill tags.
- **Common Mistakes to Avoid:** Claiming the resume parser uses an external paid LLM API when it actually runs local regex and keyword extraction.

### Q5. What technology stack was selected for this project and what was the rationale?
- **Why the Examiner Asks It:** To verify architectural justification.
- **What a Correct Answer Should Contain:**
  - *Frontend:* Vanilla HTML5, CSS3, and ES6+ JavaScript (zero external bundling overhead, fast browser execution, responsive design).
  - *Backend:* FastAPI on Python 3.11 (native asynchronous support, high throughput, automated OpenAPI documentation, Pydantic type validation).
  - *Database:* Relational persistence via SQLAlchemy ORM (support for users, interviews, questions, and telemetry logs).
  - *AI/ML Libraries:* SentenceTransformers (`all-MiniLM-L6-v2`), Scikit-learn (Random Forest, KNN, SVM, Decision Tree, K-Means), Faster-Whisper (CTranslate2 INT8 quantization), and Google MediaPipe Face Mesh.
- **Common Mistakes to Avoid:** Saying "I chose FastAPI because it was easy" without citing performance, async capabilities, or Pydantic validation.

### Q6. How are non-answers (silence or "I don't know") handled by the system?
- **Why the Examiner Asks It:** To check if the system can be fooled by candidates submitting empty recordings to get default passing scores.
- **What a Correct Answer Should Contain:** Rule E and the Zero-Floor Non-Answer Guard in `backend/app/evaluator.py`: If audio is silent (`speech_detected == False`), word count is $<3$, or text contains explicit evasions ("I don't know", "no idea"), the system clamps the score to exactly $0.0$, prevents scoring hallucination, and provides a polite prompt requesting an answer.
- **Common Mistakes to Avoid:** Claiming the Random Forest naturally gives 0 to empty answers without mentioning the deterministic zero-floor filter.

### Q7. What are the four core technical rubric dimensions evaluated by your system?
- **Why the Examiner Asks It:** To test familiarity with the scoring rubric.
- **What a Correct Answer Should Contain:**
  1. *Concept Coverage (30%):* Fraction of mandatory domain entities articulated.
  2. *Technical Depth (25%):* Presence of specialized nomenclature and technical terminology.
  3. *Semantic Similarity (25%):* Dense embedding cosine alignment between candidate and reference text.
  4. *Keyword Alignment (20%):* Lexical domain keyword match relative to the question prompt.
- **Common Mistakes to Avoid:** Confusing these four text rubrics with speech fluency or eye contact metrics.

### Q8. What security mechanisms protect reference answers and student data?
- **Why the Examiner Asks It:** To assess cybersecurity awareness in web applications.
- **What a Correct Answer Should Contain:**
  1. *Reference Answer Isolation:* The `/api/interview/questions` endpoint strictly serializes through `QuestionPublic`, omitting `reference_answer` and `evaluation_spec` so candidates cannot view answers via browser inspect.
  2. *Credential Protection:* Passwords hashed using Argon2 (`pwd_context.hash`).
  3. *Session Authentication:* Signed JSON Web Tokens (JWT) with expiration.
  4. *Upload Sanitization:* Audio endpoints enforce MIME validation, magic byte checks, and 25MB file size ceilings with guaranteed temporary file cleanup.
- **Common Mistakes to Avoid:** Claiming plain MD5 or SHA256 was used for password hashing.

### Q9. What role does the administrator dashboard play in the system?
- **Why the Examiner Asks It:** To confirm whether multi-role governance was implemented.
- **What a Correct Answer Should Contain:** The admin interface (`/admin`) allows authorized staff to inspect platform-wide interview metrics, audit candidate test scores, quarantine low-quality questions, and manage the active question pool (`is_active = 0/1`).
- **Common Mistakes to Avoid:** Confusing the candidate dashboard (personal history) with the administrative dashboard (platform governance).

### Q10. What are the key limitations of your current implementation?
- **Why the Examiner Asks It:** To test intellectual honesty and mature self-assessment.
- **What a Correct Answer Should Contain:**
  1. No live algorithmic code execution sandbox (compiler/debugger).
  2. The Random Forest model emulates continuous rubric formulas rather than human examiner grades.
  3. MediaPipe tracking runs on the client browser and can be sensitive to poor ambient lighting or webcam angles.
  4. Audio transcription currently defaults to English language interviews.
- **Common Mistakes to Avoid:** Saying "there are no limitations, the project is completely perfect."

---

## SECTION 2: MACHINE LEARNING & MATHEMATICAL QUESTIONS (10 Questions)

### Q11. Explain how SentenceTransformer (`all-MiniLM-L6-v2`) computes semantic similarity mathematically.
- **Why the Examiner Asks It:** To verify foundational NLP mathematical understanding.
- **What a Correct Answer Should Contain:** The model uses a 6-layer MiniLM Transformer architecture with mean pooling to project text into a dense 384-dimensional continuous vector space $\mathbb{R}^{384}$. The similarity between question vector $\mathbf{u}$ and answer vector $\mathbf{v}$ is the Cosine Similarity:
  $$\cos(\theta) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2} = \frac{\sum_{i=1}^{384} u_i v_i}{\sqrt{\sum_{i=1}^{384} u_i^2} \sqrt{\sum_{i=1}^{384} v_i^2}}$$
- **Common Mistakes to Avoid:** Saying it counts shared words. Cosine similarity evaluates directional alignment in high-dimensional embedding space, capturing synonyms and paraphrases.

### Q12. Why did your training dataset contain a negative cosine similarity (-0.0043)? Can cosine similarity be negative?
- **Why the Examiner Asks It:** A classic mathematical trap question based on our dataset findings.
- **What a Correct Answer Should Contain:** Yes, mathematically cosine similarity ranges between $-1.0$ and $+1.0$. Unconstrained sentence embeddings that point in slightly obtuse angles ($>90^\circ$) yield negative values. In our dataset, completely unrelated or contradictory answers produced $-0.0043$. In production, this raw score is clipped via $\max(0.0, \min(1.0, \text{sim}))$.
- **Common Mistakes to Avoid:** Panicking and claiming cosine similarity is strictly bounded between $0$ and $1$. It is only $[0, 1]$ if non-negative features (like TF-IDF) are used, NOT dense neural embeddings.

### Q13. What is "Target Leakage," and how did it manifest in your academic classification experiments?
- **Why the Examiner Asks It:** To test rigorous understanding of machine learning data integrity.
- **What a Correct Answer Should Contain:** Target leakage occurs when input features contain direct mathematical information about the target variable that would not be available in real-world inference. In Experiment A, `target_label` was constructed as `(semantic_similarity >= 0.70) & (word_count >= 20)`. When both were included as input features, the Decision Tree achieved 100% accuracy because it literally isolated this axis-aligned rectangle.
- **Common Mistakes to Avoid:** Denying leakage or trying to claim the Decision Tree achieved 100% due to "superior AI optimization."

### Q14. How did you resolve the target leakage in Experiment B, and what were the ablated results?
- **Why the Examiner Asks It:** To evaluate how the student handled experimental flaws.
- **What a Correct Answer Should Contain:** In Experiment B, `semantic_similarity` and `word_count` were completely removed from the feature set. The models were retrained strictly on `lexical_overlap`, `unique_word_ratio`, and `avg_word_length`. The Decision Tree achieved a realistic **Macro F1 of 0.6959**, **ROC-AUC of 0.7330**, and **PR-AUC of 0.4420**, demonstrating that vocabulary richness and technical word length carry genuine predictive signal.
- **Common Mistakes to Avoid:** Forgetting the ablated metric values or confusing Experiment A with Experiment B.

### Q15. Explain the architecture and hyperparameter choices of your Random Forest Regressor.
- **Why the Examiner Asks It:** To verify model configuration knowledge.
- **What a Correct Answer Should Contain:** Implemented using `sklearn.ensemble.RandomForestRegressor` with:
  - $350$ Decision Trees (`n_estimators = 350`) for variance reduction and ensemble stability.
  - Maximum tree depth of $10$ (`max_depth = 10`) to prevent leaf over-specialization.
  - $6$ input features: `semantic_similarity`, `question_length`, `answer_length`, `concept_coverage`, `keyword_alignment`, `technical_depth`.
  - Random seed $42$ for strict reproducibility.
- **Common Mistakes to Avoid:** Saying "I used default settings."

### Q16. What is the mathematical interpretation of your Random Forest Regressor's high R² (0.9985)?
- **Why the Examiner Asks It:** To see if the candidate realizes the model is a formula approximator.
- **What a Correct Answer Should Contain:** State honestly that the model was trained on 2,651 records where the target score was computed via a continuous multi-rubric formula. An $R^2$ of $0.9985$ means the 350 trees successfully learned to approximate this non-linear mathematical function with high fidelity (MAE = 0.4798 points), proving its capacity as an automated rubric-evaluation engine.
- **Common Mistakes to Avoid:** Claiming the model achieved 99.85% agreement with subjective human interviewers.

### Q17. How does K-Means clustering work, and how did you select k = 3?
- **Why the Examiner Asks It:** To test unsupervised learning knowledge.
- **What a Correct Answer Should Contain:** K-Means minimizes Within-Cluster Sum of Squares (Inertia):
  $$J = \sum_{j=1}^{k} \sum_{\mathbf{x}_i \in S_j} \|\mathbf{x}_i - \boldsymbol{\mu}_j\|^2$$
  Evaluated $k \in [2, 10]$ on standardized features. Selected $k=3$ because it represents the global peak of the **Silhouette Coefficient (0.2311)** and corresponds to the inflection point on the Elbow curve.
- **Common Mistakes to Avoid:** Saying $k=3$ was chosen randomly without referencing the silhouette peak or inertia elbow.

### Q18. What do the three discovered clusters represent behaviorally?
- **Why the Examiner Asks It:** To see if unsupervised clustering produced interpretable domain insights.
- **What a Correct Answer Should Contain:**
  - *Cluster 0 (Substantive / Extended, 25.6%):* High word count (~20 words), high lexical overlap, high semantic similarity (0.718).
  - *Cluster 1 (Low Alignment / Divergent, 25.7%):* Lowest similarity (0.448), lowest overlap, 0% Class 1 candidates (weak/off-topic answers).
  - *Cluster 2 (Concise Technical, 48.7%):* High similarity (0.717), highest unique word ratio (0.970), longest technical words (mean length 6.83 chars).
- **Common Mistakes to Avoid:** Inverting the cluster labels or reporting inaccurate centroid values.

### Q19. Why was Principal Component Analysis (PCA) used in your clustering chapter?
- **Why the Examiner Asks It:** To verify understanding of dimensionality reduction vs. clustering.
- **What a Correct Answer Should Contain:** Clustering was executed on all $5$ standardized dimensions. PCA was used strictly as a **2D visualization projection technique**, capturing **$65.91\%$** of total variance (PC1: $39.08\%$, PC2: $26.83\%$) so high-dimensional clusters could be plotted on a 2D plane.
- **Common Mistakes to Avoid:** Claiming K-Means was trained on the 2 PCA components. It was trained on the full 5-dimensional feature space.

### Q20. What is Variance Inflation Factor (VIF), and what did your VIF analysis demonstrate?
- **Why the Examiner Asks It:** To test knowledge of multicollinearity diagnosis.
- **What a Correct Answer Should Contain:** VIF measures how much the variance of an estimated regression coefficient increases due to collinearity among predictors:
  $$\text{VIF}_i = \frac{1}{1 - R_i^2}$$
  All extracted features demonstrated $\text{VIF} < 2.5$ (well below the threshold of $5.0$), confirming absence of severe multicollinearity.
- **Common Mistakes to Avoid:** Confusing VIF with variance of target labels.

---

## SECTION 3: DATASET & MODEL EVALUATION QUESTIONS (5 Questions)

### Q21. Explain how 3,193 raw records become 2,651 production training records.
- **Why the Examiner Asks It:** To verify exact accounting of dataset splits.
- **What a Correct Answer Should Contain:**
  - Academic QA Corpus: 1,806 records (1,264 Train, 270 Val, 272 Test).
  - Conversational QA Corpus: 1,227 records.
  - Hard Negatives: 160 records.
  - Total Multi-Source Corpus: $1,806 + 1,227 + 160 = 3,193$.
  - To prevent data leakage, the 270 validation and 272 test records were held out: $3,193 - 542 = 2,651$ records used for training ($1,264 + 1,227 + 160$).
- **Common Mistakes to Avoid:** Claiming 542 records were deleted or lost due to errors.

### Q22. Why did you include 160 "Hard Negatives" in your training data?
- **Why the Examiner Asks It:** To test understanding of adversarial robustness.
- **What a Correct Answer Should Contain:** Real users may test the system by submitting gibberish, evasions ("I don't know"), or completely irrelevant text. Hard negatives train the model and rubric heuristics to enforce zero-floor penalties, preventing over-generous scores on meaningless answers.
- **Common Mistakes to Avoid:** Saying hard negatives were included to balance classes.

### Q23. Why is Accuracy an inappropriate metric for your academic classification dataset?
- **Why the Examiner Asks It:** To test knowledge of class-imbalanced evaluation.
- **What a Correct Answer Should Contain:** The dataset has an imbalance of ~5.45:1 (84.5% Class 0 vs. 15.5% Class 1). A naive Dummy classifier that predicts "Class 0" for every record achieves 84.93% accuracy while having a Recall of 0.0%. Therefore, **Precision, Recall, Macro F1, and PR-AUC** are the required metrics.
- **Common Mistakes to Avoid:** Claiming 84.9% accuracy means a model is performing well.

### Q24. How did you prevent Data Snooping when scaling features with `StandardScaler`?
- **Why the Examiner Asks It:** To test methodological rigor in data preprocessing.
- **What a Correct Answer Should Contain:** The `StandardScaler` was fitted **strictly on the 1,264 training records** (`academic_scaler.pkl`). The mean and standard deviation parameters from training were then used to transform validation and test records without recomputing parameters, ensuring zero test data leakage.
- **Common Mistakes to Avoid:** Fitting the scaler on the entire dataset before splitting.

### Q25. What is the difference between ROC-AUC and PR-AUC on imbalanced datasets?
- **Why the Examiner Asks It:** To test theoretical metric depth.
- **What a Correct Answer Should Contain:** ROC-AUC plots True Positive Rate vs. False Positive Rate. When the negative class is very large, False Positive Rate remains small even with numerous false positives, creating an overly optimistic curve. Precision-Recall curves plot Precision vs. Recall, focusing directly on the minority positive class, providing an honest measure of precision.
- **Common Mistakes to Avoid:** Stating that ROC-AUC is always superior to PR-AUC.

---

## SECTION 4: ARCHITECTURE, BACKEND & IMPLEMENTATION QUESTIONS (5 Questions)

### Q26. How does Faster-Whisper achieve high-performance transcription on standard CPU hardware?
- **Why the Examiner Asks It:** To test understanding of speech model inference optimization.
- **What a Correct Answer Should Contain:** Faster-Whisper is a reimplementation of OpenAI's Whisper using **CTranslate2**, a fast inference engine for Transformer models. It uses **INT8 quantization**, reducing memory bandwidth and model size by 4x, and executes optimized C++ matrix kernels, enabling near real-time speech transcription on standard CPUs.
- **Common Mistakes to Avoid:** Saying it calls an external cloud API. It runs locally and privately inside the virtual environment.

### Q27. Explain the architecture of your Computer Vision subsystem. Does the backend process video frames?
- **Why the Examiner Asks It:** Critical technical check regarding live system operation.
- **What a Correct Answer Should Contain:** Clarify that MediaPipe FaceMesh runs **in the client web browser via CDN JavaScript and WebAssembly**. The client samples webcam frames, calculates gaze alignment and head pose, aggregates them into summary counts (`face_detected_samples`, `looking_at_camera_samples`), and transmits this telemetry to the backend. This edge-client design minimizes server load and eliminates webcam video streaming latency.
- **Common Mistakes to Avoid:** Claiming the backend ingests 30 FPS raw video over WebSockets when it actually ingests telemetry data.

### Q28. How does the backend distinguish between microphone failure and a candidate remaining silent?
- **Why the Examiner Asks It:** To test edge-case error handling.
- **What a Correct Answer Should Contain:** During Device Check, the client verifies audio input levels. During answer recording, `backend/app/audio_validator.py` checks file size, duration, and container headers. If audio contains valid background noise but no recognized speech segments, Whisper outputs `speech_detected: False`, which `AnswerEvaluator` flags as `no_answer`, avoiding treating technical hardware failure as a scored zero.
- **Common Mistakes to Avoid:** Conflating empty file uploads with silent speech recordings.

### Q29. How does the database schema ensure session integrity across questions?
- **Why the Examiner Asks It:** To test relational schema design knowledge.
- **What a Correct Answer Should Contain:** `User` has a 1-to-many relationship with `Interview`, which in turn has a 1-to-many relationship with `QuestionResult`. Each `QuestionResult` record stores the foreign key `interview_id`, the `question_number`, candidate transcript, scores, and JSON telemetry (`speech_analysis`, `visual_analysis`), ensuring all metrics are permanently tied to a specific candidate session.
- **Common Mistakes to Avoid:** Claiming interview data is stored only in browser local storage.

### Q30. Why does your backend implement both deterministic rubrics and machine learning models?
- **Why the Examiner Asks It:** The ultimate software architecture synthesis question.
- **What a Correct Answer Should Contain:** Explain that the platform employs a **Hybrid Assessment Architecture**:
  1. *Deterministic Rubric Rules (Rules A-H):* Guarantee strict technical boundary enforcement, instant detection of misconceptions, exact keyword matching, and legal fairness.
  2. *Machine Learning Models:* Provide continuous semantic similarity projection, unsupervised candidate style profiling (K-Means), and continuous score benchmarking (Random Forest).
  This combination achieves both deterministic reliability and artificial intelligence flexibility.
- **Common Mistakes to Avoid:** Arguing that pure ML is always better than rule-based systems or vice-versa. The strength is in the hybrid architecture.
