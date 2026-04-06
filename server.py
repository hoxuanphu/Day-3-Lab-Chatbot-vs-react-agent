"""
History Chatbot - FastAPI Server
Provides a REST API on top of the existing agent system.
Does NOT modify any existing agent logic.

Usage:
    uvicorn server:app --reload --host 0.0.0.0 --port 8000
"""

import sys
import os
import time
import logging
import asyncio
from typing import Optional

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Ensure project root in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.agent.rag_baseline import RAGBaselineAgent
from src.agent.agent import HistoryAgent
from src.tools.tool_registry import ToolRegistry
from src.core.gemini_provider import GeminiProvider

# ─── Logging ────────────────────────────────────────────────────
# Configure a clean logger that prints to uvicorn's console
log = logging.getLogger("history_chatbot")
log.setLevel(logging.INFO)

# Only add handler if none exist (avoid duplicates on --reload)
if not log.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        "\033[36m%(asctime)s\033[0m | \033[33m%(levelname)s\033[0m | %(message)s",
        datefmt="%H:%M:%S",
    ))
    log.addHandler(handler)


# ─── App ────────────────────────────────────────────────────────
app = FastAPI(title="History Chatbot API", version="1.0.0")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# ─── Models ─────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    question: str
    mode: str = "agent"  # "baseline" or "agent"


class ChatResponse(BaseModel):
    answer: str
    mode: str
    latency_s: float
    error: Optional[str] = None


# ─── Lazy-loaded agents (singleton) ────────────────────────────
_agents = {}


def _get_llm():
    return GeminiProvider(model_name="gemini-2.5-flash")


def get_baseline_agent():
    if "baseline" not in _agents:
        log.info("🔧 Initializing Baseline Agent (RAG)...")
        llm = _get_llm()
        _agents["baseline"] = RAGBaselineAgent(
            llm=llm,
            data_path="data/data.md",
            use_semantic=False,
            top_k=5,
            retrieval_mode="hybrid",
        )
        log.info("✅ Baseline Agent ready!")
    return _agents["baseline"]


def get_history_agent():
    if "agent" not in _agents:
        log.info("🔧 Initializing History Agent (Planner)...")
        llm = _get_llm()
        tool_registry = ToolRegistry(data_path="data/data.md")
        _agents["agent"] = HistoryAgent(llm=llm, tool_registry=tool_registry)
        log.info("✅ History Agent ready!")
    return _agents["agent"]


# ─── Lifecycle Events ───────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    log.info("═" * 50)
    log.info("🏛️  SỬ VIỆT AI — History Chatbot Server")
    log.info("📡 API:  http://localhost:8000/api/chat")
    log.info("🌐 UI:   http://localhost:8000")
    log.info("═" * 50)


# ─── Routes ─────────────────────────────────────────────────────
@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Main chat endpoint — delegates to the existing agent .run() method."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    log.info(f"📩 [{req.mode.upper()}] Question: {req.question[:80]}...")

    start = time.time()
    error = None
    answer = ""

    try:
        if req.mode == "baseline":
            agent = get_baseline_agent()
        else:
            agent = get_history_agent()

        # Run agent in a thread to not block the event loop
        answer = await asyncio.to_thread(agent.run, req.question)

    except Exception as e:
        error = str(e)
        answer = f"Đã xảy ra lỗi: {error}"
        log.error(f"❌ Error: {error}")

    elapsed = round(time.time() - start, 2)
    log.info(f"📤 [{req.mode.upper()}] Answer ({len(answer)} chars) in {elapsed}s")

    return ChatResponse(
        answer=answer,
        mode=req.mode,
        latency_s=elapsed,
        error=error,
    )


@app.get("/api/health")
async def health():
    return {"status": "ok", "agents_loaded": list(_agents.keys())}
