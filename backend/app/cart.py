from __future__ import annotations

from datetime import datetime
from typing import Any

from .database import get_collection


async def get_user_cart(username: str) -> list[dict[str, Any]]:
    collection = get_collection("carts")
    cart = await collection.find_one({"username": username})
    return cart.get("books", []) if cart else []


async def add_to_cart(username: str, book: dict[str, Any]) -> bool:
    """Add book to cart only if not already present (no duplicates)."""
    collection = get_collection("carts")
    existing = await collection.find_one(
        {"username": username, "books.title": book["title"]}
    )
    if existing:
        return False
    result = await collection.update_one(
        {"username": username},
        {
            "$push": {
                "books": {
                    "title": book["title"],
                    "author": book["author"],
                    "genre": book["genre"],
                    "rating": book["rating"],
                    "added_at": datetime.utcnow().isoformat(),
                }
            },
            "$setOnInsert": {"username": username},
        },
        upsert=True,
    )
    return result.modified_count > 0 or result.upserted_id is not None


async def remove_from_cart(username: str, book_title: str) -> bool:
    collection = get_collection("carts")
    result = await collection.update_one(
        {"username": username},
        {"$pull": {"books": {"title": book_title}}},
    )
    return result.modified_count > 0


async def clear_cart(username: str) -> bool:
    collection = get_collection("carts")
    result = await collection.delete_one({"username": username})
    return result.deleted_count > 0


async def mark_as_read(username: str, book: dict[str, Any]) -> bool:
    collection = get_collection("read_books")
    existing = await collection.find_one(
        {"username": username, "books.title": book["title"]}
    )
    if existing:
        return False
    result = await collection.update_one(
        {"username": username},
        {
            "$push": {
                "books": {
                    "title": book["title"],
                    "author": book["author"],
                    "genre": book["genre"],
                    "rating": book["rating"],
                    "read_at": datetime.utcnow().isoformat(),
                }
            },
            "$setOnInsert": {"username": username},
        },
        upsert=True,
    )
    return result.modified_count > 0 or result.upserted_id is not None


async def get_read_books(username: str) -> list[dict[str, Any]]:
    collection = get_collection("read_books")
    record = await collection.find_one({"username": username})
    return record.get("books", []) if record else []


# ── Likes ─────────────────────────────────────────────────────────────────────

async def like_book(username: str, book: dict[str, Any]) -> bool:
    """Toggle like on a book. Returns True if liked, False if unliked."""
    collection = get_collection("likes")
    existing = await collection.find_one(
        {"username": username, "books.title": book["title"]}
    )
    if existing:
        await collection.update_one(
            {"username": username},
            {"$pull": {"books": {"title": book["title"]}}},
        )
        return False
    await collection.update_one(
        {"username": username},
        {
            "$push": {
                "books": {
                    "title": book["title"],
                    "author": book["author"],
                    "genre": book["genre"],
                    "rating": book["rating"],
                    "liked_at": datetime.utcnow().isoformat(),
                }
            },
            "$setOnInsert": {"username": username},
        },
        upsert=True,
    )
    return True


async def get_liked_books(username: str) -> list[dict[str, Any]]:
    collection = get_collection("likes")
    record = await collection.find_one({"username": username})
    return record.get("books", []) if record else []


async def get_liked_genres(username: str) -> dict[str, int]:
    """Return genre -> count map derived from liked books only."""
    books = await get_liked_books(username)
    genres: dict[str, int] = {}
    for book in books:
        g = book.get("genre", "")
        if g:
            genres[g] = genres.get(g, 0) + 1
    return genres
