import unittest
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.schemas import Syllabus, StudentProfile, CheckInRecord, Topic
from src.agents.syllabus_agent import extract_syllabus_node, create_default_syllabus
from src.agents.planner_agent import synthesize_plan_node
from src.baseline.checklist import generate_baseline_checklist_node
from src.agents.evaluator_agent import evaluate_checkin_node
from src.agents.replanner_agent import replan_schedule_node
from src.agents.advisor_agent import generate_advice_node
from src.experiment.cohort_manager import CohortManager
from src.experiment.metrics import calculate_cohort_metrics
from src.ingestion.sample_generator import SAMPLE_SYLLABUS_TEXT


class TestMultiAgentStudyPlanner(unittest.TestCase):

    def setUp(self):
        self.profile = StudentProfile(
            student_id="test_student",
            name="Alice",
            daily_available_hours=2.5,
            study_days_per_week=6,
            start_date="2026-11-01",
            target_weeks=4,
            cohort_group="A_ADAPTIVE",
        )

    def test_01_syllabus_extraction(self):
        state = {
            "raw_syllabus_text": SAMPLE_SYLLABUS_TEXT,
            "execution_logs": [],
        }
        res = extract_syllabus_node(state)
        self.assertIn("syllabus", res)
        syllabus = Syllabus(**res["syllabus"])
        self.assertEqual(len(syllabus.modules), 4)
        self.assertEqual(len(syllabus.all_topics), 12)
        print("\n[Test 1 Passed] Syllabus Extraction successfully extracted 4 modules and 12 topics.")

    def test_02_plan_synthesis(self):
        syllabus = create_default_syllabus()
        state = {
            "syllabus": syllabus.model_dump(),
            "student_profile": self.profile.model_dump(),
            "execution_logs": [],
        }
        res = synthesize_plan_node(state)
        self.assertIn("current_plan", res)
        plan = res["current_plan"]
        self.assertEqual(len(plan["weeks"]), 4)
        
        # Check that buffer days exist
        buffer_days_found = 0
        for w in plan["weeks"]:
            for d in w["days"]:
                if d["is_buffer_day"]:
                    buffer_days_found += 1
        self.assertGreaterEqual(buffer_days_found, 4)
        print(f"\n[Test 2 Passed] Plan Synthesis generated 4 weeks with {buffer_days_found} dedicated buffer/catch-up days.")

    def test_03_baseline_checklist(self):
        syllabus = create_default_syllabus()
        state = {
            "syllabus": syllabus.model_dump(),
            "student_profile": self.profile.model_dump(),
            "execution_logs": [],
        }
        res = generate_baseline_checklist_node(state)
        self.assertIn("baseline_checklist", res)
        checklist = res["baseline_checklist"]
        self.assertEqual(len(checklist["items"]), 12)
        print("\n[Test 3 Passed] Baseline Checklist generated 12 static checklist items for control group.")

    def test_04_feedback_loop_and_replanning(self):
        # 1. Synthesize plan
        syllabus = create_default_syllabus()
        plan_res = synthesize_plan_node({
            "syllabus": syllabus.model_dump(),
            "student_profile": self.profile.model_dump(),
            "execution_logs": [],
        })
        current_plan = plan_res["current_plan"]

        # 2. Simulate Day 2 check-in where student completed T1 but missed T2
        checkin = CheckInRecord(
            checkin_id="chk_01",
            student_id="test_student",
            date="2026-11-02",
            day_number=2,
            completed_topic_ids=["T1"],
            missed_topic_ids=["T2"],
            actual_hours_spent=1.5,
            perceived_difficulty=4,
            student_notes="Fell behind on Gradient Descent math equations.",
            stress_rating=3,
        )

        eval_res = evaluate_checkin_node({
            "current_plan": current_plan,
            "latest_checkin": checkin.model_dump(),
            "checkin_history": [],
            "unresolved_missed_topics": [],
            "execution_logs": [],
        })

        self.assertTrue(eval_res["has_missed_topics"])
        self.assertEqual(len(eval_res["unresolved_missed_topics"]), 1)
        self.assertEqual(eval_res["unresolved_missed_topics"][0]["id"], "T2")

        # 3. Trigger dynamic replanning
        replan_res = replan_schedule_node({
            "current_plan": eval_res["current_plan"],
            "unresolved_missed_topics": eval_res["unresolved_missed_topics"],
            "student_profile": self.profile.model_dump(),
            "latest_checkin": checkin.model_dump(),
            "replan_history": [],
            "execution_logs": [],
        })

        self.assertIn("current_plan", replan_res)
        new_plan = replan_res["current_plan"]
        self.assertEqual(new_plan["version"], 2)
        self.assertEqual(len(replan_res["replan_history"]), 1)
        replan_event = replan_res["replan_history"][0]
        self.assertIn("T2", replan_event["rescheduled_to_dates"])
        print(f"\n[Test 4 Passed] Dynamic Feedback Loop replanned plan to v{new_plan['version']}! T2 rescheduled to {replan_event['rescheduled_to_dates']['T2']}.")

        # 4. Generate coaching advice
        advice_res = generate_advice_node({
            "latest_checkin": checkin.model_dump(),
            "latest_replan_event": replan_event,
            "execution_logs": [],
        })
        self.assertTrue(len(advice_res["advisor_notes"]) > 20)
        print(f"\n[Advisor Note]: {advice_res['advisor_notes']}")

    def test_05_cohort_experiment_metrics(self):
        manager = CohortManager()
        metrics = manager.get_summary_metrics()
        self.assertIn("group_a_adaptive", metrics)
        self.assertIn("group_b_static", metrics)
        self.assertIn("comparison", metrics)

        comp_a = metrics["group_a_adaptive"]["avg_completion_rate"]
        comp_b = metrics["group_b_static"]["avg_completion_rate"]
        self.assertGreater(comp_a, comp_b)
        print(f"\n[Test 5 Passed] Cohort Experiment calculated! Group A (Adaptive): {comp_a}% vs Group B (Static): {comp_b}%.")


if __name__ == "__main__":
    unittest.main()
