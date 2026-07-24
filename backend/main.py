import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from database import init_db
from config import settings, validate_config
from routes import auth, proposals, organization, documents, observability

validate_config()

app = FastAPI(
    title="ProposalPilot API",
    version="2.2.0",
    description="AI-powered Sales Proposal Generator with Multi-format Document RAG (Groq Llama 3.3)",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    response.headers["X-Process-Time"] = f"{duration:.4f}s"
    return response

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(proposals.router, prefix="/api/proposals", tags=["Proposals"])
app.include_router(organization.router, prefix="/api/organization", tags=["Organization"])
app.include_router(observability.router, prefix="/api/observability", tags=["Observability"])


@app.on_event("startup")
def startup_db():
    init_db()


@app.get("/")
def root():
    return {
        "app": "ProposalPilot API Server",
        "status": "online",
        "documentation": "/docs",
        "health": "/health",
        "metrics": "/api/observability/metrics"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "env": settings.APP_ENV,
        "groq_configured": bool(settings.GROQ_API_KEY),
        "database_target": "PostgreSQL" if "postgresql" in settings.DATABASE_URL else "SQLite Local",
    }
