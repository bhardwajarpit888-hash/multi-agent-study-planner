from typing import List, Dict, Any


def calculate_cohort_metrics(cohort_members: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes rigorous statistical metrics comparing Group A (Adaptive Planner)
    versus Group B (Static Checklist).
    """
    group_a = [m for m in cohort_members if m.get("cohort_group") == "A_ADAPTIVE"]
    group_b = [m for m in cohort_members if m.get("cohort_group") == "B_STATIC_CHECKLIST"]

    def aggregate_group(members: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not members:
            return {
                "count": 0,
                "avg_completion_rate": 0.0,
                "avg_recovery_rate": 0.0,
                "drop_off_count": 0,
                "drop_off_rate": 0.0,
                "avg_stress_rating": 0.0,
            }

        total_comp = sum(m.get("final_completion_rate", 0.0) for m in members)
        drop_offs = sum(1 for m in members if m.get("drop_off_day") is not None)
        stress_sum = sum(m.get("average_stress", 2.5) for m in members)

        # Recovery rate: recovered / missed
        total_missed = sum(m.get("missed_topics_count", 0) for m in members)
        total_recovered = sum(m.get("recovered_topics_count", 0) for m in members)
        recovery_rate = (total_recovered / total_missed * 100.0) if total_missed > 0 else 100.0

        return {
            "count": len(members),
            "avg_completion_rate": round(total_comp / len(members), 1),
            "avg_recovery_rate": round(recovery_rate, 1),
            "drop_off_count": drop_offs,
            "drop_off_rate": round((drop_offs / len(members)) * 100.0, 1),
            "avg_stress_rating": round(stress_sum / len(members), 2),
        }

    stats_a = aggregate_group(group_a)
    stats_b = aggregate_group(group_b)

    completion_lift = round(stats_a["avg_completion_rate"] - stats_b["avg_completion_rate"], 1)
    stress_reduction = round(stats_b["avg_stress_rating"] - stats_a["avg_stress_rating"], 2)

    return {
        "group_a_adaptive": stats_a,
        "group_b_static": stats_b,
        "comparison": {
            "completion_lift_percentage_points": completion_lift,
            "recovery_advantage": round(stats_a["avg_recovery_rate"] - stats_b["avg_recovery_rate"], 1),
            "drop_off_reduction_percentage_points": round(stats_b["drop_off_rate"] - stats_a["drop_off_rate"], 1),
            "stress_reduction_points": stress_reduction,
        },
    }
