import pytest

from app import app as flask_app
from models.database import init_db


@pytest.fixture
def app(tmp_path):
    flask_app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        DATABASE=str(tmp_path / "test_complaints.db"),
    )

    with flask_app.app_context():
        init_db()

    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def student_account():
    return {
        "name": "Test Student",
        "email": "student@example.test",
        "password": "test-password",
    }


@pytest.fixture
def authenticated_client(client, student_account):
    client.post("/register", data=student_account)
    response = client.post(
        "/login",
        data={
            "email": student_account["email"],
            "password": student_account["password"],
        },
    )
    assert response.status_code == 302
    return client
