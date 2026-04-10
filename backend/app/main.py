from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pythonjsonlogger.json import JsonFormatter

from .auth import create_access_token, decode_access_token, hash_password, verify_password
from .cart import (
    add_to_cart,
    clear_cart,
    get_liked_books,
    get_liked_genres,
    get_read_books,
    get_user_cart,
    like_book,
    mark_as_read,
    remove_from_cart,
)
from .database import close_mongo_connection, connect_to_mongo, get_collection, is_mongo_available
from .explainable_ai import get_random_insight
from .recommendation_engine import RecommendationEngine
from .schemas import (
    Book,
    BookRequest,
    CartResponse,
    GenreResponse,
    HistoryRecord,
    HistoryResponse,
    LikeResponse,
    ReadBooksResponse,
    RecommendationResponse,
    TokenResponse,
    UserLogin,
    UserSignup,
)

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_PATH = BASE_DIR / "dataset" / "books.json"
USERS_PATH = Path(__file__).resolve().parent / "users.json"
HISTORY_PATH = Path(__file__).resolve().parent / "history.json"

REQUEST_COUNT = Counter("bookbug_http_requests_total", "Total HTTP requests", ["endpoint"])
REQUEST_LATENCY = Histogram("bookbug_request_latency_seconds", "Latency by endpoint", ["endpoint"])


def configure_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.handlers = [handler]


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


configure_logging()
app = FastAPI(title="BookBug API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
engine = RecommendationEngine(DATASET_PATH)


# ── User storage helpers (MongoDB-first, JSON fallback) ───────────────────────

async def _get_user(username: str) -> dict | None:
    if is_mongo_available():
        return await get_collection("users").find_one({"username": username}, {"_id": 0})
    # File fallback
    users = _read_users_file()
    return next((u for u in users if u.get("username") == username), None)


async def _create_user(username: str, hashed_password: str) -> None:
    if is_mongo_available():
        await get_collection("users").insert_one(
            {"username": username, "password": hashed_password}
        )
        return
    # File fallback
    users = _read_users_file()
    users.append({"username": username, "password": hashed_password})
    _write_users_file(users)


def _read_users_file() -> list[dict]:
    if not USERS_PATH.exists():
        USERS_PATH.write_text("[]", encoding="utf-8")
    with USERS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return [item for item in data if isinstance(item, dict)]


def _write_users_file(users: list[dict]) -> None:
    with USERS_PATH.open("w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


# ── History storage helpers (MongoDB-first, JSON fallback) ────────────────────

async def _get_user_history(username: str) -> dict:
    """Return the history document for a specific user."""
    if is_mongo_available():
        doc = await get_collection("history").find_one({"username": username}, {"_id": 0})
        if doc:
            return doc
        return {"username": username, "history": [], "preferences": {"genres": {}, "books": []}}
    # File fallback – keyed by username
    all_history = _read_history_file()
    return all_history.get(
        username,
        {"history": [], "preferences": {"genres": {}, "books": []}},
    )


async def _save_user_history(username: str, user_data: dict) -> None:
    if is_mongo_available():
        await get_collection("history").update_one(
            {"username": username},
            {"$set": user_data},
            upsert=True,
        )
        return
    # File fallback
    all_history = _read_history_file()
    all_history[username] = user_data
    _write_history_file(all_history)


def _read_history_file() -> dict:
    if not HISTORY_PATH.exists():
        HISTORY_PATH.write_text("{}", encoding="utf-8")
    with HISTORY_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_history_file(data: dict) -> None:
    with HISTORY_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


async def _add_to_history(username: str, record: HistoryRecord) -> None:
    user_data = await _get_user_history(username)

    user_history = user_data.get("history", [])
    user_history.insert(0, record.model_dump())
    user_data["history"] = user_history[:20]

    genres = user_data.get("preferences", {}).get("genres", {})
    genres[record.genre] = genres.get(record.genre, 0) + 1
    user_data.setdefault("preferences", {})["genres"] = genres

    books = user_data["preferences"].get("books", [])
    for book in record.books:
        if book.title not in books:
            books.append(book.title)
    user_data["preferences"]["books"] = books[:50]

    await _save_user_history(username, user_data)


# ── Token helper ──────────────────────────────────────────────────────────────

def _extract_bearer_subject(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    try:
        return decode_access_token(token)
    except ValueError:
        return None


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health() -> dict[str, str]:
    REQUEST_COUNT.labels(endpoint="health").inc()
    return {"status": "ok"}


@app.get("/insight")
def insight() -> dict[str, str]:
    """Return a random Explainable AI insight about the platform."""
    return {"insight": get_random_insight()}


@app.get("/metrics")
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/genre", response_model=GenreResponse)
def genre() -> GenreResponse:
    with REQUEST_LATENCY.labels(endpoint="genre").time():
        REQUEST_COUNT.labels(endpoint="genre").inc()
        return GenreResponse(genre=engine.random_genre())


@app.get("/recommend/{genre}", response_model=RecommendationResponse)
async def recommend(
    genre: str,
    authorization: str | None = Header(default=None),
) -> RecommendationResponse:
    with REQUEST_LATENCY.labels(endpoint="recommend").time():
        REQUEST_COUNT.labels(endpoint="recommend").inc()
        normalized = genre.lower()
        if normalized not in engine.genres():
            raise HTTPException(status_code=404, detail=f"Genre '{genre}' not found")

        username = _extract_bearer_subject(authorization)
        session_key = username or "public"

        user_preferences = None
        if username:
            user_data = await _get_user_history(username)
            user_preferences = user_data.get("preferences", {}).get("genres", {})

        recommendations = engine.recommend(
            normalized, session_key=session_key, user_preferences=user_preferences
        )
        books = [Book.model_validate(book.__dict__) for book in recommendations]
        record = HistoryRecord(genre=normalized, books=books)

        if username:
            await _add_to_history(username, record)

        return RecommendationResponse(genre=normalized, books=books)


@app.get("/history", response_model=HistoryResponse)
async def get_history(authorization: str | None = Header(default=None)) -> HistoryResponse:
    REQUEST_COUNT.labels(endpoint="history").inc()
    username = _extract_bearer_subject(authorization)

    if not username:
        return HistoryResponse(history=[])

    user_data = await _get_user_history(username)
    records = [HistoryRecord(**item) for item in user_data.get("history", [])]
    return HistoryResponse(history=records)


@app.post("/signup")
async def signup(payload: UserSignup) -> dict[str, str]:
    REQUEST_COUNT.labels(endpoint="signup").inc()
    username = payload.username.strip()
    if not username or not payload.password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    existing = await _get_user(username)
    if existing is not None:
        raise HTTPException(status_code=400, detail="Username already exists")

    await _create_user(username, hash_password(payload.password))
    return {"message": "User created successfully"}


@app.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin) -> TokenResponse:
    REQUEST_COUNT.labels(endpoint="login").inc()
    username = payload.username.strip()

    user = await _get_user(username)
    if user is None or not verify_password(payload.password, user.get("password", "")):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(subject=username)
    return TokenResponse(access_token=token, token_type="bearer")


@app.get("/dashboard/{username}")
async def dashboard(
    username: str, authorization: str | None = Header(default=None)
) -> dict[str, object]:
    REQUEST_COUNT.labels(endpoint="dashboard").inc()
    token_user = _extract_bearer_subject(authorization)
    if token_user is None:
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    if token_user != username:
        raise HTTPException(status_code=403, detail="Forbidden")

    user_data = await _get_user_history(username)
    preferences = user_data.get("preferences", {})
    total_recommendations = sum(preferences.get("genres", {}).values())

    # Favorite genres derived from liked books only
    liked_genres = await get_liked_genres(username)
    favorite_genres = sorted(liked_genres.keys(), key=lambda g: liked_genres[g], reverse=True)[:5]

    liked_books = await get_liked_books(username)

    return {
        "user": username,
        "message": "Welcome to BookBug",
        "stats": {
            "total_recommendations": total_recommendations,
            "favorite_genres": favorite_genres,
            "books_explored": len(preferences.get("books", [])),
            "books_liked": len(liked_books),
        },
        "features": [
            "personalized recommendations",
            "genre discovery",
            "session-based recommendations",
        ],
    }


@app.post("/like", response_model=LikeResponse)
async def toggle_like(
    payload: BookRequest,
    authorization: str | None = Header(default=None),
) -> LikeResponse:
    REQUEST_COUNT.labels(endpoint="like").inc()
    username = _extract_bearer_subject(authorization)
    if not username:
        raise HTTPException(status_code=401, detail="Authentication required")
    liked = await like_book(username, payload.model_dump())
    return LikeResponse(liked=liked, title=payload.title)


@app.get("/likes")
async def get_likes(authorization: str | None = Header(default=None)) -> dict:
    REQUEST_COUNT.labels(endpoint="likes").inc()
    username = _extract_bearer_subject(authorization)
    if not username:
        raise HTTPException(status_code=401, detail="Authentication required")
    books = await get_liked_books(username)
    return {"books": books}


@app.exception_handler(Exception)
def unhandled_exception_handler(_, exc: Exception) -> JSONResponse:
    logging.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ── Cart & Read endpoints (unchanged) ─────────────────────────────────────────

@app.get("/cart", response_model=CartResponse)
async def get_cart(authorization: str | None = Header(default=None)) -> CartResponse:
    REQUEST_COUNT.labels(endpoint="cart").inc()
    username = _extract_bearer_subject(authorization)
    if not username:
        raise HTTPException(status_code=401, detail="Authentication required")
    books = await get_user_cart(username)
    return CartResponse(books=books)


@app.post("/cart")
async def add_book_to_cart(
    payload: BookRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, str]:
    REQUEST_COUNT.labels(endpoint="cart").inc()
    username = _extract_bearer_subject(authorization)
    if not username:
        raise HTTPException(status_code=401, detail="Authentication required")
    added = await add_to_cart(username, payload.model_dump())
    if not added:
        return {"message": "Book already in reading list"}
    return {"message": "Book added to cart"}


@app.delete("/cart/{book_title}")
async def remove_book_from_cart(
    book_title: str,
    authorization: str | None = Header(default=None),
) -> dict[str, str]:
    REQUEST_COUNT.labels(endpoint="cart").inc()
    username = _extract_bearer_subject(authorization)
    if not username:
        raise HTTPException(status_code=401, detail="Authentication required")
    await remove_from_cart(username, book_title)
    return {"message": "Book removed from cart"}


@app.delete("/cart")
async def clear_user_cart(authorization: str | None = Header(default=None)) -> dict[str, str]:
    REQUEST_COUNT.labels(endpoint="cart").inc()
    username = _extract_bearer_subject(authorization)
    if not username:
        raise HTTPException(status_code=401, detail="Authentication required")
    await clear_cart(username)
    return {"message": "Cart cleared"}


@app.get("/read", response_model=ReadBooksResponse)
async def get_read(authorization: str | None = Header(default=None)) -> ReadBooksResponse:
    REQUEST_COUNT.labels(endpoint="read").inc()
    username = _extract_bearer_subject(authorization)
    if not username:
        raise HTTPException(status_code=401, detail="Authentication required")
    books = await get_read_books(username)
    return ReadBooksResponse(books=books)


@app.post("/read")
async def mark_book_read(
    payload: BookRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, str]:
    REQUEST_COUNT.labels(endpoint="read").inc()
    username = _extract_bearer_subject(authorization)
    if not username:
        raise HTTPException(status_code=401, detail="Authentication required")
    await mark_as_read(username, payload.model_dump())
    return {"message": "Book marked as read"}
