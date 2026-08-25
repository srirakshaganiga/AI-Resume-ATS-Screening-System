import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Skills that our ATS can identify
SKILLS = [
    "python",
    "java",
    "c",
    "c++",
    "javascript",
    "html",
    "css",
    "flask",
    "django",
    "react",
    "node.js",
    "mysql",
    "sql",
    "mongodb",
    "git",
    "github",
    "docker",
    "kubernetes",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "nlp",
    "data science",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "data structures",
    "algorithms",
    "dbms",
    "operating systems",
    "computer networks"
]


def clean_text(text):

    text = text.lower()

    text = re.sub(
        r"[^a-zA-Z0-9+#.\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def extract_skills(text):

    text = clean_text(text)

    found_skills = []

    for skill in SKILLS:

        if skill.lower() in text:

            found_skills.append(skill)

    return sorted(set(found_skills))


def calculate_similarity(
    resume_text,
    job_description
):

    resume_text = clean_text(
        resume_text
    )

    job_description = clean_text(
        job_description
    )

    documents = [
        resume_text,
        job_description
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    matrix = vectorizer.fit_transform(
        documents
    )

    similarity = cosine_similarity(
        matrix[0:1],
        matrix[1:2]
    )[0][0]

    return similarity * 100


def calculate_qualification_score(
    resume_text,
    job_description
):

    resume_text = clean_text(
        resume_text
    )

    job_description = clean_text(
        job_description
    )

    qualifications = [
        "bca",
        "b.sc",
        "btech",
        "b.e",
        "mca",
        "mtech",
        "bachelor",
        "master",
        "computer science",
        "information technology",
        "artificial intelligence"
    ]

    required_qualifications = []

    for qualification in qualifications:

        if qualification in job_description:

            required_qualifications.append(
                qualification
            )

    # If no qualification is mentioned
    # in the job description
    if not required_qualifications:

        return 100

    matched = 0

    for qualification in required_qualifications:

        if qualification in resume_text:

            matched += 1

    return (
        matched /
        len(required_qualifications)
    ) * 100


def analyze_resume(
    resume_text,
    job_description
):

    # Skills in resume
    resume_skills = extract_skills(
        resume_text
    )

    # Skills required by job
    required_skills = extract_skills(
        job_description
    )

    matched_skills = []

    missing_skills = []

    for skill in required_skills:

        if skill in resume_skills:

            matched_skills.append(
                skill
            )

        else:

            missing_skills.append(
                skill
            )

    # Skill matching score
    if len(required_skills) > 0:

        skill_score = (
            len(matched_skills)
            /
            len(required_skills)
        ) * 100

    else:

        skill_score = 0

    # NLP similarity score
    similarity_score = calculate_similarity(
        resume_text,
        job_description
    )

    # Qualification score
    qualification_score = (
        calculate_qualification_score(
            resume_text,
            job_description
        )
    )

    # Final ATS score
    #
    # NLP similarity = 30%
    # Skills          = 50%
    # Qualification  = 20%

    ats_score = (
        similarity_score * 0.30
        +
        skill_score * 0.50
        +
        qualification_score * 0.20
    )

    return {

        "ats_score": round(
            ats_score,
            2
        ),

        "similarity_score": round(
            similarity_score,
            2
        ),

        "skill_score": round(
            skill_score,
            2
        ),

        "qualification_score": round(
            qualification_score,
            2
        ),

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills
    }