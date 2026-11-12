from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.models.state import StudyPlanState
from src.agents.syllabus_agent import extract_syllabus_node
from src.agents.planner_agent import synthesize_plan_node
from src.baseline.checklist import generate_baseline_checklist_node
from src.agents.evaluator_agent import evaluate_checkin_node
from src.agents.replanner_agent import replan_schedule_node
from src.agents.advisor_agent import generate_advice_node


def route_after_evaluation(state: Dict[str, Any]) -> Literal["replan_schedule", "generate_advice"]:
    """
    Conditional routing edge: If missed topics exist, trigger dynamic replanning;
    otherwise, proceed directly to advisor feedback.
    """
    if state.get("has_missed_topics", False) or len(state.get("unresolved_missed_topics", [])) > 0:
        return "replan_schedule"
    return "generate_advice"


def build_study_planner_graph():
    """
    Constructs and compiles the full LangGraph multi-agent workflow.
    """
    workflow = StateGraph(StudyPlanState)

    # Register Nodes
    workflow.add_node("extract_syllabus", extract_syllabus_node)
    workflow.add_node("synthesize_plan", synthesize_plan_node)
    workflow.add_node("generate_baseline", generate_baseline_checklist_node)
    workflow.add_node("evaluate_checkin", evaluate_checkin_node)
    workflow.add_node("replan_schedule", replan_schedule_node)
    workflow.add_node("generate_advice", generate_advice_node)

    # Creation pipeline
    workflow.add_edge(START, "extract_syllabus")
    workflow.add_edge("extract_syllabus", "synthesize_plan")
    workflow.add_edge("synthesize_plan", "generate_baseline")
    workflow.add_edge("generate_baseline", "generate_advice")
    workflow.add_edge("generate_advice", END)

    # Checkpoint memory for state persistence
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)
    return app


def build_feedback_loop_graph():
    """
    Constructs a dedicated feedback-loop graph for handling student check-in
    and conditional replanning cycles.
    """
    workflow = StateGraph(StudyPlanState)

    workflow.add_node("evaluate_checkin", evaluate_checkin_node)
    workflow.add_node("replan_schedule", replan_schedule_node)
    workflow.add_node("generate_advice", generate_advice_node)

    # Entry point is evaluation
    workflow.add_edge(START, "evaluate_checkin")

    # Conditional edge based on check-in evaluation
    workflow.add_conditional_edges(
        "evaluate_checkin",
        route_after_evaluation,
        {
            "replan_schedule": "replan_schedule",
            "generate_advice": "generate_advice",
        },
    )

    workflow.add_edge("replan_schedule", "generate_advice")
    workflow.add_edge("generate_advice", END)

    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)
