"""FSRS spaced-repetition wrapper using Cambridge Assessment terminology."""

from __future__ import annotations

import json
from datetime import datetime

from fsrs import Card, Rating, Scheduler


def initialise_item_state() -> str:
    """Return initial item state as JSON for a new practice item."""
    return Card().to_json()


def _scheduler_from_model_weights(model_weights_json: str | None) -> Scheduler:
    if model_weights_json is None:
        return Scheduler()
    weights = json.loads(model_weights_json)
    return Scheduler(parameters=tuple(weights))


def schedule_review(
    item_state_json: str,
    attempt_quality: int,
    model_weights_json: str | None = None,
) -> tuple[str, datetime, float, float, float | None]:
    """Compute next practice date from attempt quality (1=Again..4=Easy).

    Returns:
        (item_state_json, due_date, memory_stability, item_difficulty, retrievability)
    """
    card = Card.from_json(item_state_json)
    rating = Rating(attempt_quality)
    scheduler = _scheduler_from_model_weights(model_weights_json)
    card, _ = scheduler.review_card(card, rating)
    retrievability = scheduler.get_card_retrievability(card)
    memory_stability = card.stability if card.stability is not None else 0.0
    item_difficulty = card.difficulty if card.difficulty is not None else 0.0
    return (
        card.to_json(),
        card.due,
        memory_stability,
        item_difficulty,
        retrievability,
    )


def estimate_retrievability(
    item_state_json: str,
    model_weights_json: str | None = None,
) -> float:
    """Return current recall probability (0~1) for the item."""
    card = Card.from_json(item_state_json)
    scheduler = _scheduler_from_model_weights(model_weights_json)
    return scheduler.get_card_retrievability(card)


def build_scheduler(model_weights_json: str) -> Scheduler:
    """Build scheduler from learner model weights (JSON array of floats)."""
    return _scheduler_from_model_weights(model_weights_json)
