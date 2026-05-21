from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers.search import router as search_router

app = FastAPI(
    title="AI Agent Visualizer API",
    version="1.0.0",
    description="FastAPI backend cho 8-Puzzle và Vacuum",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "supabase": settings.supabase_enabled,
    }
