"""Version 1 router. Feature routers are mounted here as they are built."""

from fastapi import APIRouter

from app.api.v1 import health
from app.features.auth import router as auth_router
from app.features.feedback import router as feedback_router
from app.features.interview import router as interview_router
from app.features.job_description import router as job_description_router
from app.features.resume import router as resume_router
from app.features.voice import router as voice_router

v1_router = APIRouter()
v1_router.include_router(health.router, tags=["health"])
v1_router.include_router(auth_router.router)
v1_router.include_router(resume_router.router)
v1_router.include_router(job_description_router.router)
v1_router.include_router(interview_router.router)
v1_router.include_router(feedback_router.router)
v1_router.include_router(voice_router.router)
