from fastapi import APIRouter, Depends, HTTPException, Body
from database import Chat, Folder, Message, get_db
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
    # Filter out empty chats by joining with Message (Inner Join)
    # Use distinct to avoid duplicates if multiple messages
    chats = (
        db.query(Chat)
        .join(Message)
        .filter(Chat.user_id == user.id)
        .order_by(Chat.created_at.desc())
        .distinct()
        .all()
    )

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


@router.delete("/chats")
async def delete_all_chats(user=Depends(get_current_user), db=Depends(get_db)):
    try:
        from gantry.chat import delete_all_chats_for_user_db

        delete_all_chats_for_user_db(user.id, db)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "success"}


@router.put("/chats/{chat_id}/rename")
async def rename_chat(
    chat_id: str,
    title: str = Body(..., embed=True),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    chat.title = title
    db.commit()
    return {"status": "success", "title": title}


@router.get("/search")
async def search_messages(q: str, user=Depends(get_current_user), db=Depends(get_db)):
    if not q or len(q.strip()) < 2:
        return []

    results = (
        db.query(Message)
        .join(Chat)
        .filter(Chat.user_id == user.id)
        .filter(Message.content.ilike(f"%{q}%"))
        .order_by(Message.created_at.desc())
        .limit(50)
        .all()
    )

    response = []
    for msg in results:
        # Simple snippet generation
        content = msg.content
        try:
            mid_idx = content.lower().index(q.lower())
            start = max(0, mid_idx - 60)
            end = min(len(content), mid_idx + 60)
            snippet = content[start:end]
            if start > 0:
                snippet = "..." + snippet
            if end < len(content):
                snippet = snippet + "..."
        except ValueError:
            snippet = content[:150]

        response.append(
            {
                "chat_id": msg.chat_id,
                "title": msg.chat.title or "Untitled Chat",
                "snippet": snippet,
                "created_at": msg.created_at.isoformat(),
            }
        )
    return response


@router.post("/model")
async def set_model(
    model: str = Body(..., embed=True),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    db.add(user)  # Re-attach or merge if detached?
    # Since get_current_user closes its session, user is detached.
    # We must merge it into the current db session.
    user = db.merge(user)
    user.current_model = model
    db.commit()
    return {"status": "success", "model": model}
