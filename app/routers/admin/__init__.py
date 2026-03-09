from __future__ import annotations

from fastapi import APIRouter

from app.routers.admin import upload

router = APIRouter(prefix="/admin")

router.include_router(upload.router, prefix="/upload", tags=["admin"])
