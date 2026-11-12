from typing import List, Dict, Any, Optional
from src.models.schemas import ExperimentCohortMember
from src.utils.storage import get_cohort_members, save_cohort_members
from src.experiment.simulator import run_30_day_cohort_simulation
from src.experiment.metrics import calculate_cohort_metrics


class CohortManager:
    """
    Manages the 5-10 classmate cohort for the 1-month A/B comparison experiment.
    """

    def __init__(self):
        self.members = get_cohort_members()
        if not self.members:
            # Initialize with default simulation if empty
            self.members = run_30_day_cohort_simulation(seed=42)
            save_cohort_members(self.members)

    def enroll_classmate(self, name: str, group: str) -> Dict[str, Any]:
        student_id = f"user_{len(self.members) + 1:02d}"
        new_member = ExperimentCohortMember(
            student_id=student_id,
            name=name,
            cohort_group=group,
            start_date="2026-11-01",
            is_active=True,
            checkin_count=0,
            total_assigned_topics=12,
            completed_topics_count=0,
            missed_topics_count=0,
            recovered_topics_count=0,
            drop_off_day=None,
            average_stress=2.0,
            final_completion_rate=0.0,
        )
        self.members.append(new_member.model_dump())
        save_cohort_members(self.members)
        return new_member.model_dump()

    def update_classmate_progress(
        self,
        student_id: str,
        completed_add: int,
        missed_add: int,
        recovered_add: int = 0,
        stress: float = 2.5,
        dropped_off: bool = False,
        drop_off_day: Optional[int] = None,
    ):
        for m in self.members:
            if m["student_id"] == student_id:
                m["checkin_count"] += 1
                m["completed_topics_count"] = min(m["total_assigned_topics"], m["completed_topics_count"] + completed_add)
                m["missed_topics_count"] += missed_add
                m["recovered_topics_count"] += recovered_add
                m["average_stress"] = round((m["average_stress"] + stress) / 2.0, 2)
                m["final_completion_rate"] = round((m["completed_topics_count"] / max(1, m["total_assigned_topics"])) * 100.0, 1)
                if dropped_off:
                    m["is_active"] = False
                    m["drop_off_day"] = drop_off_day or m["checkin_count"]
                break
        save_cohort_members(self.members)

    def reset_cohort(self, seed: int = 42):
        self.members = run_30_day_cohort_simulation(seed=seed)
        save_cohort_members(self.members)

    def get_cohort_data(self) -> List[Dict[str, Any]]:
        return self.members

    def get_summary_metrics(self) -> Dict[str, Any]:
        return calculate_cohort_metrics(self.members)
