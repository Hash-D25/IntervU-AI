"""Resume parsing service unit tests."""

import httpx
import pytest
from openai import RateLimitError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.exceptions import ParseError
from app.db.registry import Base
from app.features.resume.models import Resume
from app.features.resume.parsed_repository import ResumeParsedProfileRepository
from app.features.resume.parsing.schemas import ParsedResume
from app.features.resume.parsing.service import ResumeParsingService
from app.features.resume.repository import ResumeRepository
from app.features.user.models import User
from app.features.user.repository import UserRepository


class _FailingParser:
    name = "fake"

    async def parse(
        self,
        pdf_bytes: bytes,
        *,
        on_progress: object = None,
    ) -> ParsedResume:
        request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
        response = httpx.Response(429, request=request)
        raise RateLimitError(
            "quota exceeded",
            response=response,
            body={"error": {"message": "insufficient_quota"}},
        )


class _FakeStorage:
    async def fetch(self, storage_key: str) -> bytes:
        return b"%PDF-1.4\nsample"


@pytest.fixture
async def session() -> AsyncSession:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db_session:
        user = await UserRepository(db_session).add(
            User(email="parse-fail@example.com", full_name="Fail User", hashed_password="x")
        )
        resume = await ResumeRepository(db_session).add(
            Resume(
                user_id=user.id,
                original_filename="resume.pdf",
                stored_path="resumes/test/resume.pdf",
                file_size_bytes=10,
                content_type="application/pdf",
            )
        )
        await db_session.commit()
        db_session.info["resume_id"] = resume.id
        db_session.info["user_id"] = user.id
        yield db_session
    await engine.dispose()


async def test_parse_records_failure_without_crashing(session: AsyncSession) -> None:
    resume_id = session.info["resume_id"]
    user_id = session.info["user_id"]
    service = ResumeParsingService(
        session,
        ResumeRepository(session),
        ResumeParsedProfileRepository(session),
        _FakeStorage(),
        _FailingParser(),
    )

    with pytest.raises(ParseError, match="LLM quota exceeded"):
        await service.parse(resume_id, user_id)

    profile = await ResumeParsedProfileRepository(session).get_by_resume_id(resume_id)
    assert profile is not None
    assert profile.parse_status == "failed"
    assert "quota" in (profile.parse_error or "").lower()
