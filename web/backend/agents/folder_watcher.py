"""
Multi-user folder watcher agent using watchdog.

Lifecycle:
  - Instantiated once in FastAPI lifespan (app startup)
  - start() launches a single Observer thread
  - reload_user(user_id) adds/refreshes a user's watch folder
  - unschedule_user(user_id) removes a user's watch folder
  - stop() tears down the observer on app shutdown
"""
from __future__ import annotations

import asyncio
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

log = logging.getLogger(__name__)


class _UserHandler(FileSystemEventHandler):
    """Triggers a pipeline run when a new PDF lands in the watched folder."""

    def __init__(
        self,
        user_id: int,
        db_factory: "SessionFactory",
        loop: asyncio.AbstractEventLoop,
    ) -> None:
        super().__init__()
        self.user_id = user_id
        self._db_factory = db_factory
        self._loop = loop
        self._lock = threading.Lock()

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        path = Path(str(event.src_path))
        if path.suffix.lower() != ".pdf":
            return
        # Avoid re-triggering on already-processed files
        if "_Invoice Generated_" in path.name:
            return

        log.info("Watcher: new PDF detected for user %d — %s", self.user_id, path.name)
        with self._lock:
            asyncio.run_coroutine_threadsafe(
                self._trigger(), self._loop
            )

    async def _trigger(self) -> None:
        from ..services.pipeline_runner import run_pipeline_for_user

        db: Session = self._db_factory()
        try:
            # Update last_watch_event timestamp
            from ..models import UserSettings
            s = db.query(UserSettings).filter(
                UserSettings.user_id == self.user_id
            ).first()
            if s:
                s.last_watch_event = datetime.now(timezone.utc).isoformat()
                db.commit()

            await run_pipeline_for_user(self.user_id, db, triggered_by="watcher")
        except Exception as exc:
            log.error("Watcher pipeline error for user %d: %s", self.user_id, exc)
        finally:
            db.close()


# Type alias so mypy/pyright doesn't complain
from typing import Callable, Protocol

class SessionFactory(Protocol):
    def __call__(self) -> "Session": ...


class FolderWatcher:
    """Registry of per-user folder watches on a single Observer thread."""

    def __init__(
        self,
        db_factory: SessionFactory,
        loop: asyncio.AbstractEventLoop,
    ) -> None:
        self._db_factory = db_factory
        self._loop = loop
        self._observer = Observer()
        self._watches: dict[int, object] = {}   # user_id → watchdog watch handle
        self._folders: dict[int, str] = {}       # user_id → folder path

    def start(self) -> None:
        self._observer.start()
        log.info("FolderWatcher observer started")

    def stop(self) -> None:
        self._observer.stop()
        self._observer.join()
        log.info("FolderWatcher observer stopped")

    def is_watching(self, user_id: int) -> bool:
        return user_id in self._watches

    def reload_user(self, user_id: int) -> None:
        """Load (or reload) a user's watch from the DB."""
        from ..database import SessionLocal
        from ..models import UserSettings

        db = SessionLocal()
        try:
            s = db.query(UserSettings).filter(
                UserSettings.user_id == user_id
            ).first()
            if not s or not s.watch_enabled or not s.input_folder:
                self.unschedule_user(user_id)
                return
            folder = s.input_folder
        finally:
            db.close()

        # Remove old watch if folder changed
        if user_id in self._watches:
            if self._folders.get(user_id) == folder:
                return  # Nothing changed
            self._observer.unschedule(self._watches.pop(user_id))

        Path(folder).mkdir(parents=True, exist_ok=True)
        handler = _UserHandler(user_id, self._db_factory, self._loop)
        watch = self._observer.schedule(handler, folder, recursive=False)
        self._watches[user_id] = watch
        self._folders[user_id] = folder
        log.info("FolderWatcher: watching %s for user %d", folder, user_id)

    def unschedule_user(self, user_id: int) -> None:
        if user_id in self._watches:
            self._observer.unschedule(self._watches.pop(user_id))
            self._folders.pop(user_id, None)
            log.info("FolderWatcher: stopped watching for user %d", user_id)

    def load_all_active_users(self) -> None:
        """Call on startup to resume watches for all enabled users."""
        from ..database import SessionLocal
        from ..models import UserSettings

        db = SessionLocal()
        try:
            active = db.query(UserSettings).filter(
                UserSettings.watch_enabled == True  # noqa: E712
            ).all()
        finally:
            db.close()

        for s in active:
            try:
                self.reload_user(s.user_id)
            except Exception as exc:
                log.error("Could not start watch for user %d: %s", s.user_id, exc)
