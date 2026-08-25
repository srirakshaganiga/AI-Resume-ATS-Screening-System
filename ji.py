from flask import Flask, render_template, request
from PyPDF2 import PdfReader
from ats_engine import analyze_resume
from database import save_candidate, get_all_candidates
from flask_mail import Mail, Message
import os


app = Flask(__name__)


# ============================================================
# EMAIL CONFIGURATION
# ============================================================

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True

app.config["MAIL_USERNAME"] = "YOUR_EMAIL@gmail.com"
app.config["MAIL_PASSWORD"] = "YOUR_APP_PASSWORD"

mail = Mail(app)


# ============================================================
# UPLOAD FOLDER
# ============================================================

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template("index.html")


# ============================================================
# SEND RESULT EMAIL
# ============================================================

def send_result_email(
    name,
    email,
    ats_score,
    status
):

    subject = "ATS Resume Screening Result"

    if status == "SHORTLISTED":

        message_body = f"""
Hello {name},

Your resume has been analyzed by our AI-Based ATS Recruitment System.

ATS Score: {ats_score}%

Status: SHORTLISTED

Congratulations!

Your resume has passed the initial ATS screening.

Regards,
AI ATS Recruitment System
"""

    else:

        message_body = f"""
Hello {name},

Your resume has been analyzed by our AI-Based ATS Recruitment System.

ATS Score: {ats_score}%

Status: REJECTED

Unfortunately, your resume did not meet the required ATS score
for this job position.

You may improve your resume by adding relevant skills and
qualifications mentioned in the job description.

Regards,
AI ATS Recruitment System
"""

    message = Message(
        subject=subject,
        sender=app.config["MAIL_USERNAME"],
        recipients=[email]
    )

    message.body = message_body

    mail.send(message)


# ============================================================
# RESUME SCREENING
# ============================================================

@app.route(
    "/screen",
    methods=["POST"]
)
def screen_resume():

    # --------------------------------------------------------
    # GET FORM DATA
    # --------------------------------------------------------

    name = request.form.get("name")

    email = request.form.get("email")

    job_description = request.form.get(
        "job_description"
    )

    resume = request.files.get("resume")


    # --------------------------------------------------------
    # VALIDATE NAME
    # --------------------------------------------------------

    if not name:

        return """
        <h2>Candidate name is required.</h2>
        <a href="/">Go Back</a>
        """


    # --------------------------------------------------------
    # VALIDATE EMAIL
    # --------------------------------------------------------

    if not email:

        return """
        <h2>Candidate email is required.</h2>
        <a href="/">Go Back</a>
        """


    # --------------------------------------------------------
    # VALIDATE JOB DESCRIPTION
    # --------------------------------------------------------

    if not job_description:

        return """
        <h2>Job description is required.</h2>
        <a href="/">Go Back</a>
        """


    # --------------------------------------------------------
    # VALIDATE RESUME
    # --------------------------------------------------------

    if not resume:

        return """
        <h2>Please upload a resume.</h2>
        <a href="/">Go Back</a>
        """


    # --------------------------------------------------------
    # CHECK FILE NAME
    # --------------------------------------------------------

    if resume.filename == "":

        return """
        <h2>Please select a resume.</h2>
        <a href="/">Go Back</a>
        """


    # --------------------------------------------------------
    # CHECK PDF
    # --------------------------------------------------------

    if not resume.filename.lower().endswith(".pdf"):

        return """
        <h2>Only PDF resumes are allowed.</h2>
        <a href="/">Go Back</a>
        """


    # ========================================================
    # CREATE UPLOAD FOLDER
    # ========================================================

    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )


    # ========================================================
    # SAVE RESUME
    # ========================================================

    resume_path = os.path.join(
        UPLOAD_FOLDER,
        resume.filename
    )

    resume.save(resume_path)


    # ========================================================
    # EXTRACT PDF TEXT
    # ========================================================

    try:

        reader = PdfReader(
            resume_path
        )

        resume_text = ""

        for page in reader.pages:

            text = page.extract_text()

            if text:

                resume_text += (
                    text + "\n"
                )


    except Exception as error:

        return f"""
        <h2>Error reading PDF</h2>

        <p>{error}</p>

        <a href="/">Go Back</a>
        """


    # ========================================================
    # CHECK EXTRACTED TEXT
    # ========================================================

    if not resume_text.strip():

        return """
        <h2>
        Could not extract text from this PDF.
        </h2>

        <p>
        Please upload a text-based PDF resume.
        </p>

        <a href="/">Go Back</a>
        """


    # ========================================================
    # ATS ANALYSIS
    # ========================================================

    try:

        result = analyze_resume(
            resume_text,
            job_description
        )

    except Exception as error:

        return f"""
        <h2>ATS Analysis Error</h2>

        <p>{error}</p>

        <a href="/">Go Back</a>
        """


    # ========================================================
    # GET ATS SCORES
    # ========================================================

    ats_score = result[
        "ats_score"
    ]

    similarity_score = result[
        "similarity_score"
    ]

    skill_score = result[
        "skill_score"
    ]

    qualification_score = result[
        "qualification_score"
    ]


    # ========================================================
    # GET SKILLS
    # ========================================================

    matched_skills = result[
        "matched_skills"
    ]

    missing_skills = result[
        "missing_skills"
    ]


    # ========================================================
    # SHORTLIST / REJECT
    # ========================================================

    if ats_score >= 70:

        status = "SHORTLISTED"

    else:

        status = "REJECTED"


    # ========================================================
    # SAVE CANDIDATE TO MYSQL
    # ========================================================

    database_message = ""

    try:

        save_candidate(
            name,
            email,
            resume.filename,
            ats_score,
            matched_skills,
            missing_skills,
            qualification_score,
            status
        )

        database_message = (
            "Candidate saved to MySQL successfully."
        )

        print(
            database_message
        )

    except Exception as error:

        database_message = (
            "Database Error: "
            + str(error)
        )

        print(
            database_message
        )


    # ========================================================
    # SEND RESULT EMAIL
    # ========================================================

    email_message = ""

    try:

        send_result_email(
            name,
            email,
            ats_score,
            status
        )

        email_message = (
            "Email notification sent successfully."
        )

        print(
            email_message
        )

    except Exception as error:

        email_message = (
            "Email Error: "
            + str(error)
        )

        print(
            email_message
        )


    # ========================================================
    # TERMINAL OUTPUT
    # ========================================================

    print()
    print(
        "================================="
    )

    print(
        "       ATS SCREENING RESULT"
    )

    print(
        "================================="
    )

    print(
        "Candidate:",
        name
    )

    print(
        "Email:",
        email
    )

    print(
        "ATS Score:",
        ats_score,
        "%"
    )

    print(
        "NLP Similarity:",
        similarity_score,
        "%"
    )

    print(
        "Skill Score:",
        skill_score,
        "%"
    )

    print(
        "Qualification Score:",
        qualification_score,
        "%"
    )

    print(
        "Matched Skills:",
        matched_skills
    )

    print(
        "Missing Skills:",
        missing_skills
    )

    print(
        "Status:",
        status
    )

    print(
        "================================="
    )


    # ========================================================
    # CREATE MATCHED SKILLS HTML
    # ========================================================

    matched_html = ""

    if matched_skills:

        for skill in matched_skills:

            matched_html += (
                f"<li>{skill}</li>"
            )

    else:

        matched_html = (
            "<li>No matching skills found.</li>"
        )


    # ========================================================
    # CREATE MISSING SKILLS HTML
    # ========================================================

    missing_html = ""

    if missing_skills:

        for skill in missing_skills:

            missing_html += (
                f"<li>{skill}</li>"
            )

    else:

        missing_html = (
            "<li>No major missing skills.</li>"
        )


    # ========================================================
    # RESULT PAGE
    # ========================================================

    return f"""
    <!DOCTYPE html>

    <html lang="en">

    <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width,
              initial-scale=1.0">

        <title>
            ATS Screening Result
        </title>


        <style>

            body {{

                font-family: Arial, sans-serif;

                background: #f4f6f8;

                margin: 0;

                padding: 40px;

            }}


            .result {{

                max-width: 750px;

                margin: auto;

                background: white;

                padding: 35px;

                border-radius: 12px;

                box-shadow:
                0 4px 15px
                rgba(0,0,0,0.1);

            }}


            h1 {{

                text-align: center;

            }}


            .score {{

                font-size: 55px;

                font-weight: bold;

                text-align: center;

                margin: 30px;

            }}


            .status {{

                text-align: center;

                font-size: 28px;

                font-weight: bold;

                margin: 20px;

            }}


            .section {{

                margin-top: 25px;

                padding: 15px;

                border: 1px solid #ddd;

                border-radius: 8px;

            }}


            li {{

                margin: 8px 0;

            }}


            .database {{

                margin-top: 20px;

                padding: 12px;

                background: #f1f1f1;

                border-radius: 6px;

            }}


            .email {{

                margin-top: 10px;

                padding: 12px;

                background: #f1f1f1;

                border-radius: 6px;

            }}


            a {{

                display: inline-block;

                margin-top: 25px;

                text-decoration: none;

            }}

        </style>

    </head>


    <body>


        <div class="result">


            <h1>
                AI ATS Screening Result
            </h1>


            <h2>
                Candidate: {name}
            </h2>


            <p>
                <strong>Email:</strong>
                {email}
            </p>


            <div class="score">

                {ats_score}%

            </div>


            <div class="status">

                Status:
                {status}

            </div>


            <div class="section">

                <h3>
                    NLP Similarity Score
                </h3>

                <p>
                    {similarity_score}%
                </p>

            </div>


            <div class="section">

                <h3>
                    Skill Match Score
                </h3>

                <p>
                    {skill_score}%
                </p>

            </div>


            <div class="section">

                <h3>
                    Qualification Score
                </h3>

                <p>
                    {qualification_score}%
                </p>

            </div>


            <div class="section">

                <h3>
                    Matched Skills
                </h3>

                <ul>

                    {matched_html}

                </ul>

            </div>


            <div class="section">

                <h3>
                    Missing Skills
                </h3>

                <ul>

                    {missing_html}

                </ul>

            </div>


            <div class="database">

                <strong>
                    Database:
                </strong>

                {database_message}

            </div>


            <div class="email">

                <strong>
                    Email:
                </strong>

                {email_message}

            </div>


            <a href="/">
                ← Analyze Another Resume
            </a>


            <br>


            <a href="/dashboard">
                📊 Open ATS Dashboard
            </a>


        </div>


    </body>

    </html>
    """


# ============================================================
# ADMIN DASHBOARD
# STEP 9
# ============================================================

@app.route("/dashboard")
def dashboard():

    try:

        candidates = get_all_candidates()

    except Exception as error:

        return f"""
        <h2>Dashboard Database Error</h2>

        <p>{error}</p>

        <a href="/">Go Back</a>
        """


    # ========================================================
    # STATISTICS
    # ========================================================

    total_candidates = len(
        candidates
    )

    shortlisted = 0

    rejected = 0

    total_score = 0


    # ========================================================
    # CALCULATE STATISTICS
    # ========================================================

    for candidate in candidates:

        # Expected database order:
        #
        # 0 = ID
        # 1 = Name
        # 2 = Email
        # 3 = ATS Score
        # 4 = Matched Skills
        # 5 = Missing Skills
        # 6 = Qualification Score
        # 7 = Status

        try:

            ats_score = float(
                candidate[3]
            )

        except:

            ats_score = 0


        status = str(
            candidate[7]
        ).upper()


        if status == "SHORTLISTED":

            shortlisted += 1


        elif status == "REJECTED":

            rejected += 1


        total_score += ats_score


    # ========================================================
    # AVERAGE ATS SCORE
    # ========================================================

    if total_candidates > 0:

        average_score = round(
            total_score / total_candidates,
            2
        )

    else:

        average_score = 0


    # ========================================================
    # DASHBOARD
    # ========================================================

    return render_template(
        "dashboard.html",

        candidates=candidates,

        total_candidates=
        total_candidates,

        shortlisted=
        shortlisted,

        rejected=
        rejected,

        average_score=
        average_score
    )


# ============================================================
# START FLASK
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )