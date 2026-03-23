from __future__ import annotations

import logging
from collections import deque
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pythonjsonlogger.json import JsonFormatter

from app.schemas import Book, GenreResponse, HistoryRecord, HistoryResponse, RecommendationResponse
from recommender.engine import RecommendationEngine

BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = BASE_DIR / "dataset" / "books.json"

REQUEST_COUNT = Counter("bookbee_http_requests_total", "Total HTTP requests", ["endpoint"])
REQUEST_LATENCY = Histogram("bookbee_request_latency_seconds", "Latency by endpoint", ["endpoint"])


def configure_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.handlers = [handler]


configure_logging()
app = FastAPI(title="BookBee DevOps Platform API", version="1.0.0")
engine = RecommendationEngine(DATASET_PATH)
history: deque[HistoryRecord] = deque(maxlen=20)


@app.get("/health")
def health() -> dict[str, str]:
    REQUEST_COUNT.labels(endpoint="health").inc()
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/genre", response_model=GenreResponse)
def genre() -> GenreResponse:
    with REQUEST_LATENCY.labels(endpoint="genre").time():
        REQUEST_COUNT.labels(endpoint="genre").inc()
        return GenreResponse(genre=engine.random_genre())


@app.get("/recommend/{genre}", response_model=RecommendationResponse)
def recommend(genre: str) -> RecommendationResponse:
    with REQUEST_LATENCY.labels(endpoint="recommend").time():
        REQUEST_COUNT.labels(endpoint="recommend").inc()
        normalized = genre.lower()
        if normalized not in engine.genres():
            raise HTTPException(status_code=404, detail=f"Genre '{genre}' not found")

        books = [Book.model_validate(book.__dict__) for book in engine.recommend(normalized)]
        record = HistoryRecord(genre=normalized, books=books)
        history.appendleft(record)
        return RecommendationResponse(genre=normalized, books=books)


@app.get("/history", response_model=HistoryResponse)
def get_history() -> HistoryResponse:
    REQUEST_COUNT.labels(endpoint="history").inc()
    return HistoryResponse(history=list(history))


@app.exception_handler(Exception)
def unhandled_exception_handler(_, exc: Exception) -> JSONResponse:
    logging.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
