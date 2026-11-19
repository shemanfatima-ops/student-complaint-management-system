import os
import sqlite3
from flask import Blueprint, render_template, session, request, abort, redirect, url_for

tracking_bp = Blueprint("tracking", __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "database.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id TEXT NOT NULL,
            status TEXT NOT NULL,
            note TEXT,
            changed_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    return conn


@tracking_bp.route("/my-complaints")
def my_complaints():
    uid = session.get("user_id")
    if not uid:
        return redirect(url_for("auth.login"))

    q = request.args.get("q", "").strip()
    conn = get_db()
    try:
        if q:
            rows = conn.execute(
                "SELECT * FROM complaints WHERE user_id = ? AND complaint_id LIKE ? ORDER BY id DESC",
                (uid, "%" + q + "%")
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM complaints WHERE user_id = ? ORDER BY id DESC",
                (uid,)
            ).fetchall()
    finally:
        conn.close()
    return render_template("my_complaints.html", complaints=rows, q=q)


@tracking_bp.route("/complaint/<complaint_id>")
def complaint_details(complaint_id):
    uid = session.get("user_id")
    if not uid:
        return redirect(url_for("auth.login"))

    conn = get_db()
    try:
        c = conn.execute(
            "SELECT * FROM complaints WHERE complaint_id = ?", (complaint_id,)
        ).fetchone()
        if c is None:
            abort(404)
        if c["user_id"] != uid:
            abort(403)
        history = conn.execute(
            "SELECT * FROM status_history WHERE complaint_id = ? ORDER BY id",
            (complaint_id,)
        ).fetchall()
    finally:
        conn.close()
    return render_template("complaint_details.html", c=c, history=history)