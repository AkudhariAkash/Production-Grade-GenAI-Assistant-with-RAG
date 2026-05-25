from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import ChatRequest, ChatResponse, HealthResponse, TokenRequest, TokenResponse
from app.services.auth import create_access_token, verify_token
from app.services.rag_service import RAGService


router = APIRouter()
rag_service = RAGService()


@router.get("/health", response_model=HealthResponse)
def health():
    return {"status": "healthy"}


@router.post("/auth/token", response_model=TokenResponse)
def issue_token(payload: TokenRequest):
    return {"access_token": create_access_token(payload.username)}


@router.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest, _: str = Depends(verify_token)):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message field is required")
    if not req.sessionId.strip():
        raise HTTPException(status_code=400, detail="sessionId field is required")
    try:
        return rag_service.chat(req.sessionId, req.message)
    except RuntimeError as exc:
        msg = str(exc)
        if msg == "Invalid API key":
            raise HTTPException(status_code=401, detail=msg)
        if msg == "Request timeout":
            raise HTTPException(status_code=504, detail=msg)
        if msg == "Rate limit exceeded":
            raise HTTPException(status_code=429, detail=msg)
        if msg == "Model temporarily unavailable. Please try again in a moment.":
            raise HTTPException(status_code=503, detail=msg)
        raise HTTPException(status_code=502, detail=msg)
