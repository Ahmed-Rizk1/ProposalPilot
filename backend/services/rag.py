import io
import math
import re
import csv
import json
import pdfplumber
import docx

def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
    ext = filename.lower().split(".")[-1] if "." in filename else ""
    text = ""
    
    if ext == "pdf":
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages_text = [page.extract_text() or "" for page in pdf.pages]
                text = "\n\n".join(pages_text)
        except Exception as e:
            text = f"Error reading PDF: {str(e)}"
            
    elif ext in ["docx", "doc"]:
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception as e:
            text = f"Error reading DOCX: {str(e)}"
            
    elif ext in ["csv"]:
        try:
            stream = io.StringIO(file_bytes.decode("utf-8", errors="ignore"))
            reader = csv.reader(stream)
            rows = [", ".join(row) for row in reader if any(row)]
            text = "\n".join(rows)
        except Exception as e:
            text = f"Error reading CSV: {str(e)}"
            
    elif ext in ["json"]:
        try:
            data = json.loads(file_bytes.decode("utf-8", errors="ignore"))
            text = json.dumps(data, indent=2)
        except Exception as e:
            text = f"Error reading JSON: {str(e)}"
            
    else:
        try:
            text = file_bytes.decode("utf-8", errors="ignore")
        except Exception as e:
            text = f"Error reading text file: {str(e)}"
            
    return text.strip()


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> list[str]:
    if not text:
        return []
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if len(current_chunk) + len(p) + 2 <= chunk_size:
            current_chunk += ("\n\n" if current_chunk else "") + p
        else:
            if current_chunk:
                chunks.append(current_chunk)
            if len(p) > chunk_size:
                words = p.split(" ")
                sub = ""
                for w in words:
                    if len(sub) + len(w) + 1 <= chunk_size:
                        sub += (" " if sub else "") + w
                    else:
                        chunks.append(sub)
                        sub = w
                if sub:
                    current_chunk = sub
            else:
                current_chunk = p

    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks


def get_embedding(text: str, dim: int = 1536) -> list[float]:
    """
    Generates a normalized 1536-dimensional semantic hashing vector for zero-credit local RAG vector indexing.
    """
    vec = [0.0] * dim
    words = re.findall(r'\w+', text.lower())
    if not words:
        return vec
        
    for idx, word in enumerate(words):
        # Hash word into vector index bucket
        h = 0
        for char in word:
            h = (h * 31 + ord(char)) % dim
        vec[h] += 1.0
        
        # Hash character bi-grams for semantic substring matching
        for i in range(len(word) - 1):
            bigram = word[i:i+2]
            bh = (hash(bigram) & 0x7FFFFFFF) % dim
            vec[bh] += 0.5

    # L2 normalize vector
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2))
    return dot  # normalized vectors dot product equals cosine similarity


def search_relevant_chunks(db_session, org_id: int, query: str, top_k: int = 5) -> list[dict]:
    from models import Document, DocumentChunk
    
    query_vec = get_embedding(query)
    query_words = set(re.findall(r'\w+', query.lower()))
    
    chunks = (
        db_session.query(DocumentChunk)
        .join(Document, DocumentChunk.document_id == Document.id)
        .filter(Document.organization_id == org_id)
        .all()
    )
    
    scored_chunks = []
    
    for c in chunks:
        vec = c.embedding
        sim = cosine_similarity(query_vec, vec) if vec else 0.0
        
        # Keyword match boost
        content_lower = c.content.lower()
        match_count = sum(1 for w in query_words if len(w) > 2 and w in content_lower)
        keyword_score = min(match_count * 0.1, 0.3)
        
        final_score = sim + keyword_score
        scored_chunks.append({
            "chunk_id": c.id,
            "filename": c.document.filename if c.document else "document",
            "content": c.content,
            "score": final_score
        })
        
    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    return scored_chunks[:top_k]
