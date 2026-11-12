from typing import Dict, Any, List
from src.models.schemas import (
    Syllabus,
    StudentProfile,
    StaticChecklist,
    StaticChecklistItem,
)


def generate_baseline_checklist_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node: Generates a static, linear checklist without dynamic buffer days
    or adaptive rescheduling. Serves as the Control Group baseline.
    """
    logs = list(state.get("execution_logs", []))
    logs.append("[BaselineEngine] Generating static control-group checklist...")

    syllabus_dict = state.get("syllabus")
    if not syllabus_dict:
        raise ValueError("Syllabus missing in state.")
    syllabus = Syllabus(**syllabus_dict)

    profile_dict = state.get("student_profile", {})
    profile = StudentProfile(**profile_dict) if profile_dict else StudentProfile()

    all_topics = syllabus.all_topics
    total_weeks = profile.target_weeks
    topics_per_week = max(1, len(all_topics) // total_weeks)

    checklist_items: List[StaticChecklistItem] = []

    for idx, topic in enumerate(all_topics):
        assigned_week = min(total_weeks, (idx // topics_per_week) + 1)
        # Find module title
        mod_title = next(
            (m.title for m in syllabus.modules if m.id == topic.module_id),
            "General Module"
        )
        item = StaticChecklistItem(
            topic_id=topic.id,
            title=topic.title,
            module_title=mod_title,
            assigned_week=assigned_week,
            estimated_hours=topic.estimated_hours,
            completed=False,
            completed_on_date=None,
        )
        checklist_items.append(item)

    checklist = StaticChecklist(
        student_id=profile.student_id,
        course_name=syllabus.course_name,
        items=checklist_items,
    )

    logs.append(f"[BaselineEngine] Static checklist initialized with {len(checklist_items)} unbuffered items.")

    return {
        "baseline_checklist": checklist.model_dump(),
        "execution_logs": logs,
        "next_step": "advise",
    }
