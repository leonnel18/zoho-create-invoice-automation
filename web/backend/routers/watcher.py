from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, UserSettings
from ..core.dependencies import get_current_user

router = APIRouter(prefix="/api/watcher", tags=["watcher"])


@router.get("/status")
def watcher_status(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    watcher = getattr(request.app.state, "folder_watcher", None)
    active = watcher.is_watching(user.id) if watcher else False
    return {
        "enabled":    s.watch_enabled if s else False,
        "folder":     s.input_folder if s else "",
        "last_event": s.last_watch_event if s else None,
    }


@router.post("/enable")
def enable_watcher(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not s or not s.input_folder:
        raise HTTPException(400, "Set an input folder first")
    s.watch_enabled = True
    db.commit()
    watcher = getattr(request.app.state, "folder_watcher", None)
    if watcher:
        watcher.reload_user(user.id)
    active = watcher.is_watching(user.id) if watcher else False
    return {
        "enabled":    True,
        "folder":     s.input_folder or "",
        "last_event": s.last_watch_event,
    }


@router.post("/disable")
def disable_watcher(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if s:
        s.watch_enabled = False
        db.commit()
    watcher = getattr(request.app.state, "folder_watcher", None)
    if watcher:
        watcher.unschedule_user(user.id)
    return {
        "enabled":    False,
        "folder":     s.input_folder if s else "",
        "last_event": s.last_watch_event if s else None,
    }
