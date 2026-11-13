import hashlib
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from src.database.db import get_connection

SALT = "langgraph_study_planner_secure_salt_2026"


def hash_password(password: str) -> str:
    """Hashes password with static salt using SHA-256."""
    return hashlib.sha256((SALT + password).encode("utf-8")).hexdigest()


def seed_default_users():
    """Seeds default recruiter/demo accounts if database is empty."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM users")
    count = cursor.fetchone()["count"]

    if count == 0:
        default_users = [
            ("user_adaptive", "student_adaptive", hash_password("study123"), "student", "A_ADAPTIVE"),
            ("user_static", "student_static", hash_password("study123"), "student", "B_STATIC_CHECKLIST"),
            ("user_admin", "admin", hash_password("admin123"), "admin", "A_ADAPTIVE"),
        ]
        now = datetime.now().isoformat()
        with conn:
            conn.executemany("""
                INSERT INTO users (id, username, password_hash, role, cohort_group, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [(u[0], u[1], u[2], u[3], u[4], now) for u in default_users])
    conn.close()


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticates username and password against SQLite database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username.strip().lower(),))
    user = cursor.fetchone()
    conn.close()

    if user and user["password_hash"] == hash_password(password):
        return {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "cohort_group": user["cohort_group"],
            "created_at": user["created_at"],
        }
    return None


def register_user(username: str, password: str, cohort_group: str = "A_ADAPTIVE") -> Dict[str, Any]:
    """Registers a new student account."""
    clean_username = username.strip().lower()
    if len(clean_username) < 3:
        raise ValueError("Username must be at least 3 characters.")
    if len(password) < 4:
        raise ValueError("Password must be at least 4 characters.")

    conn = get_connection()
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    pwd_hash = hash_password(password)
    now = datetime.now().isoformat()

    try:
        with conn:
            conn.execute("""
                INSERT INTO users (id, username, password_hash, role, cohort_group, created_at)
                VALUES (?, ?, ?, 'student', ?, ?)
            """, (user_id, clean_username, pwd_hash, cohort_group, now))
    except Exception as e:
        conn.close()
        raise ValueError(f"Username '{clean_username}' is already taken.")

    conn.close()
    return {
        "id": user_id,
        "username": clean_username,
        "role": "student",
        "cohort_group": cohort_group,
        "created_at": now,
    }


# Auto-seed on module import
seed_default_users()
