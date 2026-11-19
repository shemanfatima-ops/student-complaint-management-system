from models.user import User


def test_user_password_is_hashed_and_verifiable():
    password = "student-password"
    user = User("Test Student", "student@example.test", User.hash_password(password))

    assert user.password_hash != password
    assert user.check_password(password)
    assert not user.check_password("incorrect")


def test_student_profile_displays_authenticated_student(authenticated_client, student_account):
    response = authenticated_client.get("/profile")

    assert response.status_code == 200
    assert f"Welcome, {student_account['name']}!".encode() in response.data
    assert b"You are successfully logged in." in response.data


def test_profile_contains_correct_student_information(authenticated_client, student_account):
    authenticated_client.get("/profile")
    with authenticated_client.session_transaction() as session:
        assert session["user_name"] == student_account["name"]
