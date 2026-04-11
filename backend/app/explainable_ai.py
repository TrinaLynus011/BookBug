"""
Explainable AI module for BookBug.
Generates short, personalized, context-aware explanations.
No "Did you know?" — every message feels like the system understands the user.
"""
from __future__ import annotations

import random


# ── Personalized recommendation explanations ─────────────────────────────────
# Keyed by (has_genre, has_book) tuple for template selection.

_GENRE_BOOK_TEMPLATES = [
    (
        "You're seeing {book} because your recent activity leans toward {genre}. "
        "The engine adapts in real time through a continuously deployed backend, "
        "so your shelf stays relevant as your taste evolves."
    ),
    (
        "{book} surfaced because {genre} keeps showing up in your reading pattern. "
        "Recommendations are recalculated on every session using a live backend — "
        "nothing here is static."
    ),
    (
        "Your interest in {genre} is what brought {book} to the top. "
        "The platform deploys updates automatically, so the logic behind this "
        "suggestion is always current."
    ),
]

_GENRE_ONLY_TEMPLATES = [
    (
        "You're exploring {genre} — the system noticed and is weighting similar titles higher. "
        "A containerised backend processes this in real time, so the shelf shifts as you do."
    ),
    (
        "Your recent sessions show a pull toward {genre}. "
        "The recommendation engine runs on a scalable backend that updates continuously, "
        "keeping suggestions aligned with where your reading is heading."
    ),
    (
        "Since you've been spending time in {genre}, the engine is surfacing more of it. "
        "Every interaction quietly refines what you see next — no manual tuning needed."
    ),
]

_BOOK_ONLY_TEMPLATES = [
    (
        "{book} appeared because it matches the reading pattern the system has built for you. "
        "The backend is always on, deployed through an automated pipeline that keeps "
        "recommendations fresh without any downtime."
    ),
    (
        "The system flagged {book} as a strong match based on your recent choices. "
        "It runs through a CI/CD pipeline, so the logic behind this is tested and "
        "updated continuously."
    ),
]

_LIKED_TEMPLATES = [
    (
        "Your likes are shaping this. The engine weighs {genre} more heavily "
        "because you've been hearting titles in that space. "
        "Those signals feed directly into what surfaces next."
    ),
    (
        "The books you've liked are quietly steering the shelf. "
        "Favouriting a title tells the system something real — "
        "it adjusts your recommendations without you having to ask."
    ),
]

_READING_LIST_TEMPLATES = [
    (
        "Your reading list is stored in a persistent database, not just your browser. "
        "Close the tab, switch devices — it'll still be there when you come back."
    ),
    (
        "Everything you save to your reading list lives in the backend, "
        "so it survives refreshes, restarts, and new sessions. "
        "The system keeps it safe automatically."
    ),
]

_HISTORY_TEMPLATES = [
    (
        "Your history is private and isolated — no other user can see it. "
        "The backend stores each person's journey separately, "
        "so your reading path is entirely your own."
    ),
    (
        "The system remembers your sessions so it can serve better suggestions over time. "
        "That history lives in a secure database, updated in real time as you explore."
    ),
]

_FALLBACK_TEMPLATES = [
    (
        "The platform is running a continuously deployed backend, "
        "so what you see here is always up to date. "
        "Every change goes through automated testing before it reaches you."
    ),
    (
        "BookBug runs inside containers, which means it behaves the same "
        "whether it's on a developer's laptop or a production server. "
        "Consistency is built in, not bolted on."
    ),
    (
        "The system scales automatically based on how many people are using it. "
        "You'll never notice the infrastructure — that's the point."
    ),
    (
        "Automated health checks run in the background constantly. "
        "If anything drifts, the system corrects itself before you'd ever notice."
    ),
]


def _pick(templates: list[str], **kwargs) -> str:
    return random.choice(templates).format(**kwargs)


def get_personalized_insight(
    feature: str | None = None,
    book_title: str | None = None,
    liked_genres: list[str] | None = None,
    current_genre: str | None = None,
) -> str:
    """
    Return a short, personalized, context-aware explanation.

    Priority:
      1. feature-specific (reading_list, history, liked)
      2. genre + book together
      3. genre only
      4. book only
      5. fallback
    """
    genre_str = current_genre or (liked_genres[0] if liked_genres else None)
    book_str  = f'"{book_title}"' if book_title else None

    # Feature-specific overrides
    if feature == "reading_list":
        return _pick(_READING_LIST_TEMPLATES)

    if feature == "history":
        return _pick(_HISTORY_TEMPLATES)

    if feature == "liked" and genre_str:
        return _pick(_LIKED_TEMPLATES, genre=genre_str)

    # Context-driven
    if genre_str and book_str:
        return _pick(_GENRE_BOOK_TEMPLATES, genre=genre_str, book=book_str)

    if genre_str:
        return _pick(_GENRE_ONLY_TEMPLATES, genre=genre_str)

    if book_str:
        return _pick(_BOOK_ONLY_TEMPLATES, book=book_str)

    return _pick(_FALLBACK_TEMPLATES)


# Keep the old name as an alias so existing callers don't break
def get_random_insight() -> str:
    return get_personalized_insight()
