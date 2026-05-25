from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.routes.chat import router as chat_router
from app.utils.logger import setup_logger

logger = setup_logger()
app = FastAPI(title="Production RAG Assistant", version="1.0.0")
app.include_router(chat_router)
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@app.get("/")
def root():
    return FileResponse("frontend/index.html")


@app.exception_handler(RequestValidationError)
async def validation_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"error": "Validation error", "details": str(exc)})


@app.exception_handler(Exception)
async def global_handler(_: Request, exc: Exception):
    logger.exception("Unhandled server error: %s", exc)
    return JSONResponse(status_code=500, content={"error": "Internal server error", "details": str(exc)})
