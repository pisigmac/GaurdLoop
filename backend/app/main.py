from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from app.core.database import engine, Base
from app.middleware.rate_limit import RateLimitMiddleware
from app.core.redis import close_redis
import app.models
from app.api import tasks, agents, scores, pii, browser, webhooks, sse, billing, api_keys

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.organization import Organization

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        res = await session.execute(select(Organization).where(Organization.id == "default-org"))
        if not res.scalar_one_or_none():
            org = Organization(id="default-org", name="Default Organization", slug="default-org")
            session.add(org)
            await session.commit()

    yield
    # Shutdown
    await engine.dispose()
    await close_redis()

app = FastAPI(
    title="GuardLoop API",
    description="Agent Trust & Orchestration Layer. Multi-agent safety platform for Cursor, Claude Code, GitHub Copilot, and custom agents.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:33000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:33000",
        "https://guardloop.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(round(time.time() - start, 4))
    return response

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )

# Health
@app.get("/health")
async def health():
    return {"status": "ok", "service": "guardloop-api", "version": "1.0.0"}

# Routes
app.include_router(tasks.router)
app.include_router(agents.router)
app.include_router(scores.router)
app.include_router(pii.router)
app.include_router(browser.router)
app.include_router(webhooks.router)
app.include_router(sse.router)
app.include_router(billing.router)
app.include_router(api_keys.router)

@app.get("/")
async def root():
    return {
        "name": "GuardLoop",
        "version": "1.0.0",
        "description": "Agent Trust & Orchestration Layer",
        "docs": "/docs",
        "health": "/health",
    }
