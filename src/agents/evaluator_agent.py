from typing import Dict, Any, List
from src.models.schemas import CheckInRecord, StudyPlan, Topic


def evaluate_checkin_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node: Ingests student check-in, verifies completions vs missed topics,
    and determines whether an adaptive replan is required.
    """
    logs = list(state.get("execution_logs", []))
    checkin_dict = state.get("latest_checkin")
    
    if not checkin_dict:
        logs.append("[EvaluatorAgent] No new check-in detected.")
        return {"next_step": "done", "execution_logs": logs}

    checkin = CheckInRecord(**checkin_dict)
    logs.append(f"[EvaluatorAgent] Processing Day {checkin.day_number} check-in for {checkin.student_id}...")

    # Update checkin history
    history = list(state.get("checkin_history", []))
    history.append(checkin.model_dump())

    # Inspect current plan
    plan_dict = state.get("current_plan")
    unresolved_topics = list(state.get("unresolved_missed_topics", []))
    has_missed = False

    if plan_dict:
        plan = StudyPlan(**plan_dict)
        target_day = None

        # Find the day being checked in
        for week in plan.weeks:
            for day in week.days:
                if day.day_number == checkin.day_number:
                    target_day = day
                    break
            if target_day:
                break

        if target_day:
            if checkin.missed_topic_ids:
                has_missed = True
                target_day.status = "partial" if checkin.completed_topic_ids else "missed"
                logs.append(f"[EvaluatorAgent] Missed topics detected: {checkin.missed_topic_ids}.")

                # Identify missed topic objects from day's allocated topics
                for topic in target_day.allocated_topics:
                    if topic.id in checkin.missed_topic_ids:
                        # Append if not already in unresolved
                        if not any(t.get("id") == topic.id for t in unresolved_topics):
                            unresolved_topics.append(topic.model_dump())
            else:
                target_day.status = "completed"
                logs.append("[EvaluatorAgent] All scheduled topics completed successfully!")

        state["current_plan"] = plan.model_dump()

    logs.append(f"[EvaluatorAgent] Queue has {len(unresolved_topics)} unresolved missed topic(s). Has missed: {has_missed}")

    return {
        "current_plan": state.get("current_plan"),
        "checkin_history": history,
        "unresolved_missed_topics": unresolved_topics,
        "has_missed_topics": has_missed or len(unresolved_topics) > 0,
        "execution_logs": logs,
        "next_step": "replan" if (has_missed or len(unresolved_topics) > 0) else "advise",
    }
