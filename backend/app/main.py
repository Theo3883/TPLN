from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import editions, reviews, rankings, audit, export, search, ingest, moderation
from app.core.database import engine
from app.core.security import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio
    from app.services.search import get_search_client
    from app.services.crawler_runner import run_crawler
    from app.core.config import settings
    try:
        client = get_search_client()
        client.create_index(settings.meilisearch_index, {"primaryKey": "id"})
    except Exception:
        pass
    asyncio.create_task(run_crawler())
    yield
    await engine.dispose()


app = FastAPI(
    title="Platformă Evaluare Literatură Română",
    description="API pentru catalog, recenzii și ranking-uri de literatură română",
    version="0.1.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(search.router, prefix="", tags=["search"])
app.include_router(editions.router, prefix="/editions", tags=["editions"])
app.include_router(reviews.router, prefix="/editions", tags=["reviews"])
app.include_router(reviews.create_router, prefix="", tags=["reviews"])
app.include_router(rankings.router, prefix="/rankings", tags=["rankings"])
app.include_router(audit.router, prefix="/audit", tags=["audit"])
app.include_router(export.router, prefix="/export", tags=["export"])
app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(moderation.router, prefix="/moderation", tags=["moderation"])


@app.get("/")
async def root():
    return {"message": "Platformă Evaluare Literatură Română", "docs": "/docs"}
