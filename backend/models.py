import json
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    created_at = Column(DateTime, server_default=func.now())

    organization = relationship("Organization", back_populates="members")


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    logo_url = Column(String(500))
    primary_color = Column(String(7), default="#4F46E5")
    font_family = Column(String(100), default="Helvetica")
    created_at = Column(DateTime, server_default=func.now())

    members = relationship("User", back_populates="organization")
    products = relationship("Product", back_populates="organization")
    proposals = relationship("Proposal", back_populates="organization")
    categories = relationship("Category", back_populates="organization")
    templates = relationship("ProposalTemplate", back_populates="organization")
    documents = relationship("Document", back_populates="organization")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(100), nullable=False)
    name_ar = Column(String(100))
    parent_id = Column(Integer, ForeignKey("categories.id"))

    organization = relationship("Organization", back_populates="categories")
    products = relationship("Product", back_populates="category_rel")
    parent = relationship("Category", remote_side=[id])


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    name_ar = Column(String(255))
    description = Column(Text)
    description_ar = Column(Text)
    price = Column(Float, nullable=False, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"))
    sku = Column(String(50), nullable=False)
    image_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    organization = relationship("Organization", back_populates="products")
    category_rel = relationship("Category", back_populates="products")


class ProposalTemplate(Base):
    __tablename__ = "proposal_templates"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    html_template = Column(Text, nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    organization = relationship("Organization", back_populates="templates")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, default=0)
    parsed_text = Column(Text)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    organization = relationship("Organization", back_populates="documents")
    user = relationship("User")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding_json = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    document = relationship("Document", back_populates="chunks")

    @property
    def embedding(self) -> list[float]:
        if not self.embedding_json:
            return []
        try:
            return json.loads(self.embedding_json)
        except Exception:
            return []

    @embedding.setter
    def embedding(self, val: list[float]):
        self.embedding_json = json.dumps(val)


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    client_name = Column(String(255), nullable=False)
    client_request = Column(Text, nullable=False)
    language = Column(String(10), default="en")
    status = Column(String(20), default="draft")
    proposal_content = Column(Text)
    pdf_path = Column(String(500))
    template_id = Column(Integer, ForeignKey("proposal_templates.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", back_populates="proposals")
    user = relationship("User")
    messages = relationship("ProposalChatMessage", back_populates="proposal", cascade="all, delete-orphan")


class ProposalChatMessage(Base):
    __tablename__ = "proposal_chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String(20), nullable=False) # 'user' or 'assistant'
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    proposal = relationship("Proposal", back_populates="messages")
