"""FastAPI application entrypoint."""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine, SessionLocal
from .routers import auth, settings, pipeline, invoices, watcher
from .agents.folder_watcher import FolderWatcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s — %(message)s",
)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # ── Startup ──────────────────────────────────────────────────────────────
    # Create all DB tables (idempotent)
    Base.metadata.create_all(bind=engine)
    log.info("Database tables ready")

    # Start the multi-user folder watcher
    loop = asyncio.get_event_loop()
    fw = FolderWatcher(db_factory=SessionLocal, loop=loop)
    fw.start()
    fw.load_all_active_users()
    app.state.folder_watcher = fw

    # Per-user Zoho token caches  {user_id: {"access_token": ..., "expires_at": ...}}
    app.state.zoho_token_caches: dict[int, dict] = {}

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────────
    fw.stop()
    log.info("Shutdown complete")


app = FastAPI(
    title="Zoho Invoice Automation API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the Next.js dev server and production domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # Add your Vercel URL here when deploying:
        # "https://your-app.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(settings.router)
app.include_router(pipeline.router)
app.include_router(invoices.router)
app.include_router(watcher.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
