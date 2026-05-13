"""
main.py — Entry point FastAPI.
Modificări adăugate de Martinaș Ioana Maria (Backend API lead):
  - Înregistrare error handlers globali
  - Rate limiting extins (moderation + ingest)
  - Router NLP sentiment
  - Logging configurat
"""

import logging
from contextlib import asynccontextmanager

from app.core.database import engine

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.security import limiter
from app.core.error_handlers import register_error_handlers

# Importuri routere existente
from app.api import (
    audit,
    auth,
    editions,
    export,
    ingest,
    likes,
    moderation,
    preview_books,
    rankings,
    reviews,
    search,
    sentiment,
    users,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio

    from app.services.crawler_runner import run_crawler
    from app.services.json_ingest import ingest_from_crawler_output

    try:
        from app.services.search import configure_search_index

        configure_search_index()
    except Exception:
        pass

    # Load cover image URL cache from crawler JSON files
    from app.services.cover_cache import load_cover_cache
    load_cover_cache()

    # Ingest any existing crawler JSON files into the DB on startup
    asyncio.create_task(ingest_from_crawler_output())
    asyncio.create_task(run_crawler())
    yield
    await engine.dispose()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Platformă Evaluare Literatură Română",
    description=(
        "API pentru evaluarea continuă a edițiilor de literatură română: "
        "catalog, recenzii, ranking-uri transparente, moderare, export și NLP sentiment."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Rate limiting middleware ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# --- Error handlers globali (Martinaș Ioana Maria) ---
register_error_handlers(app)

# --- Routere de autentificare și utilizatori ---
app.include_router(auth.router, prefix="/auth", tags=["Autentificare"])
app.include_router(users.router, prefix="/users", tags=["Utilizatori"])

# --- Routere existente ---
app.include_router(editions.router, prefix="/editions", tags=["Ediții"])
app.include_router(reviews.router, prefix="/editions", tags=["Recenzii"])
app.include_router(reviews.create_router, tags=["Recenzii"])
app.include_router(rankings.router, prefix="/rankings", tags=["Ranking"])
app.include_router(moderation.router, prefix="/moderation", tags=["Moderare"])
app.include_router(export.router, prefix="/export", tags=["Export"])
app.include_router(ingest.router, prefix="/ingest", tags=["Ingestie"])
app.include_router(search.router, tags=["Căutare"])
app.include_router(audit.router, prefix="/audit", tags=["Audit"])

# --- Router gamification (likes și unlocks) ---
app.include_router(likes.router, tags=["Gamification"])

# --- Router preview books ---
app.include_router(preview_books.router, tags=["Preview Books"])

# --- Router NLP sentiment (Martinaș Ioana Maria) ---
app.include_router(
    sentiment.router,
    prefix="/sentiment",
    tags=["NLP Sentiment"],
)


@app.get("/health", tags=["System"])
async def health_check():
    """Endpoint de health check — verifică că aplicația rulează."""
    return {"status": "ok", "service": "literatura-romana-api"}


@app.on_event("startup")
async def on_startup():
    logger.info("Aplicația a pornit. Endpoint-uri disponibile la /docs")