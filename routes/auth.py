from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

auth_bp = Blueprint("auth", __name__)

def get_db_connection():
    conn = sqlite3.connect("complaints.db")
    conn.row_factory = sqlite3.Row
    return conn


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please fill in all fields.", "error")
            return redirect(url_for("auth.register"))

        conn = get_db_connection()

        try:
            conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password))
            )
            conn.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("auth.login"))
        except sqlite3.IntegrityError:
            flash("This email is already registered.", "error")
        finally:
            conn.close()

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db_connection()
        try:
            user = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()
        finally:
            conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for("auth.profile"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@auth_bp.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    return render_template(
        "profile.html",
        name=session["user_name"]
    )


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))