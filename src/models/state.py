from typing import TypedDict, List, Optional, Dict, Any
from src.models.schemas import (
    Syllabus,
    StudentProfile,
    StudyPlan,
    CheckInRecord,
    ReplanEvent,
    StaticChecklist,
    Topic,
)


class StudyPlanState(TypedDict, total=False):
    # Syllabus and Extraction
    raw_syllabus_text: str
    syllabus: Optional[Dict[str, Any]]  # Serialized Syllabus
    
    # Student Profile
    student_profile: Dict[str, Any]     # Serialized StudentProfile
    
    # Plans
    current_plan: Optional[Dict[str, Any]]    # Serialized StudyPlan
    baseline_checklist: Optional[Dict[str, Any]] # Serialized StaticChecklist
    
    # Feedback & Monitoring Loop
    latest_checkin: Optional[Dict[str, Any]]  # Serialized CheckInRecord
    checkin_history: List[Dict[str, Any]]     # List of CheckInRecord dicts
    unresolved_missed_topics: List[Dict[str, Any]] # List of Topic dicts awaiting redistribution
    
    # Replanning & Guidance
    replan_history: List[Dict[str, Any]]      # List of ReplanEvent dicts
    latest_replan_event: Optional[Dict[str, Any]]
    advisor_notes: str                        # Human-readable empathetic coaching text
    
    # Routing & Flow control
    next_step: str                            # e.g., "synthesize", "replan", "advise", "done"
    has_missed_topics: bool
    iteration_count: int
    execution_logs: List[str]
