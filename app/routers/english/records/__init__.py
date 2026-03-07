from __future__ import annotations

from fastapi import APIRouter

from app.routers.english.records import (
    acquisition,
    learner_proficiency,
    needs_analysis,
    practice,
    task_outcome,
    writing_assessment,
)

router = APIRouter(prefix="/records")

router.include_router(acquisition.router)
router.include_router(practice.router)
router.include_router(writing_assessment.router)
router.include_router(task_outcome.router)
router.include_router(needs_analysis.router)
router.include_router(learner_proficiency.router)
