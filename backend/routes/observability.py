import time
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Document, DocumentChunk, Proposal
from config import settings

router = APIRouter()
START_TIME = time.time()


@router.get("/health")
@router.get("/status")
def get_system_status(db: Session = Depends(get_db)):
    db_ok = True
    try:
        db.query(User).first()
    except Exception:
        db_ok = False

    return {
        "status": "ok" if db_ok else "degraded",
        "timestamp": time.time(),
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "environment": settings.APP_ENV,
        "database": {
            "status": "connected" if db_ok else "error",
            "driver": "PostgreSQL" if "postgresql" in settings.DATABASE_URL else "SQLite",
        },
        "services": {
            "groq_llm": bool(settings.GROQ_API_KEY),
            "rag_vector_engine": "active",
        },
    }


@router.get("/metrics")
def get_system_metrics(db: Session = Depends(get_db)):
    try:
        users_cnt = db.query(User).count()
        docs_cnt = db.query(Document).count()
        chunks_cnt = db.query(DocumentChunk).count()
        props_cnt = db.query(Proposal).count()
    except Exception as e:
        raise HTTPException(500, f"Error calculating metrics: {str(e)}")

    return {
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "total_users": users_cnt,
        "total_documents": docs_cnt,
        "total_rag_chunks": chunks_cnt,
        "total_proposals": props_cnt,
        "llm_provider": "Groq Llama 3.3 70B",
    }


@router.get("/logs")
def get_recent_activity(db: Session = Depends(get_db)):
    recent_docs = (
        db.query(Document)
        .order_by(Document.id.desc())
        .limit(5)
        .all()
    )
    recent_props = (
        db.query(Proposal)
        .order_by(Proposal.id.desc())
        .limit(5)
        .all()
    )

    activities = []
    for d in recent_docs:
        activities.append({
            "type": "document_upload",
            "description": f"Uploaded '{d.filename}' ({d.chunk_count} RAG chunks)",
            "timestamp": d.created_at.isoformat() if d.created_at else None,
        })
    for p in recent_props:
        activities.append({
            "type": "proposal_generation",
            "description": f"Generated proposal for '{p.client_name}' ({p.language.upper()})",
            "timestamp": p.created_at.isoformat() if p.created_at else None,
        })

    activities.sort(key=lambda x: x["timestamp"] or "", reverse=True)
    return {"activity_log": activities}
