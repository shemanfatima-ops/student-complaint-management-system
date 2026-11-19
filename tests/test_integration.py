import re

from models.database import get_db_connection


def test_student_registration_login_and_complaint_submission(client, app):
    student = {
        "name": "Integration Student",
        "email": "integration@example.test",
        "password": "integration-password",
    }

    registration = client.post("/register", data=student)
    assert registration.status_code == 302

    login = client.post(
        "/login",
        data={"email": student["email"], "password": student["password"]},
    )
    assert login.status_code == 302

    submission_page = client.get("/submit-complaint")
    assert submission_page.status_code == 200
    assert b"Submit Student Complaint" in submission_page.data

    submission = client.post(
        "/submit-complaint",
        data={"category": "IT", "description": "Unable to access the student portal"},
    )
    assert submission.status_code == 200
    match = re.search(
        rb"Unique Complaint ID is: <strong>(CMP-[A-F0-9]{8})</strong>", submission.data
    )
    assert match is not None
    complaint_id = match.group(1).decode()

    with app.app_context():
        conn = get_db_connection()
        try:
            complaint = conn.execute(
                """
                SELECT complaints.complaint_id, complaints.category,
                       complaints.description, users.email
                FROM complaints
                JOIN users ON users.id = complaints.user_id
                WHERE complaints.complaint_id = ?
                """,
                (complaint_id,),
            ).fetchone()
        finally:
            conn.close()

    assert complaint["complaint_id"] == complaint_id
    assert complaint["category"] == "IT"
    assert complaint["description"] == "Unable to access the student portal"
    assert complaint["email"] == student["email"]
