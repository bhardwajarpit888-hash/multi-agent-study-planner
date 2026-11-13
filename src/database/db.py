import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
DB_PATH = os.path.join(DB_DIR, "study_planner.db")


def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initializes SQLite schema for multi-user persistence, traces, and check-ins."""
    conn = get_connection()
    with conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
            cohort_group TEXT NOT NULL DEFAULT 'A_ADAPTIVE',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS syllabi (
            id TEXT PRIMARY KEY,
            course_code TEXT NOT NULL,
            course_name TEXT NOT NULL,
            total_weeks INTEGER NOT NULL,
            raw_text TEXT,
            parsed_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS study_plans (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            course_name TEXT NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            plan_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS checkins (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            checkin_date TEXT NOT NULL,
            day_number INTEGER NOT NULL,
            completed_topic_ids TEXT NOT NULL,
            missed_topic_ids TEXT NOT NULL,
            actual_hours REAL NOT NULL,
            stress_rating INTEGER NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS replan_events (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            plan_id TEXT NOT NULL,
            trigger_day INTEGER NOT NULL,
            missed_topics TEXT NOT NULL,
            rescheduled_dates TEXT NOT NULL,
            strategy_used TEXT NOT NULL,
            explanation TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS agent_traces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trace_id TEXT NOT NULL,
            agent_name TEXT NOT NULL,
            latency_ms REAL NOT NULL,
            status TEXT NOT NULL,
            input_summary TEXT,
            output_summary TEXT,
            timestamp TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS eval_runs (
            id TEXT PRIMARY KEY,
            run_name TEXT NOT NULL,
            metrics_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)
    conn.close()


# Database helper operations
def save_user_study_plan(user_id: str, plan_dict: Dict[str, Any]):
    conn = get_connection()
    plan_id = plan_dict.get("plan_id", f"plan_{user_id}")
    course_name = plan_dict.get("course_name", "Curriculum")
    version = plan_dict.get("version", 1)
    now = datetime.now().isoformat()
    plan_json = json.dumps(plan_dict)

    with conn:
        conn.execute("""
            INSERT INTO study_plans (id, user_id, course_name, version, plan_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                version = excluded.version,
                plan_json = excluded.plan_json,
                updated_at = excluded.updated_at
        """, (plan_id, user_id, course_name, version, plan_json, now, now))
    conn.close()


def get_user_study_plan(user_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT plan_json FROM study_plans
        WHERE user_id = ?
        ORDER BY updated_at DESC LIMIT 1
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row["plan_json"])
    return None


def record_checkin_db(checkin_data: Dict[str, Any]):
    conn = get_connection()
    now = datetime.now().isoformat()
    with conn:
        conn.execute("""
            INSERT OR REPLACE INTO checkins
            (id, user_id, checkin_date, day_number, completed_topic_ids, missed_topic_ids, actual_hours, stress_rating, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            checkin_data["checkin_id"],
            checkin_data["student_id"],
            checkin_data["date"],
            checkin_data["day_number"],
            json.dumps(checkin_data.get("completed_topic_ids", [])),
            json.dumps(checkin_data.get("missed_topic_ids", [])),
            checkin_data.get("actual_hours_spent", 0.0),
            checkin_data.get("stress_rating", 2),
            checkin_data.get("student_notes", ""),
            now,
        ))
    conn.close()


def get_user_checkins_db(user_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM checkins WHERE user_id = ? ORDER BY day_number ASC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        results.append({
            "checkin_id": r["id"],
            "student_id": r["user_id"],
            "date": r["checkin_date"],
            "day_number": r["day_number"],
            "completed_topic_ids": json.loads(r["completed_topic_ids"]),
            "missed_topic_ids": json.loads(r["missed_topic_ids"]),
            "actual_hours_spent": r["actual_hours"],
            "stress_rating": r["stress_rating"],
            "student_notes": r["notes"],
            "created_at": r["created_at"],
        })
    return results


def log_agent_trace_db(trace_id: str, agent_name: str, latency_ms: float, status: str, input_summary: str, output_summary: str):
    conn = get_connection()
    now = datetime.now().isoformat()
    with conn:
        conn.execute("""
            INSERT INTO agent_traces (trace_id, agent_name, latency_ms, status, input_summary, output_summary, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (trace_id, agent_name, round(latency_ms, 2), status, input_summary, output_summary, now))
    conn.close()


def get_all_agent_traces_db(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM agent_traces ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# Auto-initialize database on import
init_database()
