"""Version 1 router. Feature routers are mounted here as they are built."""

from fastapi import APIRouter

from app.api.v1 import health

v1_router = APIRouter()
v1_router.include_router(health.router, tags=["health"])
