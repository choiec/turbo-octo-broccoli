from __future__ import annotations

from fastapi import APIRouter

from app.routers.english import inventory, records

router = APIRouter(prefix="/english")

router.include_router(records.router)
router.include_router(inventory.router)
