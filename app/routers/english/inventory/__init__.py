from __future__ import annotations

from fastapi import APIRouter

from app.routers.english.inventory import grammar, lexis, vocab_list

router = APIRouter(prefix="/inventory")

router.include_router(grammar.router)
router.include_router(lexis.router)
router.include_router(vocab_list.router)
