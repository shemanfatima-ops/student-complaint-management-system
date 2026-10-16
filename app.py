
from flask import Flask
import sqlite3
import os

from routes.auth import auth_bp
from routes.complaints import complaints_bp
from routes.admin import admin_bp

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-later"


def init_db():
    # Student users database
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

    # Complaints database
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect("database/database.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            department TEXT DEFAULT 'Unassigned',
            created_at TEXT,
            admin_response TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()


app.register_blueprint(auth_bp)
app.register_blueprint(complaints_bp)
app.register_blueprint(admin_bp)


@app.route("/")
def home():
    return """
        <h1>Student Complaint Management System</h1>
        <a href="/register">Register</a><br>
        <a href="/login">Login</a><br>
        <a href="/admin-login">Admin Login</a>
    """


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

