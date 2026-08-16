"""
FastAPI entrypoint. Run with:
    uvicorn app.main:app --reload --port 8000
(from inside backend/, with the venv active)

This is a Phase 0 placeholder that only proves the server boots and CORS is
wired up. Real endpoints (/upload, /status, /result, /export) are added in
Phase 2 and Phase 3.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app = FastAPI(
    title="Automated Meeting Minutes API",
    description="Backend for the ASR & LLM meeting minutes generation capstone project.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "meeting-minutes-backend"}
