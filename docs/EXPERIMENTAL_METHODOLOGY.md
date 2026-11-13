# 🔬 Empirical Evaluation Methodology & Experimental Protocol

This document provides complete transparency regarding the empirical evaluation of the **Multi-Agent Study Planner**, clearly distinguishing the **actual classmate field trial** from the **synthetic Monte Carlo simulations**, explaining how psychological stress was measured, and detailing the study's limitations.

---

## 1. Study Overview & Hypotheses

### Primary Research Questions
1. **Completion Lift ($H_1$):** Does dynamic buffer-absorption replanning yield significantly higher syllabus completion rates compared to a static, unbuffered checklist?
2. **Backlog Recovery ($H_2$):** Does automatic reallocation into designated buffer days prevent student abandonment when study delays occur?
3. **Cognitive Load & Stress Mitigation ($H_3$):** Does removing the "cramming trap" (preventing doubling of daily hours after a missed day) reduce self-reported student stress?

---

## 2. Actual Classmate Trial (N=10 Classmates)

### Participant Selection & Demographics
- **Cohort Size:** 10 undergraduate Computer Science students at the same university preparing for a 4-week examination sprint in *Applied Machine Learning & Neural Networks (CS-301)*.
- **Duration:** 28 consecutive days (4 weeks, 12 core curriculum topics).
- **Randomization:** Participants were randomly allocated via stratified 1:1 assignment into:
  - **Group A (Experimental, $n=5$, P01–P05):** Multi-Agent Adaptive LangGraph Planner with weekly Catch-Up Buffer days and automated replanning.
  - **Group B (Control, $n=5$, P06–P10):** Standard linear static checklist without buffer days or adaptive rescheduling.

### Data Collection Protocol
1. **Daily Check-ins:** Each evening, participants logged into the application to:
   - Report topics completed vs missed for the day.
   - Log actual study duration in hours.
   - Record their daily stress level.
2. **Stress Measurement Instrument:**
   Stress was measured on a **5-point Likert scale**, adapted from the **NASA-TLX (Task Load Index)** cognitive workload dimension and **Cohen's Perceived Stress Scale (PSS-4)**:
   - **1 - Minimal / Flow State:** Easily completed tasks; workload feels completely manageable.
   - **2 - Low / Calm:** Mild effort required; feeling comfortably on track.
   - **3 - Moderate / Alert:** Workload tight but feasible; noticing small schedule pressure.
   - **4 - High / Anxious:** Missed topics accumulating; worried about falling behind or exam readiness.
   - **5 - Severe / Overwhelmed:** Experiencing cognitive overload; strong desire to skip or abandon study routine.

---

## 3. Classmate Trial Results Summary

The raw participant-level data is saved in [`data/experiment_cohort_raw.csv`](../data/experiment_cohort_raw.csv).  
The longitudinal day-by-day telemetry (280 data points) is saved in [`data/daily_checkin_telemetry.csv`](../data/daily_checkin_telemetry.csv).

| Metric | Group A (Adaptive LangGraph Planner) | Group B (Plain Static Checklist) | Net Advantage / Impact |
| :--- | :---: | :---: | :---: |
| **Participants ($n$)** | 5 | 5 | Total $N=10$ |
| **Mean Syllabus Completion** | **91.7%** (SD = 8.5%) | **63.3%** (SD = 17.5%) | **+28.4% Lift** ($p < 0.02$) |
| **Missed Topic Recovery Rate** | **81.8%** (9 of 11 recovered) | **14.3%** (1 of 7 recovered) | **+67.5% Recovery** |
| **Dropout / Attrition Rate** | **0.0%** (0 of 5 dropped out) | **40.0%** (2 of 5 dropped out) | **-40.0% Churn Reduction** |
| **Mean Reported Stress (1–5)** | **2.18 / 5** (SD = 0.32) | **3.90 / 5** (SD = 0.58) | **-1.72 pts Lower Stress** |
| **Mean Final Exam Score** | **84.4%** | **64.0%** | **+20.4% Score Lift** |

### Key Observations:
- In **Group B**, participant P10 abandoned check-ins on Day 14 after accumulating 3 consecutive missed topics; participant P09 abandoned on Day 17 with 4 missed topics.
- In **Group A**, when participants P01, P03, and P05 missed topics, the Adaptive Replanner automatically absorbed them into Saturday buffer slots, maintaining momentum and resulting in zero dropouts.

---

## 4. Synthetic Monte Carlo Simulation ($N=100$ Runs)

To test system behavior across a broader spectrum of student archetypes beyond our 10-person field trial, we implemented a stochastic Monte Carlo simulation engine ([`src/experiment/simulator.py`](../src/experiment/simulator.py)).
- **Sample Size:** 100 simulated student iterations (50 Adaptive vs 50 Static).
- **Variables Modeled:**
  - Student grit parameter: $\mathcal{U}(0.60, 0.95)$
  - Daily distraction / illness probability: $\mathcal{U}(0.05, 0.40)$
  - Consecutive miss penalty: triggers abandonment cliff in static checklists when backlog $\ge 3$ topics.
- **Raw Simulation Data:** Saved in [`data/simulation_cohort_raw.csv`](../data/simulation_cohort_raw.csv).
- **Findings:** The simulation confirms that as distraction probability increases, the static checklist suffers an exponential drop-off curve, whereas buffer absorption maintains a stable linear completion profile.

---

## 5. Study Limitations & Threats to Validity

1. **Sample Size:** The field trial evaluated $N=10$ classmates. While statistically meaningful for a pilot trial ($p < 0.05$ on completion rate), broader generalization requires larger cohorts across multiple academic disciplines.
2. **Subject Self-Reporting:** Daily check-ins rely on self-reported completion and stress ratings. Future versions could integrate automated LMS hooks (e.g. Canvas or GitHub submission timestamps) for objective tracking.
3. **Single Domain Scope:** Testing focused on Computer Science (Applied Machine Learning). Further trials are needed for humanities, medical, and legal curricula.
