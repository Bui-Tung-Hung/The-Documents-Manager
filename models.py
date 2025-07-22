from pydantic import BaseModel
from typing import List


class SearchFileRequest(BaseModel):
    query: str


class FileSearchResult(BaseModel):
    file_id: str
    score: float
    content: str


class FileSearchResponse(BaseModel):
    query: str
    results: List[FileSearchResult]


class HealthResponse(BaseModel):
    status: str
    message: str
