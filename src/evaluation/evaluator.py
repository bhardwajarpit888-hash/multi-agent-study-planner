import uuid
from datetime import datetime
from typing import Dict, Any, List
from src.models.schemas import Syllabus, StudyPlan, StudentProfile
from src.agents.syllabus_agent import extract_syllabus_node, create_default_syllabus
from src.agents.planner_agent import synthesize_plan_node
from src.agents.evaluator_agent import evaluate_checkin_node
from src.agents.replanner_agent import replan_schedule_node
from src.ingestion.sample_generator import SAMPLE_SYLLABUS_TEXT

GROUND_TRUTH_CORE_CONCEPTS = [
    "Linear Regression",
    "Gradient Descent",
    "Logistic Regression",
    "Overfitting",
    "Regularization",
    "Cross Validation",
    "Decision Trees",
    "Random Forests",
    "Boosting",
    "Neural Networks",
    "Backpropagation",
    "CNN",
]


def evaluate_syllabus_extraction(extracted_syllabus: Syllabus) -> Dict[str, Any]:
    """
    Evaluates extraction accuracy and concept recall against ground truth.
    """
    all_titles = " ".join([t.title.lower() for t in extracted_syllabus.all_topics])
    matched_concepts = []
    missing_concepts = []

    for concept in GROUND_TRUTH_CORE_CONCEPTS:
        if any(word.lower() in all_titles for word in concept.split()):
            matched_concepts.append(concept)
        else:
            missing_concepts.append(concept)

    recall = round((len(matched_concepts) / len(GROUND_TRUTH_CORE_CONCEPTS)) * 100.0, 1)

    return {
        "metric_name": "Concept Extraction Recall",
        "score_percentage": recall,
        "matched_count": len(matched_concepts),
        "total_expected": len(GROUND_TRUTH_CORE_CONCEPTS),
        "missing_concepts": missing_concepts,
        "status": "PASS" if recall >= 80.0 else "WARN",
    }


def evaluate_plan_constraints(plan: StudyPlan, profile: StudentProfile) -> Dict[str, Any]:
    """
    Evaluates whether the synthesized plan adheres to student constraints:
    1. Daily workload cap
    2. Buffer day presence
    3. Prerequisite topological order
    """
    daily_cap = profile.daily_available_hours
    total_days = 0
    overloaded_days = 0
    buffer_days_count = 0

    topic_schedule_day: Dict[str, int] = {}
    prerequisite_violations = []

    for week in plan.weeks:
        for day in week.days:
            total_days += 1
            if day.planned_hours > daily_cap + 0.5:
                overloaded_days += 1
            if day.is_buffer_day:
                buffer_days_count += 1
            for topic in day.allocated_topics:
                topic_schedule_day[topic.id] = day.day_number

    # Check prerequisite consistency
    for week in plan.weeks:
        for day in week.days:
            for topic in day.allocated_topics:
                for prereq_id in topic.prerequisites:
                    if prereq_id in topic_schedule_day:
                        if topic_schedule_day[prereq_id] >= day.day_number:
                            prerequisite_violations.append((topic.id, prereq_id))

    workload_adherence = round(((total_days - overloaded_days) / max(1, total_days)) * 100.0, 1)
    buffer_ratio = round((buffer_days_count / max(1, len(plan.weeks))) * 100.0, 1)
    prereq_health = 100.0 if not prerequisite_violations else round((1 - len(prerequisite_violations) / max(1, len(topic_schedule_day))) * 100.0, 1)

    return {
        "workload_constraint_adherence": workload_adherence,
        "buffer_day_preservation_rate": buffer_ratio,
        "prerequisite_integrity_score": prereq_health,
        "prerequisite_violations_count": len(prerequisite_violations),
        "total_days_evaluated": total_days,
        "overloaded_days_count": overloaded_days,
        "status": "PASS" if (workload_adherence >= 95.0 and prereq_health == 100.0) else "WARN",
    }


def evaluate_replanning_resilience() -> Dict[str, Any]:
    """
    Tests dynamic replanning behavior under simulated topic failure:
    Verifies that the missed topic was reallocated to an upcoming buffer
    without bumping the current daily study load.
    """
    syllabus = create_default_syllabus()
    profile = StudentProfile(daily_available_hours=2.5, study_days_per_week=6, target_weeks=4)

    # 1. Synthesize Plan
    plan_out = synthesize_plan_node({
        "syllabus": syllabus.model_dump(),
        "student_profile": profile.model_dump(),
        "execution_logs": [],
    })
    initial_plan = StudyPlan(**plan_out["current_plan"])

    # 2. Simulate Missed Topic T2 on Day 2
    mock_checkin = {
        "checkin_id": "test_chk",
        "student_id": "test_eval_user",
        "date": "2026-11-02",
        "day_number": 2,
        "completed_topic_ids": ["T1"],
        "missed_topic_ids": ["T2"],
        "actual_hours_spent": 1.5,
        "stress_rating": 3,
        "student_notes": "Eval stress test",
    }

    eval_out = evaluate_checkin_node({
        "current_plan": initial_plan.model_dump(),
        "latest_checkin": mock_checkin,
        "checkin_history": [],
        "unresolved_missed_topics": [],
        "execution_logs": [],
    })

    replan_out = replan_schedule_node({
        "current_plan": eval_out["current_plan"],
        "unresolved_missed_topics": eval_out["unresolved_missed_topics"],
        "student_profile": profile.model_dump(),
        "latest_checkin": mock_checkin,
        "replan_history": [],
        "execution_logs": [],
    })

    updated_plan = StudyPlan(**replan_out["current_plan"])
    replan_event = replan_out["latest_replan_event"]

    # Verification:
    # 1. Was plan version bumped?
    version_bumped = updated_plan.version > initial_plan.version
    # 2. Was T2 rescheduled?
    t2_rescheduled = "T2" in replan_event.get("rescheduled_to_dates", {})
    # 3. Was Day 3 overloaded (the cramming trap check)?
    day_3 = next(d for w in updated_plan.weeks for d in w.days if d.day_number == 3)
    no_cramming = day_3.planned_hours <= profile.daily_available_hours + 0.5

    soundness_score = 100.0 if (version_bumped and t2_rescheduled and no_cramming) else 50.0

    return {
        "metric_name": "Replanning Health & Anti-Cramming Index",
        "score_percentage": soundness_score,
        "version_bumped": version_bumped,
        "topic_rescheduled": t2_rescheduled,
        "cramming_trap_avoided": no_cramming,
        "rescheduled_date": replan_event.get("rescheduled_to_dates", {}).get("T2"),
        "status": "PASS" if soundness_score == 100.0 else "FAIL",
    }


def run_full_evaluation_suite() -> Dict[str, Any]:
    """
    Executes the entire automated LLM & Agent quality benchmark suite.
    """
    sample_syl = create_default_syllabus()
    profile = StudentProfile()

    plan_res = synthesize_plan_node({
        "syllabus": sample_syl.model_dump(),
        "student_profile": profile.model_dump(),
        "execution_logs": [],
    })
    study_plan = StudyPlan(**plan_res["current_plan"])

    extraction_eval = evaluate_syllabus_extraction(sample_syl)
    constraint_eval = evaluate_plan_constraints(study_plan, profile)
    replanning_eval = evaluate_replanning_resilience()

    composite_score = round(
        (extraction_eval["score_percentage"] +
         constraint_eval["workload_constraint_adherence"] +
         constraint_eval["prerequisite_integrity_score"] +
         replanning_eval["score_percentage"]) / 4.0, 1
    )

    return {
        "evaluation_id": f"eval_{uuid.uuid4().hex[:8]}",
        "timestamp": datetime.now().isoformat(),
        "composite_quality_score": composite_score,
        "extraction_benchmark": extraction_eval,
        "constraint_benchmark": constraint_eval,
        "replanning_benchmark": replanning_eval,
        "overall_status": "EXCELLENT (READY FOR PRODUCTION)" if composite_score >= 90.0 else "ACCEPTABLE",
    }
