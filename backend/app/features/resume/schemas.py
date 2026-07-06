"""Resume request/response DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    original_filename: str
    stored_path: str
    file_url: str | None = None
    file_size_bytes: int
    content_type: str
    created_at: datetime
