"""Version 1 router. Feature routers are mounted here as they are built."""

from fastapi import APIRouter

from app.api.v1 import health
from app.features.auth import router as auth_router
from app.features.resume import router as resume_router

v1_router = APIRouter()
v1_router.include_router(health.router, tags=["health"])
v1_router.include_router(auth_router.router)
v1_router.include_router(resume_router.router)
