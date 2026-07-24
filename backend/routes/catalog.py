import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import User, Product, Category
from auth import get_current_user

router = APIRouter()


def serialize_product(p: Product) -> dict:
    cat = p.category_rel
    return {
        "id": p.id,
        "name": p.name,
        "name_ar": p.name_ar,
        "description": p.description,
        "description_ar": p.description_ar,
        "price": p.price,
        "category_id": p.category_id,
        "category": cat.name if cat else None,
        "sku": p.sku,
        "image_url": p.image_url,
        "is_active": p.is_active,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


def serialize_category(c: Category) -> dict:
    return {"id": c.id, "name": c.name, "name_ar": c.name_ar, "parent_id": c.parent_id}


class ProductIn(BaseModel):
    name: str
    name_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    price: float = 0
    category_id: int | None = None
    sku: str
    is_active: bool = True


class CategoryIn(BaseModel):
    name: str
    name_ar: str | None = None
    parent_id: int | None = None


@router.get("/products")
def list_products(
    search: str = "",
    category_id: int | None = None,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Product).filter(Product.organization_id == user.organization_id)
    if active_only:
        q = q.filter(Product.is_active == True)
    if search:
        q = q.filter(
            Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%")
        )
    if category_id:
        q = q.filter(Product.category_id == category_id)
    return [serialize_product(p) for p in q.offset(skip).limit(limit).all()]


@router.post("/products")
def create_product(
    data: ProductIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (
        db.query(Product)
        .filter(
            Product.organization_id == user.organization_id, Product.sku == data.sku
        )
        .first()
    ):
        raise HTTPException(400, "SKU already exists in your catalog")
    p = Product(**data.model_dump(), organization_id=user.organization_id)
    db.add(p)
    db.commit()
    db.refresh(p)
    return serialize_product(p)


@router.put("/products/{product_id}")
def update_product(
    product_id: int,
    data: ProductIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = (
        db.query(Product)
        .filter(
            Product.id == product_id, Product.organization_id == user.organization_id
        )
        .first()
    )
    if not p:
        raise HTTPException(404, "Product not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return serialize_product(p)


@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = (
        db.query(Product)
        .filter(
            Product.id == product_id, Product.organization_id == user.organization_id
        )
        .first()
    )
    if not p:
        raise HTTPException(404, "Product not found")
    db.delete(p)
    db.commit()
    return {"ok": True}


@router.get("/categories")
def list_categories(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cats = (
        db.query(Category)
        .filter(Category.organization_id == user.organization_id)
        .all()
    )
    return [serialize_category(c) for c in cats]


@router.post("/categories")
def create_category(
    data: CategoryIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    c = Category(**data.model_dump(), organization_id=user.organization_id)
    db.add(c)
    db.commit()
    db.refresh(c)
    return serialize_category(c)


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    c = (
        db.query(Category)
        .filter(
            Category.id == category_id, Category.organization_id == user.organization_id
        )
        .first()
    )
    if not c:
        raise HTTPException(404, "Category not found")
    db.delete(c)
    db.commit()
    return {"ok": True}


@router.post("/import")
def import_csv(
    user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    import csv
    import io

    content = file.file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))

    # Normalize headers to lowercase for case-insensitive matching
    reader.fieldnames = [h.strip().lower() for h in (reader.fieldnames or [])]

    created = 0
    skipped = 0
    errors = []

    for i, row in enumerate(reader, start=2):
        sku = row.get("sku", "").strip()
        name = row.get("name", "").strip()
        if not sku or not name:
            skipped += 1
            continue
        if (
            db.query(Product)
            .filter(Product.organization_id == user.organization_id, Product.sku == sku)
            .first()
        ):
            skipped += 1
            continue

        try:
            price = float(row.get("price", 0) or 0)
        except ValueError:
            errors.append(f"Row {i}: invalid price '{row.get('price')}'")
            skipped += 1
            continue

        # Match category by name if provided
        category_id = None
        cat_name = row.get("category", "").strip()
        if cat_name:
            cat = (
                db.query(Category)
                .filter(
                    Category.organization_id == user.organization_id,
                    Category.name.ilike(cat_name),
                )
                .first()
            )
            if cat:
                category_id = cat.id

        p = Product(
            organization_id=user.organization_id,
            name=name,
            name_ar=row.get("name_ar", "").strip() or None,
            description=row.get("description", "").strip() or None,
            description_ar=row.get("description_ar", "").strip() or None,
            price=price,
            sku=sku,
            category_id=category_id,
        )
        db.add(p)
        created += 1

    db.commit()
    return {"created": created, "skipped": skipped, "errors": errors}


@router.post("/import-pdf")
def import_pdf(
    user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    import pdfplumber
    import io

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "File must be a PDF")

    pdf_bytes = file.file.read()
    if len(pdf_bytes) > 20 * 1024 * 1024:
        raise HTTPException(400, "PDF file too large (max 20MB)")

    # Extract text from PDF
    text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            if i >= 15:
                break
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    if not text.strip():
        raise HTTPException(
            400, "No extractable text found in PDF. The file may be a scanned image."
        )

    # Truncate if very long
    if len(text) > 12000:
        text = text[:12000]

    # Use LLM to extract products
    from services.llm import extract_products_from_text

    try:
        products = extract_products_from_text(text)
    except Exception as e:
        raise HTTPException(400, f"Failed to extract products from PDF: {str(e)}")

    created = 0
    skipped = 0
    errors = []

    def clean_str(val) -> str | None:
        if val is None:
            return None
        s = str(val).strip()
        if not s or s.lower() == "none" or s.lower() == "null":
            return None
        return s

    for i, row in enumerate(products, start=1):
        name = clean_str(row.get("name"))
        if not name:
            skipped += 1
            continue

        sku = str(row.get("sku", "")).strip()
        if not sku:
            sku = f"PROD-{i:04d}"

        if (
            db.query(Product)
            .filter(Product.organization_id == user.organization_id, Product.sku == sku)
            .first()
        ):
            skipped += 1
            continue

        try:
            price = float(row.get("price", 0) or 0)
        except (ValueError, TypeError):
            errors.append(f"Product '{name}': invalid price '{row.get('price')}'")
            skipped += 1
            continue

        category_id = None
        cat_name = clean_str(row.get("category"))
        if cat_name:
            cat = (
                db.query(Category)
                .filter(
                    Category.organization_id == user.organization_id,
                    Category.name.ilike(cat_name),
                )
                .first()
            )
            if cat:
                category_id = cat.id
            else:
                # Auto-create the category
                new_cat = Category(
                    organization_id=user.organization_id,
                    name=cat_name,
                )
                db.add(new_cat)
                db.flush()
                category_id = new_cat.id

        p = Product(
            organization_id=user.organization_id,
            name=name,
            name_ar=clean_str(row.get("name_ar")),
            description=clean_str(row.get("description")),
            description_ar=clean_str(row.get("description_ar")),
            price=price,
            sku=sku,
            category_id=category_id,
        )
        db.add(p)
        created += 1

    db.commit()
    return {"created": created, "skipped": skipped, "errors": errors}
