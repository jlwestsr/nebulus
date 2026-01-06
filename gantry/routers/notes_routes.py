from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

try:
    from gantry.database import get_db, Note, User
except ImportError:
    from database import get_db, Note, User
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/notes", tags=["notes"])


# Pydantic Models
class NoteCreate(BaseModel):
    title: str = "Untitled"
    content: str = ""
    category: Optional[str] = "Uncategorized"


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None


class NoteResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    category: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Dependency to get current user (mocked/simplified for now as per chat.py)
def get_current_user_id(db: Session = Depends(get_db)) -> int:
    # MVP: Fetch first user or default to 1.
    # In production, this would use the AuthMiddleware user object.
    user = db.query(User).first()
    return user.id if user else 1


@router.get("", response_model=List[NoteResponse])
async def get_notes(
    db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)
):
    return (
        db.query(Note)
        .filter(Note.user_id == user_id)
        .order_by(Note.updated_at.desc())
        .all()
    )


@router.post("", response_model=NoteResponse)
async def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    new_note = Note(
        user_id=user_id,
        title=note.title,
        content=note.content,
        category=note.category,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_update: NoteUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if note_update.title is not None:
        note.title = note_update.title
    if note_update.content is not None:
        note.content = note_update.content
    if note_update.category is not None:
        note.category = note_update.category

    note.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}")
async def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(note)
    db.commit()
    return {"status": "success", "message": "Note deleted"}
