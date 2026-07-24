import sys, os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import User, Proposal, Organization, ProposalChatMessage
from auth import get_current_user
from services.rag import search_relevant_chunks
from services.llm import generate_rag_proposal, chat_edit_proposal
from services.pdf import generate_pdf

router = APIRouter()


def serialize_proposal(p: Proposal) -> dict:
    msgs = [
        {
            "id": m.id,
            "sender": m.sender,
            "message": m.message,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in (p.messages or [])
    ]
    return {
        "id": p.id,
        "client_name": p.client_name,
        "client_request": p.client_request,
        "language": p.language,
        "status": p.status,
        "proposal_content": p.proposal_content,
        "pdf_path": p.pdf_path,
        "messages": msgs,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }


def ensure_proposal_pdf(p: Proposal, db: Session, user: User) -> str:
    if p.pdf_path and os.path.exists(p.pdf_path):
        return p.pdf_path

    org = db.query(Organization).filter(Organization.id == user.organization_id).first()
    org_name = org.name if org else ""
    
    new_pdf_path = generate_pdf(
        p.client_name,
        p.proposal_content or "No proposal content.",
        p.language or "en",
        org_name=org_name,
        brand_color=org.primary_color if org else "#4F46E5",
        logo_url=org.logo_url if org else "",
    )
    
    p.pdf_path = new_pdf_path
    db.commit()
    db.refresh(p)
    return new_pdf_path


class ProposalRequest(BaseModel):
    client_name: str
    client_request: str
    language: str = "en"


class ProposalUpdate(BaseModel):
    proposal_content: str


class ChatMessageRequest(BaseModel):
    message: str


@router.get("/")
def list_proposals(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    props = (
        db.query(Proposal)
        .filter(Proposal.organization_id == user.organization_id)
        .order_by(Proposal.id.desc())
        .all()
    )
    return [serialize_proposal(p) for p in props]


@router.get("/{proposal_id}")
def get_proposal(
    proposal_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = (
        db.query(Proposal)
        .filter(
            Proposal.id == proposal_id, Proposal.organization_id == user.organization_id
        )
        .first()
    )
    if not p:
        raise HTTPException(404, "Proposal not found")
    return serialize_proposal(p)


@router.put("/{proposal_id}")
def update_proposal(
    proposal_id: int,
    data: ProposalUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = (
        db.query(Proposal)
        .filter(
            Proposal.id == proposal_id, Proposal.organization_id == user.organization_id
        )
        .first()
    )
    if not p:
        raise HTTPException(404, "Proposal not found")

    p.proposal_content = data.proposal_content
    db.commit()

    ensure_proposal_pdf(p, db, user)
    return serialize_proposal(p)


@router.post("/{proposal_id}/chat")
def chat_with_proposal_ai(
    proposal_id: int,
    data: ChatMessageRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = (
        db.query(Proposal)
        .filter(
            Proposal.id == proposal_id, Proposal.organization_id == user.organization_id
        )
        .first()
    )
    if not p:
        raise HTTPException(404, "Proposal not found")

    user_msg_text = data.message.strip()
    if not user_msg_text:
        raise HTTPException(400, "Message cannot be empty")

    user_msg = ProposalChatMessage(
        proposal_id=p.id,
        sender="user",
        message=user_msg_text
    )
    db.add(user_msg)
    db.commit()

    history = [
        {"sender": m.sender, "message": m.message}
        for m in p.messages
    ]

    updated_markdown, ai_response_text = chat_edit_proposal(
        current_content=p.proposal_content or "",
        user_message=user_msg_text,
        chat_history=history,
        language=p.language or "en"
    )

    ai_msg = ProposalChatMessage(
        proposal_id=p.id,
        sender="assistant",
        message=ai_response_text
    )
    db.add(ai_msg)

    p.proposal_content = updated_markdown
    p.pdf_path = None # invalidate old PDF path so fresh PDF is created
    db.commit()

    ensure_proposal_pdf(p, db, user)
    return serialize_proposal(p)


@router.delete("/{proposal_id}")
def delete_proposal(
    proposal_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = (
        db.query(Proposal)
        .filter(
            Proposal.id == proposal_id, Proposal.organization_id == user.organization_id
        )
        .first()
    )
    if not p:
        raise HTTPException(404, "Proposal not found")
    db.delete(p)
    db.commit()
    return {"ok": True}


@router.get("/{proposal_id}/pdf")
def view_pdf_inline(
    proposal_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = (
        db.query(Proposal)
        .filter(
            Proposal.id == proposal_id, Proposal.organization_id == user.organization_id
        )
        .first()
    )
    if not p:
        raise HTTPException(404, "Proposal not found")

    pdf_file_path = ensure_proposal_pdf(p, db, user)
    return FileResponse(
        pdf_file_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=proposal_{p.client_name}.pdf"},
    )


@router.get("/{proposal_id}/download")
def download_proposal(
    proposal_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = (
        db.query(Proposal)
        .filter(
            Proposal.id == proposal_id, Proposal.organization_id == user.organization_id
        )
        .first()
    )
    if not p:
        raise HTTPException(404, "Proposal not found")

    pdf_file_path = ensure_proposal_pdf(p, db, user)
    return FileResponse(
        pdf_file_path,
        media_type="application/pdf",
        filename=f"proposal_{p.client_name}.pdf",
    )


@router.post("/generate")
def generate_proposal(
    req: ProposalRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org = db.query(Organization).filter(Organization.id == user.organization_id).first()
    org_name = org.name if org else ""

    rag_chunks = search_relevant_chunks(db, user.organization_id, req.client_request, top_k=5)

    content = generate_rag_proposal(
        client_name=req.client_name,
        client_request=req.client_request,
        rag_chunks=rag_chunks,
        language=req.language,
        org_name=org_name
    )

    proposal = Proposal(
        organization_id=user.organization_id,
        user_id=user.id,
        client_name=req.client_name,
        client_request=req.client_request,
        language=req.language,
        status="completed",
        proposal_content=content,
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    welcome_msg = ProposalChatMessage(
        proposal_id=proposal.id,
        sender="assistant",
        message=f"Hello! I am your AI Proposal Assistant. I've generated your initial draft based on your customer demands and RAG company knowledge. Ask me anything to refine or edit!"
    )
    db.add(welcome_msg)
    db.commit()

    ensure_proposal_pdf(proposal, db, user)
    return serialize_proposal(proposal)
