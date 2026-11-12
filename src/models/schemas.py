from datetime import date, datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class Topic(BaseModel):
    id: str = Field(..., description="Unique identifier, e.g. T1, T2")
    module_id: str = Field(..., description="Parent module identifier, e.g. M1")
    title: str = Field(..., description="Title of the topic")
    description: str = Field("", description="Summary of key concepts covered")
    estimated_hours: float = Field(2.0, description="Estimated study duration in hours")
    difficulty: int = Field(3, ge=1, le=5, description="Difficulty rating from 1 (easy) to 5 (advanced)")
    prerequisites: List[str] = Field(default_factory=list, description="IDs of precursor topics")
    priority: Literal["core", "elective", "review"] = Field("core", description="Importance category")


class Module(BaseModel):
    id: str = Field(..., description="Module identifier, e.g. M1")
    title: str = Field(..., description="Module title")
    description: str = Field("", description="Module description")
    order: int = Field(1, description="Sequence order in course")
    topics: List[Topic] = Field(default_factory=list, description="Topics within this module")


class Syllabus(BaseModel):
    course_code: str = Field("CS-101", description="Course code or identifier")
    course_name: str = Field(..., description="Full course title")
    description: str = Field("", description="Course summary")
    total_weeks: int = Field(4, ge=1, le=52, description="Target course duration in weeks")
    exam_date: Optional[str] = Field(None, description="Target completion or exam date YYYY-MM-DD")
    modules: List[Module] = Field(default_factory=list, description="Ordered course modules")

    @property
    def all_topics(self) -> List[Topic]:
        topics = []
        for mod in self.modules:
            topics.extend(mod.topics)
        return topics


class StudentProfile(BaseModel):
    student_id: str = Field("student_01", description="Unique student ID")
    name: str = Field("Classmate", description="Student display name")
    daily_available_hours: float = Field(2.5, ge=0.5, le=12.0, description="Available study hours per study day")
    study_days_per_week: int = Field(6, ge=1, le=7, description="Number of active study days per week")
    start_date: str = Field(default_factory=lambda: date.today().isoformat(), description="Study start date YYYY-MM-DD")
    target_weeks: int = Field(4, ge=1, le=12, description="Target duration in weeks")
    cohort_group: Literal["A_ADAPTIVE", "B_STATIC_CHECKLIST"] = Field(
        "A_ADAPTIVE", description="Experimental group (Adaptive Planner) vs Control (Plain Checklist)"
    )


class DaySchedule(BaseModel):
    day_number: int = Field(..., description="Sequential day in course, e.g. Day 1")
    date_str: str = Field(..., description="Calendar date YYYY-MM-DD")
    day_name: str = Field("Monday", description="Day of week")
    allocated_topics: List[Topic] = Field(default_factory=list, description="Topics scheduled for this day")
    planned_hours: float = Field(0.0, description="Sum of planned hours for allocated topics")
    is_buffer_day: bool = Field(False, description="True if reserved for catch-up, review, and buffer")
    status: Literal["pending", "completed", "partial", "missed"] = Field("pending", description="Execution status")
    notes: str = Field("", description="Notes or reminder instructions")


class WeekSchedule(BaseModel):
    week_number: int = Field(..., description="Week sequence 1..N")
    start_date: str = Field(..., description="Week start date")
    end_date: str = Field(..., description="Week end date")
    days: List[DaySchedule] = Field(default_factory=list, description="7-day schedule")
    buffer_hours_reserved: float = Field(2.0, description="Dedicated buffer hours in this week")
    theme: str = Field("", description="Weekly learning objective or theme")


class StudyPlan(BaseModel):
    plan_id: str = Field(..., description="Plan identifier")
    student_id: str = Field(..., description="Target student")
    course_name: str = Field(..., description="Target course")
    weeks: List[WeekSchedule] = Field(default_factory=list, description="Weekly breakdown")
    version: int = Field(1, description="Plan iteration version number (increments on replan)")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class CheckInRecord(BaseModel):
    checkin_id: str = Field(..., description="Check-in identifier")
    student_id: str = Field(..., description="Student identifier")
    date: str = Field(..., description="Date of check-in YYYY-MM-DD")
    day_number: int = Field(..., description="Course day number being reported")
    completed_topic_ids: List[str] = Field(default_factory=list, description="Topic IDs completed")
    missed_topic_ids: List[str] = Field(default_factory=list, description="Topic IDs scheduled but missed")
    actual_hours_spent: float = Field(0.0, description="Actual study time in hours")
    perceived_difficulty: int = Field(3, ge=1, le=5, description="1 (Very easy) to 5 (Very hard)")
    student_notes: str = Field("", description="Student feedback / explanation for missed topics")
    stress_rating: int = Field(2, ge=1, le=5, description="Reported stress/overwhelm 1 (relaxed) to 5 (overwhelmed)")


class ReplanEvent(BaseModel):
    event_id: str = Field(..., description="Event unique ID")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    trigger_day: int = Field(..., description="Day number where replan was triggered")
    missed_topic_ids: List[str] = Field(default_factory=list)
    rescheduled_to_dates: Dict[str, str] = Field(default_factory=dict, description="topic_id -> new_date_str")
    strategy_used: str = Field("", description="E.g., 'Buffer Absorption', 'Weekend Redistribution', 'Pacing Extension'")
    explanation: str = Field("", description="Student-facing explanation of schedule changes")


class StaticChecklistItem(BaseModel):
    topic_id: str
    title: str
    module_title: str
    assigned_week: int
    estimated_hours: float
    completed: bool = False
    completed_on_date: Optional[str] = None


class StaticChecklist(BaseModel):
    student_id: str
    course_name: str
    items: List[StaticChecklistItem] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ExperimentCohortMember(BaseModel):
    student_id: str
    name: str
    cohort_group: Literal["A_ADAPTIVE", "B_STATIC_CHECKLIST"]
    start_date: str
    is_active: bool = True
    checkin_count: int = 0
    total_assigned_topics: int = 0
    completed_topics_count: int = 0
    missed_topics_count: int = 0
    recovered_topics_count: int = 0
    drop_off_day: Optional[int] = None
    average_stress: float = 2.5
    final_completion_rate: float = 0.0
