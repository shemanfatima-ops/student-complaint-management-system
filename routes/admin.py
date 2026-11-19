
import os
import sqlite3
from functools import wraps
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash, abort
)

admin_bp = Blueprint("admin", __name__)

# Demo credentials — deployment se pehle change karna.
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin@123"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPLAINT_DB = os.path.join(BASE_DIR, "database", "database.db")


def get_db():
    os.makedirs(os.path.dirname(COMPLAINT_DB), exist_ok=True)
    conn = sqlite3.connect(COMPLAINT_DB)
    conn.row_factory = sqlite3.Row

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

    columns = [
        row["name"]
        for row in conn.execute("PRAGMA table_info(complaints)")
    ]

    if "admin_response" not in columns:
        conn.execute(
            "ALTER TABLE complaints ADD COLUMN admin_response TEXT DEFAULT ''"
        )

    conn.commit()
    return conn


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin.admin_login"))
        return view(*args, **kwargs)
    return wrapped


@admin_bp.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session.clear()
            session["is_admin"] = True
            return redirect(url_for("admin.dashboard"))

        flash("Username ya password ghalat hai.", "error")

    return render_template("admin_login.html")


@admin_bp.route("/admin-logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin.admin_login"))


@admin_bp.route("/admin")
@admin_required
def dashboard():
    conn = get_db()
    try:
        counts = {}
        for status in ["Pending", "In Progress", "Resolved", "Rejected"]:
            counts[status] = conn.execute(
                "SELECT COUNT(*) FROM complaints WHERE status = ?",
                (status,)
            ).fetchone()[0]

        total = conn.execute(
            "SELECT COUNT(*) FROM complaints"
        ).fetchone()[0]
    finally:
        conn.close()

    return render_template(
        "admin_dashboard.html",
        total=total,
        pending=counts["Pending"],
        in_progress=counts["In Progress"],
        resolved=counts["Resolved"],
        rejected=counts["Rejected"]
    )


@admin_bp.route("/admin/complaints")
@admin_required
def manage_complaints():
    conn = get_db()
    try:
        complaints = conn.execute(
            "SELECT * FROM complaints ORDER BY created_at DESC, id DESC"
        ).fetchall()
    finally:
        conn.close()

    return render_template(
        "manage_complaints.html",
        complaints=complaints
    )


@admin_bp.route("/admin/complaints/<complaint_id>", methods=["GET", "POST"])
@admin_required
def complaint_details(complaint_id):
    conn = get_db()
    try:
        complaint = conn.execute(
            "SELECT * FROM complaints WHERE complaint_id = ?",
            (complaint_id,)
        ).fetchone()

        if complaint is None:
            abort(404)

        if request.method == "POST":
            status = request.form.get("status", "")
            department = request.form.get("department", "").strip()
            response = request.form.get("admin_response", "").strip()

            if status not in [
                "Pending", "In Progress", "Resolved", "Rejected"
            ]:
                flash("Invalid status.", "error")
            elif not department:
                flash("Department select karo.", "error")
            else:
                conn.execute("""
                    UPDATE complaints
                    SET status = ?, department = ?, admin_response = ?
                    WHERE complaint_id = ?
                """, (status, department, response, complaint_id))
                conn.commit()
                flash("Complaint update ho gayi.", "success")
                return redirect(url_for(
                    "admin.complaint_details",
                    complaint_id=complaint_id
                ))
    finally:
        conn.close()

    return render_template(
        "admin_complaint_details.html",
        complaint=complaint
    )
