
from flask import Flask
import sqlite3
from routes.auth import auth_bp

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-later"


def init_db():
    conn = sqlite3.connect("complaints.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


app.register_blueprint(auth_bp)


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
