from __future__ import annotations

import logging
import os

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "bookbug"

_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None

logger = logging.getLogger(__name__)


async def connect_to_mongo() -> None:
    global _client, _database
    try:
        _client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        # Ping to verify connection is actually reachable
        await _client.admin.command("ping")
        _database = _client[DATABASE_NAME]
        logger.info("Connected to MongoDB at %s", MONGODB_URL)
    except Exception as exc:
        logger.warning("MongoDB unavailable (%s) – running in file-fallback mode", exc)
        _client = None
        _database = None


async def close_mongo_connection() -> None:
    global _client
    if _client:
        _client.close()
        _client = None


def get_database() -> AsyncIOMotorDatabase | None:
    """Return the database handle, or None when running without MongoDB."""
    return _database


def get_collection(name: str):
    db = get_database()
    if db is None:
        raise RuntimeError("MongoDB is not available")
    return db[name]


def is_mongo_available() -> bool:
    return _database is not None
