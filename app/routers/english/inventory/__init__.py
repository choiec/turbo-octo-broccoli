from __future__ import annotations

from fastapi import APIRouter

from app.routers.english.inventory import grammar, lexis

router = APIRouter(prefix="/inventory")

router.include_router(grammar.router)
router.include_router(lexis.router)
