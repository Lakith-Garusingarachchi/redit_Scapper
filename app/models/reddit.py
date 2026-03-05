from pydantic import BaseModel
from typing import List, Optional


class Comment(BaseModel):
    author: str
    body: str
    score: int


class Thread(BaseModel):
    id: str
    title: str
    url: str
    upvotes: int
    upvote_ratio: float
    num_comments: int
    body: Optional[str] = None
    top_comments: List[Comment] = []
    thread_summary: Optional[str] = None


class Community(BaseModel):
    name: str
    title: str
    description: str
    subscribers: int
    threads: List[Thread] = []
    community_summary: Optional[str] = None


class ScrapeRequest(BaseModel):
    category: str
    max_communities: int = 5
    max_threads: int = 20


class ScrapeResponse(BaseModel):
    category: str
    scraped_at: str
    file_path: str
    communities: List[Community]


class SummarizeRequest(BaseModel):
    file_path: str
