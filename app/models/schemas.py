from pydantic import BaseModel, Field
from typing import List, Optional


class ChatRequest(BaseModel):
    sessionId: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    reply: str
    tokensUsed: int
    retrievedChunks: int
    similarityScores: List[float]
    responseTimeMs: int


class HealthResponse(BaseModel):
    status: str


class TokenRequest(BaseModel):
    username: str = Field(..., min_length=3)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
