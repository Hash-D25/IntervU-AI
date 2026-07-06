"""Local file storage unit tests."""

from pathlib import Path
from uuid import uuid4

import pytest

from app.features.resume.storage import LocalFileStorageService

MINIMAL_PDF = b"%PDF-1.4\n%%EOF"


@pytest.fixture
def storage(tmp_path: Path) -> LocalFileStorageService:
    return LocalFileStorageService(str(tmp_path))


async def test_save_creates_unique_paths(storage: LocalFileStorageService) -> None:
    user_id = uuid4()
    first = await storage.save(user_id=user_id, content=MINIMAL_PDF)
    second = await storage.save(user_id=user_id, content=MINIMAL_PDF)

    assert first.key != second.key
    assert first.key.startswith(f"resumes/{user_id}/")
    assert first.key.endswith(".pdf")
    assert first.url is None


async def test_delete_removes_file(storage: LocalFileStorageService) -> None:
    user_id = uuid4()
    stored = await storage.save(user_id=user_id, content=MINIMAL_PDF)

    await storage.delete(stored.key)

    absolute = storage._root / stored.key
    assert not absolute.is_file()
