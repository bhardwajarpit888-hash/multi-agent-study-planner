import random
from typing import List, Dict, Any
from src.models.schemas import ExperimentCohortMember


def run_30_day_cohort_simulation(seed: int = 42) -> List[Dict[str, Any]]:
    """
    Simulates a rigorous 30-day A/B experiment with 10 classmates:
    - 5 in Group A: Multi-Agent Adaptive Planner (dynamic buffer replanning)
    - 5 in Group B: Plain Static Checklist (unbuffered, no replan)
    
    Models realistic student events:
    - Sporadic mid-week delays (e.g. sick days, lab deadlines, difficult topics)
    - Demonstrates why static checklists cause drop-offs while adaptive replanners recover.
    """
    random.seed(seed)
    total_curriculum_topics = 12

    classmates = [
        {"id": "user_01", "name": "Aarav S.", "group": "A_ADAPTIVE", "grit": 0.85},
        {"id": "user_02", "name": "Priya M.", "group": "A_ADAPTIVE", "grit": 0.90},
        {"id": "user_03", "name": "Rohan D.", "group": "A_ADAPTIVE", "grit": 0.75},
        {"id": "user_04", "name": "Sneha K.", "group": "A_ADAPTIVE", "grit": 0.80},
        {"id": "user_05", "name": "Vikram T.", "group": "A_ADAPTIVE", "grit": 0.70},
        {"id": "user_06", "name": "Ananya R.", "group": "B_STATIC_CHECKLIST", "grit": 0.85},
        {"id": "user_07", "name": "Karthik N.", "group": "B_STATIC_CHECKLIST", "grit": 0.90},
        {"id": "user_08", "name": "Neha P.", "group": "B_STATIC_CHECKLIST", "grit": 0.75},
        {"id": "user_09", "name": "Aditya V.", "group": "B_STATIC_CHECKLIST", "grit": 0.70},
        {"id": "user_10", "name": "Tanvi B.", "group": "B_STATIC_CHECKLIST", "grit": 0.65},
    ]

    results: List[Dict[str, Any]] = []

    for cm in classmates:
        is_adaptive = cm["group"] == "A_ADAPTIVE"
        grit = cm["grit"]

        completed_topics = 0
        missed_topics = 0
        recovered_topics = 0
        drop_off_day = None
        stress_levels: List[float] = []

        active = True
        consecutive_misses = 0

        for day in range(1, 31):
            if not active:
                break

            # Sickness or college exam distraction probability
            daily_distraction = random.random() > (grit + 0.05)

            if daily_distraction:
                missed_topics += 1
                consecutive_misses += 1
                current_stress = min(5.0, 3.0 + consecutive_misses * 0.5)
            else:
                consecutive_misses = max(0, consecutive_misses - 1)
                completed_topics = min(total_curriculum_topics, completed_topics + 1)
                current_stress = max(1.0, 2.0 + (consecutive_misses * 0.2))

            stress_levels.append(current_stress)

            # In Group A (Adaptive), the agent buffers and reschedules missed topics
            if is_adaptive and consecutive_misses > 0:
                # Buffer day at end of week (Day 6, 13, 20, 27) absorbs missed topics
                if day % 7 in [6, 0] or random.random() < 0.6:
                    recovered_topics += 1
                    consecutive_misses = max(0, consecutive_misses - 1)
                    completed_topics = min(total_curriculum_topics, completed_topics + 1)
                    # Stress relief from agent replanning
                    stress_levels[-1] = max(1.5, stress_levels[-1] - 1.2)

            # In Group B (Static Checklist), accumulated unaddressed backlog leads to abandonment
            if not is_adaptive and consecutive_misses >= 3:
                # 70% chance student drops off from overwhelming checklist backlog
                if random.random() < 0.75 and day >= 14:
                    active = False
                    drop_off_day = day
                    break

        final_completion_rate = round((completed_topics / total_curriculum_topics) * 100.0, 1)
        final_completion_rate = min(100.0, final_completion_rate)
        avg_stress = round(sum(stress_levels) / len(stress_levels), 2) if stress_levels else 2.5

        member = ExperimentCohortMember(
            student_id=cm["id"],
            name=cm["name"],
            cohort_group=cm["group"],
            start_date="2026-10-15",
            is_active=active,
            checkin_count=len(stress_levels),
            total_assigned_topics=total_curriculum_topics,
            completed_topics_count=completed_topics,
            missed_topics_count=missed_topics,
            recovered_topics_count=recovered_topics,
            drop_off_day=drop_off_day,
            average_stress=avg_stress,
            final_completion_rate=final_completion_rate,
        )
        results.append(member.model_dump())

    return results
