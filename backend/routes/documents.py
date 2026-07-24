import sys, os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models import User, Document, DocumentChunk
from auth import get_current_user
from services.rag import extract_text_from_file, chunk_text, get_embedding, search_relevant_chunks

router = APIRouter()

def serialize_document(doc: Document, include_text: bool = False) -> dict:
    data = {
        "id": doc.id,
        "filename": doc.filename,
        "file_type": doc.file_type,
        "file_size": doc.file_size,
        "chunk_count": doc.chunk_count,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
    }
    if include_text:
        data["parsed_text"] = doc.parsed_text
    return data


@router.get("/")
def list_documents(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    docs = (
        db.query(Document)
        .filter(Document.organization_id == user.organization_id)
        .order_by(Document.id.desc())
        .all()
    )
    return [serialize_document(d) for d in docs]


@router.get("/{doc_id}")
def get_document(
    doc_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = (
        db.query(Document)
        .filter(Document.id == doc_id, Document.organization_id == user.organization_id)
        .first()
    )
    if not doc:
        raise HTTPException(404, "Document not found")
    return serialize_document(doc, include_text=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    content_bytes = await file.read()
    filename = file.filename or "uploaded_file"
    file_size = len(content_bytes)
    file_type = filename.split(".")[-1].lower() if "." in filename else "txt"

    # Extract text from uploaded document
    extracted_text = extract_text_from_file(filename, content_bytes)
    if not extracted_text:
        raise HTTPException(400, "Could not extract text content from the uploaded file.")

    # Create Document record
    doc = Document(
        organization_id=user.organization_id,
        user_id=user.id,
        filename=filename,
        file_type=file_type,
        file_size=file_size,
        parsed_text=extracted_text,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Chunk text & generate vector embeddings
    text_chunks = chunk_text(extracted_text)
    doc_chunks = []
    for idx, chunk_str in enumerate(text_chunks):
        embedding_vec = get_embedding(chunk_str)
        chunk_obj = DocumentChunk(
            document_id=doc.id,
            chunk_index=idx,
            content=chunk_str,
            embedding=embedding_vec
        )
        doc_chunks.append(chunk_obj)

    db.add_all(doc_chunks)
    doc.chunk_count = len(doc_chunks)
    db.commit()
    db.refresh(doc)

    return serialize_document(doc, include_text=True)


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = (
        db.query(Document)
        .filter(Document.id == doc_id, Document.organization_id == user.organization_id)
        .first()
    )
    if not doc:
        raise HTTPException(404, "Document not found")
    
    db.delete(doc)
    db.commit()
    return {"ok": True, "message": f"Document '{doc.filename}' deleted successfully."}


@router.get("/search")
def test_search(
    q: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    results = search_relevant_chunks(db, user.organization_id, q, top_k=5)
    return {"query": q, "results": results}
