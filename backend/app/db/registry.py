"""Single import point that registers every ORM model on ``Base.metadata``.

Import this module (rather than individual model modules) wherever the full
schema must be known — Alembic autogenerate and test table creation. Importing a
model class has the side effect of registering its table.
"""

from app.db.base import Base
from app.features.feedback.models import FeedbackReport
from app.features.interview.models import Answer, Interview, Question
from app.features.user.models import User

__all__ = [
    "Answer",
    "Base",
    "FeedbackReport",
    "Interview",
    "Question",
    "User",
]
