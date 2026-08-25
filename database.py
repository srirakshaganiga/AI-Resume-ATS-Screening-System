import mysql.connector


def get_connection():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ats_resume_db"
    )


def save_candidate(
    name,
    email,
    resume_file,
    ats_score,
    matched_skills,
    missing_skills,
    qualification_score,
    status
):

    connection = get_connection()

    cursor = connection.cursor()

    query = """
        INSERT INTO candidates
        (
            name,
            email,
            resume_file,
            ats_score,
            matched_skills,
            missing_skills,
            qualification_score,
            status
        )
        VALUES
        (
            %s, %s, %s, %s,
            %s, %s, %s, %s
        )
    """

    values = (
        name,
        email,
        resume_file,
        ats_score,
        ", ".join(matched_skills),
        ", ".join(missing_skills),
        qualification_score,
        status
    )

    cursor.execute(
        query,
        values
    )

    connection.commit()

    cursor.close()

    connection.close()


# ==========================
# GET ALL CANDIDATES
# ==========================

def get_all_candidates():

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    query = """
        SELECT *
        FROM candidates
        ORDER BY ats_score DESC
    """

    cursor.execute(query)

    candidates = cursor.fetchall()

    cursor.close()

    connection.close()

    return candidates