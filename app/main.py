

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

# ✅ FIX imports to be package-relative
from . import models, schemas, auth
from .database import get_db


app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev only, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to SaaS Notes API"}



@app.get("/health")
def health():
    return {"status": "ok"}


# -------- Tenant Upgrade --------
@app.post("/tenants/{slug}/upgrade")
def upgrade_tenant(
    slug: str,
    current=Depends(auth.get_current_admin),  # only Admin allowed
    db: Session = Depends(get_db),
):
    tenant = db.query(models.Tenant).filter_by(slug=slug).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.plan = "pro"
    db.add(tenant)
    db.commit()
    return {"status": "upgraded", "plan": tenant.plan}


# -------- Notes CRUD --------
@app.post("/notes")
def create_note(
    payload: schemas.NoteCreate,
    current=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    tenant_id = current["tenant_id"]
    tenant = db.query(models.Tenant).get(tenant_id)

    # Enforce free plan limit
    if tenant.plan == "free":
        count = db.query(models.Note).filter_by(tenant_id=tenant_id).count()
        if count >= 3:
            raise HTTPException(status_code=403, detail="Free plan limit reached")

    note = models.Note(
        title=payload.title, content=payload.content, tenant_id=tenant_id
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@app.get("/notes")
def list_notes(
    current=Depends(auth.get_current_user), db: Session = Depends(get_db)
):
    return db.query(models.Note).filter_by(tenant_id=current["tenant_id"]).all()


@app.get("/notes/{note_id}")
def get_note(
    note_id: int, current=Depends(auth.get_current_user), db: Session = Depends(get_db)
):
    note = (
        db.query(models.Note)
        .filter_by(id=note_id, tenant_id=current["tenant_id"])
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Not found")
    return note


@app.put("/notes/{note_id}")
def update_note(
    note_id: int,
    payload: schemas.NoteCreate,
    current=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    note = (
        db.query(models.Note)
        .filter_by(id=note_id, tenant_id=current["tenant_id"])
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Not found")
    note.title = payload.title
    note.content = payload.content
    db.add(note)
    db.commit()
    return note


@app.delete("/notes/{note_id}")
def delete_note(
    note_id: int, current=Depends(auth.get_current_user), db: Session = Depends(get_db)
):
    note = (
        db.query(models.Note)
        .filter_by(id=note_id, tenant_id=current["tenant_id"])
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(note)
    db.commit()
    return {"status": "deleted"}
