import os
import json
from typing import Dict, Any, List, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
STORE_FILE = os.path.join(DATA_DIR, "study_planner_db.json")


def _init_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(STORE_FILE):
        initial_data = {
            "active_plan": None,
            "syllabus": None,
            "profile": None,
            "checkins": [],
            "replans": [],
            "cohort_members": [],
        }
        with open(STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=2)


def load_db() -> Dict[str, Any]:
    _init_storage()
    try:
        with open(STORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Storage] Warning reading DB: {e}. Reinitializing.")
        _init_storage()
        with open(STORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)


def save_db(data: Dict[str, Any]):
    _init_storage()
    with open(STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_stored_plan() -> Optional[Dict[str, Any]]:
    db = load_db()
    return db.get("active_plan")


def save_stored_plan(plan_dict: Dict[str, Any]):
    db = load_db()
    db["active_plan"] = plan_dict
    save_db(db)


def get_cohort_members() -> List[Dict[str, Any]]:
    db = load_db()
    return db.get("cohort_members", [])


def save_cohort_members(members: List[Dict[str, Any]]):
    db = load_db()
    db["cohort_members"] = members
    save_db(db)


def add_checkin_record(checkin_dict: Dict[str, Any]):
    db = load_db()
    checkins = db.get("checkins", [])
    checkins.append(checkin_dict)
    db["checkins"] = checkins
    save_db(db)


def get_all_checkins() -> List[Dict[str, Any]]:
    db = load_db()
    return db.get("checkins", [])
