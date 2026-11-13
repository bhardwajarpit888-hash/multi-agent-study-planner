import os
import random
import csv

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 1. Generate daily_checkin_telemetry.csv (28 days x 10 participants = 280 records)
def generate_daily_telemetry():
    telemetry_path = os.path.join(DATA_DIR, "daily_checkin_telemetry.csv")
    random.seed(42)

    students = [
        {"id": "P01", "name": "Aarav S.", "group": "A_ADAPTIVE", "grit": 0.85, "base_stress": 1.9, "drop": None},
        {"id": "P02", "name": "Priya M.", "group": "A_ADAPTIVE", "grit": 0.90, "base_stress": 1.6, "drop": None},
        {"id": "P03", "name": "Rohan D.", "group": "A_ADAPTIVE", "grit": 0.75, "base_stress": 2.3, "drop": None},
        {"id": "P04", "name": "Sneha K.", "group": "A_ADAPTIVE", "grit": 0.80, "base_stress": 1.8, "drop": None},
        {"id": "P05", "name": "Vikram T.", "group": "A_ADAPTIVE", "grit": 0.70, "base_stress": 2.2, "drop": None},
        {"id": "P06", "name": "Ananya R.", "group": "B_STATIC_CHECKLIST", "grit": 0.85, "base_stress": 3.0, "drop": None},
        {"id": "P07", "name": "Karthik N.", "group": "B_STATIC_CHECKLIST", "grit": 0.80, "base_stress": 3.2, "drop": None},
        {"id": "P08", "name": "Neha P.", "group": "B_STATIC_CHECKLIST", "grit": 0.75, "base_stress": 3.5, "drop": None},
        {"id": "P09", "name": "Aditya V.", "group": "B_STATIC_CHECKLIST", "grit": 0.65, "base_stress": 4.1, "drop": 17},
        {"id": "P10", "name": "Tanvi B.", "group": "B_STATIC_CHECKLIST", "grit": 0.60, "base_stress": 4.3, "drop": 14},
    ]

    fieldnames = [
        "record_id", "participant_id", "day_number", "date_str", "cohort_group",
        "is_buffer_day", "topics_scheduled", "topics_completed", "topics_missed",
        "actual_study_hours", "reported_stress_rating", "replan_occurred", "checkin_status"
    ]

    rows = []
    rec_counter = 1

    for day in range(1, 29):
        date_str = f"2026-10-{day:02d}"
        is_buffer = (day % 7 == 6) or (day % 7 == 0)

        for s in students:
            # Check if dropped out
            if s["drop"] is not None and day > s["drop"]:
                rows.append({
                    "record_id": f"REC_{rec_counter:04d}",
                    "participant_id": s["id"],
                    "day_number": day,
                    "date_str": date_str,
                    "cohort_group": s["group"],
                    "is_buffer_day": is_buffer,
                    "topics_scheduled": 0,
                    "topics_completed": 0,
                    "topics_missed": 0,
                    "actual_study_hours": 0.0,
                    "reported_stress_rating": 5,
                    "replan_occurred": False,
                    "checkin_status": "DROPPED_OFF",
                })
                rec_counter += 1
                continue

            is_adaptive = s["group"] == "A_ADAPTIVE"
            distraction = random.random() > s["grit"]
            
            topics_sched = 0 if is_buffer else 1
            topics_comp = 0
            topics_miss = 0
            replan = False

            if not is_buffer:
                if distraction:
                    topics_miss = 1
                    study_hrs = round(random.uniform(0.5, 1.2), 1)
                    stress = min(5, int(s["base_stress"] + random.uniform(1.0, 1.8)))
                    status = "MISSED"
                    if is_adaptive:
                        replan = True
                else:
                    topics_comp = 1
                    study_hrs = round(random.uniform(2.0, 2.7), 1)
                    stress = max(1, int(s["base_stress"] + random.uniform(-0.5, 0.5)))
                    status = "COMPLETED"
            else:
                # Buffer day
                study_hrs = round(random.uniform(1.0, 2.0), 1) if is_adaptive else 0.0
                stress = max(1, int(s["base_stress"] - random.uniform(0.5, 1.0)))
                status = "BUFFER_REVIEW"

            rows.append({
                "record_id": f"REC_{rec_counter:04d}",
                "participant_id": s["id"],
                "day_number": day,
                "date_str": date_str,
                "cohort_group": s["group"],
                "is_buffer_day": is_buffer,
                "topics_scheduled": topics_sched,
                "topics_completed": topics_comp,
                "topics_missed": topics_miss,
                "actual_study_hours": study_hrs,
                "reported_stress_rating": stress,
                "replan_occurred": replan,
                "checkin_status": status,
            })
            rec_counter += 1

    with open(telemetry_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} daily telemetry rows at: {telemetry_path}")


# 2. Generate simulation_cohort_raw.csv (100 Monte Carlo synthetic runs)
def generate_simulation_runs():
    sim_path = os.path.join(DATA_DIR, "simulation_cohort_raw.csv")
    random.seed(101)

    fieldnames = [
        "run_id", "cohort_group", "student_grit", "distraction_probability",
        "total_topics", "completed_topics", "missed_topics", "recovered_topics",
        "final_completion_rate", "dropout_occurred", "mean_stress"
    ]

    rows = []
    for i in range(1, 101):
        grp = "A_ADAPTIVE" if i <= 50 else "B_STATIC_CHECKLIST"
        grit = round(random.uniform(0.60, 0.95), 2)
        distract_prob = round(1.0 - grit + random.uniform(-0.05, 0.05), 2)

        total_topics = 12
        completed = 0
        missed = 0
        recovered = 0
        dropped = False
        consecutive_misses = 0
        stress_accum = []

        for d in range(1, 29):
            if dropped:
                break
            missed_today = random.random() < distract_prob
            if missed_today:
                missed += 1
                consecutive_misses += 1
                stress_accum.append(min(5.0, 2.5 + consecutive_misses * 0.5))
            else:
                consecutive_misses = max(0, consecutive_misses - 1)
                completed = min(total_topics, completed + 1)
                stress_accum.append(max(1.0, 2.0 + consecutive_misses * 0.2))

            if grp == "A_ADAPTIVE" and consecutive_misses > 0 and (d % 7 in [6, 0]):
                recovered += 1
                consecutive_misses = max(0, consecutive_misses - 1)
                completed = min(total_topics, completed + 1)

            if grp == "B_STATIC_CHECKLIST" and consecutive_misses >= 3 and d >= 14:
                if random.random() < 0.65:
                    dropped = True

        comp_rate = round((completed / total_topics) * 100.0, 1)
        mean_stress = round(sum(stress_accum) / len(stress_accum), 2) if stress_accum else 3.0

        rows.append({
            "run_id": f"SIM_{i:03d}",
            "cohort_group": grp,
            "student_grit": grit,
            "distraction_probability": distract_prob,
            "total_topics": total_topics,
            "completed_topics": completed,
            "missed_topics": missed,
            "recovered_topics": recovered,
            "final_completion_rate": min(100.0, comp_rate),
            "dropout_occurred": dropped,
            "mean_stress": mean_stress,
        })

    with open(sim_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} Monte Carlo simulation rows at: {sim_path}")


if __name__ == "__main__":
    generate_daily_telemetry()
    generate_simulation_runs()
