"""
Explainable AI module for BookBug.
Returns short, friendly insights about how the platform works.
"""
from __future__ import annotations

import random

_INSIGHTS: list[str] = [
    "Did you know? BookBug automatically verifies every update before it reaches you, "
    "keeping the platform reliable and stable.",

    "Did you know? The platform packages the application in a consistent container so it "
    "behaves exactly the same whether running locally or in the cloud.",

    "Did you know? Automated checks run on every code change to make sure new features "
    "never break existing functionality.",

    "Did you know? Your reading list is stored in a database so it persists across "
    "sessions — close the tab and your books are still waiting for you.",

    "Did you know? BookBug learns your favourite genres from the books you ♥ like, "
    "not just the ones you browse.",

    "Did you know? The recommendation engine shuffles results each session so you always "
    "discover something new, even in a genre you've visited before.",

    "Did you know? Infrastructure as Code means the entire server environment can be "
    "recreated from a single command — no manual setup required.",

    "Did you know? The CI/CD pipeline means a developer's change goes from laptop to "
    "live platform in minutes, fully tested and containerised.",

    "Did you know? BookBug uses health checks so the system automatically restarts "
    "if a service ever becomes unresponsive.",

    "Did you know? Your recommendation history is kept private — each user's journey "
    "is stored separately and never shared.",
]


def get_random_insight() -> str:
    """Return one randomly selected insight string."""
    return random.choice(_INSIGHTS)
