"""Select an interview planner strategy."""

from app.features.interview.planning.protocols import InterviewPlanner
from app.features.interview.planning.strategies.resume_based_planner import (
    ResumeBasedInterviewPlanner,
)


def create_interview_planner() -> InterviewPlanner:
    return ResumeBasedInterviewPlanner()
