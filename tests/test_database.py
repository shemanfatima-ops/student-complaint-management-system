import sqlite3

import pytest

from models.database import get_db_connection, init_db


def test_database_connection_uses_temporary_database(app):
    with app.app_context():
        conn = get_db_connection()
        try:
            database_path = conn.execute("PRAGMA database_list").fetchone()["file"]
        finally:
            conn.close()

    assert database_path == app.config["DATABASE"]


def test_table_creation_creates_users_and_complaints_tables(app):
    with app.app_context():
        conn = get_db_connection()
        try:
            tables = {
                row["name"]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            }
        finally:
            conn.close()

    assert {"users", "complaints"}.issubset(tables)


def test_init_db_can_be_called_more_than_once(app):
    with app.app_context():
        init_db()
        init_db()
        conn = get_db_connection()
        try:
            user_table = conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'users'"
            ).fetchone()
        finally:
            conn.close()

    assert user_table["name"] == "users"


def test_database_insert_and_retrieve_user(app):
    with app.app_context():
        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                ("Database Test Student", "database@example.test", "hashed-password"),
            )
            conn.commit()
            user = conn.execute(
                "SELECT name, email FROM users WHERE email = ?",
                ("database@example.test",),
            ).fetchone()
        finally:
            conn.close()

    assert user["name"] == "Database Test Student"
    assert user["email"] == "database@example.test"


def test_database_rejects_duplicate_user_email(app):
    with app.app_context():
        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                ("First Student", "unique@example.test", "hash"),
            )
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    ("Second Student", "unique@example.test", "hash"),
                )
        finally:
            conn.close()
