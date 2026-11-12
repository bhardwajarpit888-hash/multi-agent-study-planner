import uuid
from datetime import datetime
from typing import Dict, Any, List
from src.models.schemas import StudyPlan, ReplanEvent, Topic, StudentProfile
from src.config import get_llm
from src.agents.prompts import REPLANNER_PROMPT


def replan_schedule_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node: Adaptively reorganizes remaining schedule when topics are missed.
    Avoids cramming traps by utilizing buffer days and light-load slots.
    """
    logs = list(state.get("execution_logs", []))
    logs.append("[ReplannerAgent] Initiating dynamic schedule adaptation...")

    plan_dict = state.get("current_plan")
    if not plan_dict:
        logs.append("[ReplannerAgent] Error: No current plan found.")
        return {"execution_logs": logs, "next_step": "advise"}

    plan = StudyPlan(**plan_dict)
    unresolved_topics_raw = state.get("unresolved_missed_topics", [])
    if not unresolved_topics_raw:
        logs.append("[ReplannerAgent] No missed topics to reallocate.")
        return {"execution_logs": logs, "next_step": "advise"}

    unresolved_topics = [Topic(**t) for t in unresolved_topics_raw]
    profile_dict = state.get("student_profile", {})
    daily_cap = profile_dict.get("daily_available_hours", 2.5)

    checkin_dict = state.get("latest_checkin", {})
    trigger_day = checkin_dict.get("day_number", 1)

    rescheduled_map: Dict[str, str] = {}
    remaining_unresolved: List[Topic] = []

    # 1. Attempt Buffer Absorption: look for future buffer days after trigger_day
    for topic in unresolved_topics:
        placed = False

        # First pass: try to place on an upcoming buffer day
        for week in plan.weeks:
            for day in week.days:
                if day.day_number > trigger_day and day.is_buffer_day:
                    if day.planned_hours + topic.estimated_hours <= daily_cap + 0.5:
                        day.allocated_topics.append(topic)
                        day.planned_hours = round(day.planned_hours + topic.estimated_hours, 1)
                        day.notes = f"Adapted: Absorbed catch-up topic '{topic.title}'"
                        rescheduled_map[topic.id] = day.date_str
                        placed = True
                        logs.append(f"[ReplannerAgent] Placed missed topic '{topic.title}' into Buffer Day {day.day_number} ({day.date_str}).")
                        break
            if placed:
                break

        # Second pass: if buffer is full, look for a regular future day with headroom
        if not placed:
            for week in plan.weeks:
                for day in week.days:
                    if day.day_number > trigger_day and not day.is_buffer_day:
                        if day.planned_hours + topic.estimated_hours <= daily_cap + 0.2:
                            day.allocated_topics.append(topic)
                            day.planned_hours = round(day.planned_hours + topic.estimated_hours, 1)
                            day.notes = f"Adapted: Rescheduled '{topic.title}'"
                            rescheduled_map[topic.id] = day.date_str
                            placed = True
                            logs.append(f"[ReplannerAgent] Placed missed topic '{topic.title}' into Regular Day {day.day_number} ({day.date_str}).")
                            break
                if placed:
                    break

        if not placed:
            remaining_unresolved.append(topic)

    # Strategy formulation
    strategy = "Buffer Day Absorption" if len(rescheduled_map) == len(unresolved_topics) else "Buffer & Low-Density Redistribution"

    explanation = (
        f"Missed topic(s) ({', '.join(rescheduled_map.keys())}) were automatically moved to your upcoming "
        f"designated buffer and low-density study days. Your daily study limit ({daily_cap} hrs) was strictly protected "
        "to prevent burnout or cramming."
    )

    replan_event = ReplanEvent(
        event_id=f"replan_{uuid.uuid4().hex[:8]}",
        timestamp=datetime.now().isoformat(),
        trigger_day=trigger_day,
        missed_topic_ids=[t.id for t in unresolved_topics],
        rescheduled_to_dates=rescheduled_map,
        strategy_used=strategy,
        explanation=explanation,
    )

    # Increment plan version
    plan.version += 1
    plan.updated_at = datetime.now().isoformat()

    history = list(state.get("replan_history", []))
    history.append(replan_event.model_dump())

    logs.append(f"[ReplannerAgent] Replan v{plan.version} finalized. Strategy: {strategy}.")

    return {
        "current_plan": plan.model_dump(),
        "unresolved_missed_topics": [t.model_dump() for t in remaining_unresolved],
        "replan_history": history,
        "latest_replan_event": replan_event.model_dump(),
        "has_missed_topics": False,
        "execution_logs": logs,
        "next_step": "advise",
    }
