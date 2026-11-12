from typing import Dict, Any
from src.agents.prompts import ADVISOR_PROMPT
from src.config import get_llm
from src.models.schemas import CheckInRecord, ReplanEvent


def generate_advice_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node: Generates encouraging, human-centered coaching advice
    explaining schedule changes and reinforcing self-efficacy.
    """
    logs = list(state.get("execution_logs", []))
    logs.append("[AdvisorAgent] Formulating personalized guidance and coaching feedback...")

    latest_checkin = state.get("latest_checkin")
    latest_replan = state.get("latest_replan_event")

    day_num = 1
    completed_count = 0
    missed_count = 0
    strategy = "N/A"
    replan_explanation = "Plan is executing smoothly on schedule."

    if latest_checkin:
        checkin = CheckInRecord(**latest_checkin)
        day_num = checkin.day_number
        completed_count = len(checkin.completed_topic_ids)
        missed_count = len(checkin.missed_topic_ids)

    if latest_replan:
        replan = ReplanEvent(**latest_replan)
        strategy = replan.strategy_used
        replan_explanation = replan.explanation

    llm = get_llm()
    prompt = ADVISOR_PROMPT.format(
        day_number=day_num,
        completed_count=completed_count,
        missed_count=missed_count,
        strategy=strategy,
        explanation=replan_explanation,
    )

    try:
        response = llm.invoke(prompt)
        advice_text = response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        logs.append(f"[AdvisorAgent] LLM generation note: {e}. Using deterministic coach message.")
        if missed_count > 0:
            advice_text = (
                f"Hey, don't worry about missing topics on Day {day_num}! Falling slightly behind is a natural part of mastering "
                f"complex technical subjects. We've utilized your upcoming buffer day to absorb the missed material smoothly. "
                "Take a deep breath and keep going—your total finish date remains unchanged."
            )
        else:
            advice_text = (
                f"Fantastic progress on Day {day_num}! You completed all scheduled topics right on time. "
                "Keep this consistent momentum going into tomorrow!"
            )

    logs.append("[AdvisorAgent] Coaching notes generated.")

    return {
        "advisor_notes": advice_text.strip(),
        "execution_logs": logs,
        "next_step": "done",
    }
