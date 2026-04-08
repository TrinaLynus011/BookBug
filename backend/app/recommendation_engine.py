from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BookRecord:
    title: str
    author: str
    genre: str
    rating: float


class RecommendationEngine:
    def __init__(self, dataset_path: Path, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._books = self._load_books(dataset_path)
        self._by_genre = self._group_by_genre(self._books)
        self._session_history: dict[str, dict[str, set[str]]] = {}

    def genres(self) -> list[str]:
        return sorted(self._by_genre.keys())

    def random_genre(self) -> str:
        return self._rng.choice(self.genres())

    def recommend(
        self,
        genre: str,
        count: int = 5,
        session_key: str = "public",
        user_preferences: dict[str, int] | None = None,
    ) -> list[BookRecord]:
        normalized = genre.lower()
        books = self._by_genre.get(normalized, []).copy()

        if not books:
            return []

        session_map = self._session_history.setdefault(session_key, {})
        history = session_map.get(normalized, set())

        books = [book for book in books if book.title not in history]
        if not books:
            session_map[normalized] = set()
            books = self._by_genre.get(normalized, []).copy()

        self._rng.shuffle(books)
        scores = [self._score(book, user_preferences) for book in books]

        selected: list[BookRecord] = []
        seen_titles: set[str] = set()
        target = min(max(count, 3), 5)

        while len(selected) < target and books:
            candidate = self._weighted_choice(books, scores)
            index = books.index(candidate)

            if candidate.title not in seen_titles:
                selected.append(candidate)
                seen_titles.add(candidate.title)

            books.pop(index)
            scores.pop(index)

        session_map[normalized] = history.union({book.title for book in selected})
        return selected

    def _score(
        self,
        book: BookRecord,
        user_preferences: dict[str, int] | None = None,
    ) -> float:
        base = book.rating
        random_factor = self._rng.uniform(0.7, 1.5)
        novelty_factor = self._rng.uniform(0.9, 1.3)

        score = base * random_factor * novelty_factor

        if user_preferences and book.genre in user_preferences:
            preference_boost = 1.0 + (user_preferences[book.genre] * 0.05)
            score *= min(preference_boost, 1.5)

        return score

    def _weighted_choice(self, books: list[BookRecord], scores: list[float]) -> BookRecord:
        return self._rng.choices(books, weights=scores, k=1)[0]

    @staticmethod
    def _load_books(dataset_path: Path) -> list[BookRecord]:
        with dataset_path.open("r", encoding="utf-8") as file:
            raw_books = json.load(file)

        return [
            BookRecord(
                title=str(item["title"]),
                author=str(item["author"]),
                genre=str(item["genre"]).lower(),
                rating=float(item["rating"]),
            )
            for item in raw_books
        ]

    @staticmethod
    def _group_by_genre(books: list[BookRecord]) -> dict[str, list[BookRecord]]:
        grouped: dict[str, list[BookRecord]] = {}
        for book in books:
            grouped.setdefault(book.genre, []).append(book)
        return grouped
