import uuid
import datetime

from models.database import get_db_connection

def generate_complaint_id():
    return "CMP-" + str(uuid.uuid4())[:8].upper()

def save_complaint(user_id, category, description):
    complaint_id = generate_complaint_id()
    status = "Pending"
    department = "Unassigned"
    created_at = datetime.datetime.now().isoformat()

    conn = get_db_connection()
    try:
        conn.execute(
            """
            INSERT INTO complaints (
                complaint_id, user_id, category, description, status, department, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (complaint_id, user_id, category, description, status, department, created_at),
        )
        conn.commit()
    finally:
        conn.close()

    return complaint_id