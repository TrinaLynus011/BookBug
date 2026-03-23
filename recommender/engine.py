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

    def genres(self) -> list[str]:
        return sorted(self._by_genre.keys())

    def random_genre(self) -> str:
        return self._rng.choice(self.genres())

    def recommend(self, genre: str, count: int = 5) -> list[BookRecord]:
        books = self._by_genre.get(genre.lower(), [])
        if not books:
            return []

        # Score favors highly rated books while keeping randomness for diversity.
        scores = [self._score(book) for book in books]
        selected: list[BookRecord] = []
        seen_titles: set[str] = set()

        attempts = 0
        target = min(max(count, 3), 5)
        while len(selected) < target and attempts < 100:
            attempts += 1
            candidate = self._weighted_choice(books, scores)
            if candidate.title in seen_titles:
                continue
            selected.append(candidate)
            seen_titles.add(candidate.title)

        return selected

    def _score(self, book: BookRecord) -> float:
        base = max(book.rating, 0.1)
        exploration = self._rng.uniform(0.85, 1.2)
        return round(base * exploration, 4)

    def _weighted_choice(self, books: list[BookRecord], scores: list[float]) -> BookRecord:
        return self._rng.choices(books, weights=scores, k=1)[0]

    @staticmethod
    def _load_books(dataset_path: Path) -> list[BookRecord]:
        with dataset_path.open("r", encoding="utf-8") as f:
            raw_books = json.load(f)

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
