from pydantic import BaseModel


class AuthorSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class BookSchema(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


class EditionBase(BaseModel):
    isbn: str | None = None
    publisher: str | None = None
    year: int | None = None


class EditionCreate(EditionBase):
    book_id: int
    author_ids: list[int] = []


class EditionResponse(EditionBase):
    id: int
    book_id: int
    score: float | None = None
    confidence: float | None = None
    review_count: int = 0
    book: BookSchema | None = None
    authors: list[AuthorSchema] = []

    class Config:
        from_attributes = True
