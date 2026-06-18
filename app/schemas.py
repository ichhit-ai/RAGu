from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    query: str

class SourceSnippet(BaseModel):
    content: str
    metadata: Dict[str, Any]

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceSnippet]
    latency: float
    answer_found: bool

class FrequentQueryItem(BaseModel):
    query: str
    count: int

class UnresolvedQueryItem(BaseModel):
    query: str
    timestamp: str
    latency: float

class LatencyHistoryItem(BaseModel):
    id: int
    timestamp: str
    latency: float
    answer_found: bool

class AnalyticsResponse(BaseModel):
    total_queries: int
    avg_latency: float
    success_rate: float
    frequent_queries: List[FrequentQueryItem]
    unresolved_queries: List[UnresolvedQueryItem]
    latency_history: List[LatencyHistoryItem]
