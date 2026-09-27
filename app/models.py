from pydantic import BaseModel, Field
from typing import List


class Source(BaseModel):
    path: str
    start_line: int | None = None
    end_line: int | None = None
    page: int | None = None
    chunk_id: str


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=10)


class AskResponse(BaseModel):
    answer: str
    sources: List[Source]


class IngestResponse(BaseModel):
    indexed_files: int
    indexed_chunks: int
    collection_count: int