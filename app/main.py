import logging
from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.services.decision_agent import make_hiring_decision

from app.api.auth import router as auth_router
from app.api.sessions import router as sessions_router
from app.core.database import engine, Base
from app.models import user, session  # Import models to register them with Base.metadata
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup if needed
    await engine.dispose()

app = FastAPI(
    title="Resume Ingestion and Embedding API",
    description="API for ingesting resumes, chunking, generating embeddings, and vector search with FAISS.",
    lifespan=lifespan
)

import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

# Read FRONTEND_URL if deployed in production, otherwise allow all origins
frontend_url = os.environ.get("FRONTEND_URL", "*")
allowed_origins = [frontend_url] if frontend_url != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(auth_router)
app.include_router(sessions_router)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
