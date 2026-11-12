import uuid
from datetime import datetime, date, timedelta
from typing import Dict, Any, List
from src.models.schemas import (
    Syllabus,
    StudentProfile,
    StudyPlan,
    WeekSchedule,
    DaySchedule,
    Topic,
)


def synthesize_plan_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node: Synthesizes a resilient, adaptive multi-week study plan
    featuring dedicated buffer days and balanced daily cognitive load.
    """
    logs = list(state.get("execution_logs", []))
    logs.append("[PlannerAgent] Synthesizing adaptive weekly study plan with buffer intervals...")

    syllabus_dict = state.get("syllabus")
    if not syllabus_dict:
        raise ValueError("Syllabus data missing in state.")
    syllabus = Syllabus(**syllabus_dict)

    profile_dict = state.get("student_profile", {})
    profile = StudentProfile(**profile_dict) if profile_dict else StudentProfile()

    # Plan parameters
    start_date = datetime.strptime(profile.start_date, "%Y-%m-%d").date()
    target_weeks = min(max(profile.target_weeks, 1), 12)
    daily_cap = profile.daily_available_hours
    study_days = profile.study_days_per_week

    # All topics in order
    all_topics: List[Topic] = syllabus.all_topics
    topic_queue = list(all_topics)

    weeks_schedules: List[WeekSchedule] = []
    current_date = start_date
    day_counter = 1

    for w_idx in range(1, target_weeks + 1):
        week_days: List[DaySchedule] = []
        week_start_date = current_date
        buffer_hours_reserved = 0.0

        for d_idx in range(1, 8):
            day_name = current_date.strftime("%A")
            is_study_day = d_idx <= study_days
            # Designate the second-to-last study day (e.g. Saturday) as a dedicated buffer day
            is_buffer_day = (d_idx == study_days and study_days > 1) or (not is_study_day)

            day_topics: List[Topic] = []
            day_hours = 0.0

            if is_study_day and not is_buffer_day:
                # Allocate topics until daily cap is reached
                while topic_queue:
                    next_topic = topic_queue[0]
                    if day_hours + next_topic.estimated_hours <= daily_cap + 0.5 or not day_topics:
                        day_topics.append(topic_queue.pop(0))
                        day_hours += next_topic.estimated_hours
                    else:
                        break

            if is_buffer_day:
                buffer_hours_reserved += daily_cap
                status_notes = "Reserved for catch-up, consolidation, and buffer"
            else:
                status_notes = f"Target study duration: {round(day_hours, 1)} hrs"

            day_sched = DaySchedule(
                day_number=day_counter,
                date_str=current_date.isoformat(),
                day_name=day_name,
                allocated_topics=day_topics,
                planned_hours=round(day_hours, 1),
                is_buffer_day=is_buffer_day,
                status="pending",
                notes=status_notes,
            )
            week_days.append(day_sched)
            current_date += timedelta(days=1)
            day_counter += 1

        week_end_date = current_date - timedelta(days=1)
        theme = f"Module {w_idx}: Focused Learning & Practical Applications" if w_idx <= len(syllabus.modules) else "Comprehensive Review & Capstone"
        
        week_sched = WeekSchedule(
            week_number=w_idx,
            start_date=week_start_date.isoformat(),
            end_date=week_end_date.isoformat(),
            days=week_days,
            buffer_hours_reserved=round(buffer_hours_reserved, 1),
            theme=theme,
        )
        weeks_schedules.append(week_sched)

    study_plan = StudyPlan(
        plan_id=f"plan_{uuid.uuid4().hex[:8]}",
        student_id=profile.student_id,
        course_name=syllabus.course_name,
        weeks=weeks_schedules,
        version=1,
    )

    logs.append(f"[PlannerAgent] Successfully synthesized {len(weeks_schedules)}-week adaptive schedule with {day_counter - 1} total days.")

    return {
        "current_plan": study_plan.model_dump(),
        "execution_logs": logs,
        "next_step": "baseline",
    }
