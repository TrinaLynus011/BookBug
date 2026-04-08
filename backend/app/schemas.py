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


class UserSignup(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class BookRequest(BaseModel):
    title: str
    author: str
    genre: str
    rating: float


class CartItem(BaseModel):
    title: str
    author: str
    genre: str
    rating: float
    added_at: str


class CartResponse(BaseModel):
    books: list[CartItem]


class ReadBooksResponse(BaseModel):
    books: list[CartItem]


class LikeResponse(BaseModel):
    liked: bool
    title: str
