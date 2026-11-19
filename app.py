
from flask import Flask
import os
from models.database import init_db as initialize_database
from routes.auth import auth_bp
from routes.complaints import complaints_bp

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-later"
app.config["DATABASE"] = os.path.join(os.path.dirname(__file__), "complaints.db")


def init_db():
    with app.app_context():
        initialize_database()


app.register_blueprint(auth_bp)
app.register_blueprint(complaints_bp)


@app.route("/")
def home():
    return """
        <h1>Student Complaint Management System</h1>
        <a href="/register">Register</a><br>
        <a href="/login">Login</a>
    """


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
