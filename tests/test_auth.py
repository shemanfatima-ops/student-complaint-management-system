def test_valid_registration_creates_student(client, student_account, app):
    response = client.post("/register", data=student_account)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
    with app.app_context():
        from models.database import get_db_connection

        conn = get_db_connection()
        try:
            student = conn.execute(
                "SELECT name, email, password_hash FROM users WHERE email = ?",
                (student_account["email"],),
            ).fetchone()
        finally:
            conn.close()
    assert student["name"] == student_account["name"]
    assert student["password_hash"] != student_account["password"]


def test_invalid_registration_rejects_empty_fields(client):
    response = client.post(
        "/register",
        data={"name": "", "email": "student@example.test", "password": ""},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Please fill in all fields." in response.data


def test_duplicate_email_is_rejected(client, student_account):
    client.post("/register", data=student_account)
    duplicate = dict(student_account, name="Another Student")

    response = client.post("/register", data=duplicate, follow_redirects=True)

    assert response.status_code == 200
    assert b"This email is already registered." in response.data


def test_valid_login_sets_session(client, student_account):
    client.post("/register", data=student_account)

    response = client.post(
        "/login",
        data={
            "email": student_account["email"].upper(),
            "password": student_account["password"],
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/profile")
    with client.session_transaction() as session:
        assert session["user_id"] == 1
        assert session["user_name"] == student_account["name"]


def test_incorrect_password_does_not_authenticate(client, student_account):
    client.post("/register", data=student_account)

    response = client.post(
        "/login",
        data={"email": student_account["email"], "password": "incorrect"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid email or password." in response.data
    with client.session_transaction() as session:
        assert "user_id" not in session


def test_logout_clears_session(authenticated_client):
    response = authenticated_client.get("/logout")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
    with authenticated_client.session_transaction() as session:
        assert not session


def test_profile_redirects_when_not_logged_in(client):
    response = client.get("/profile")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
