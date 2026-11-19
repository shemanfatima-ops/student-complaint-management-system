import re

from models.database import get_db_connection


def test_valid_complaint_submission_returns_generated_id(authenticated_client):
    response = authenticated_client.post(
        "/submit-complaint",
        data={"category": "Facilities", "description": "Broken classroom projector"},
    )

    assert response.status_code == 200
    match = re.search(rb"Unique Complaint ID is: <strong>(CMP-[A-F0-9]{8})</strong>", response.data)
    assert match is not None


def test_complaint_with_empty_fields_is_rejected(authenticated_client):
    response = authenticated_client.post(
        "/submit-complaint",
        data={"category": " ", "description": "   "},
    )

    assert response.status_code == 400
    assert b"All fields are required!" in response.data


def test_submitted_complaint_is_saved_with_logged_in_student(authenticated_client, app):
    response = authenticated_client.post(
        "/submit-complaint",
        data={"category": "Academics", "description": "Need help with course registration"},
    )
    complaint_id = re.search(
        rb"Unique Complaint ID is: <strong>(CMP-[A-F0-9]{8})</strong>", response.data
    ).group(1).decode()

    with authenticated_client.session_transaction() as session:
        student_id = session["user_id"]
    with app.app_context():
        conn = get_db_connection()
        try:
            complaint = conn.execute(
                """
                SELECT complaint_id, user_id, category, description, status
                FROM complaints WHERE complaint_id = ?
                """,
                (complaint_id,),
            ).fetchone()
        finally:
            conn.close()

    assert complaint["complaint_id"] == complaint_id
    assert complaint["user_id"] == student_id
    assert complaint["category"] == "Academics"
    assert complaint["description"] == "Need help with course registration"
    assert complaint["status"] == "Pending"


def test_complaint_submission_requires_login(client):
    response = client.get("/submit-complaint")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
