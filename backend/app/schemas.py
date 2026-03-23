from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str
    genre: str
    rating: float


class GenreResponse(BaseModel):
    genre: str


class RecommendationResponse(BaseModel):
    genre: str
    books: list[Book]


class HistoryRecord(BaseModel):
    genre: str
    books: list[Book]


class HistoryResponse(BaseModel):
    history: list[HistoryRecord]
