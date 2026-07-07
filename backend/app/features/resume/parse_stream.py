"""Server-sent events stream for resume parsing progress."""

import asyncio
import json
from collections.abc import AsyncIterator
from uuid import UUID

from app.core.exceptions import AppError
from app.features.resume.parsed_mapper import to_parsed_profile_response
from app.features.resume.parsing.service import ResumeParsingService


async def stream_parse_events(
    service: ResumeParsingService,
    resume_id: UUID,
    user_id: UUID,
) -> AsyncIterator[str]:
    queue: asyncio.Queue[dict[str, object] | None] = asyncio.Queue()

    async def on_progress(stage: str, percent: int, message: str) -> None:
        await queue.put({"stage": stage, "percent": percent, "message": message})

    async def run_parse() -> None:
        try:
            profile = await service.parse(resume_id, user_id, on_progress=on_progress)
            response = to_parsed_profile_response(profile)
            await queue.put(
                {
                    "stage": "done",
                    "percent": 100,
                    "message": "Parse complete",
                    "result": response.model_dump(mode="json"),
                }
            )
        except AppError as exc:
            await queue.put({"stage": "error", "percent": 0, "message": exc.message})
        except Exception as exc:
            await queue.put({"stage": "error", "percent": 0, "message": str(exc)})
        finally:
            await queue.put(None)

    task = asyncio.create_task(run_parse())
    try:
        while True:
            event = await queue.get()
            if event is None:
                break
            yield f"data: {json.dumps(event)}\n\n"
    finally:
        await task
