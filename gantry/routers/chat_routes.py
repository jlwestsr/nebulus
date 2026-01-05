from fastapi import APIRouter, Depends, HTTPException, Body
from database import Chat, Folder, get_db
from routers.auth_routes import get_current_user

router = APIRouter(prefix="/api", tags=["chat"])


@router.get("/folders")
async def get_folders(user=Depends(get_current_user), db=Depends(get_db)):
    folders = db.query(Folder).filter(Folder.user_id == user.id).all()
    return [{"id": f.id, "name": f.name} for f in folders]


@router.post("/folders")
async def create_folder(
    name: str = Body(..., embed=True),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    folder = Folder(name=name, user_id=user.id)
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return {"id": folder.id, "name": folder.name}


@router.delete("/folders/{folder_id}")
async def delete_folder(
    folder_id: int, user=Depends(get_current_user), db=Depends(get_db)
):
    folder = (
        db.query(Folder)
        .filter(Folder.id == folder_id, Folder.user_id == user.id)
        .first()
    )
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Move chats to root (null folder) or delete them? Usually move to root.
    # Logic: Set folder_id to None for all chats in this folder
    chats = db.query(Chat).filter(Chat.folder_id == folder_id).all()
    for chat in chats:
        chat.folder_id = None

    db.delete(folder)
    db.commit()
    return {"status": "success"}


@router.get("/history")
async def get_chat_history(user=Depends(get_current_user), db=Depends(get_db)):
    # Fetch all chats for user, ordered by creation desc
    # Chainlit likely handles 'Session' logic differently, but we are building a persistent history view.
    # We might need to sync Chainlit sessions to this DB if they aren't already.
    # For now, we assume simple retrieval.

    chats = (
        db.query(Chat)
        .filter(Chat.user_id == user.id)
        .order_by(Chat.created_at.desc())
        .all()
    )

    # Format for sidebar: Group by folder if present, or "Recent"
    # Or just return flat list and let frontend group
    result = []
    for chat in chats:
        result.append(
            {
                "id": chat.id,
                "title": chat.title or "New Chat",
                "folder_id": chat.folder_id,
                "created_at": chat.created_at.isoformat(),
            }
        )
    return result


@router.put("/chats/{chat_id}/move")
async def move_chat(
    chat_id: str,
    folder_id: int = Body(..., embed=True),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    chat.folder_id = folder_id if folder_id != 0 else None  # 0 means root
    db.commit()
    return {"status": "success"}


@router.delete("/chats/{chat_id}")
async def delete_chat(chat_id: str, user=Depends(get_current_user), db=Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    db.delete(chat)
    db.commit()
    return {"status": "success"}
