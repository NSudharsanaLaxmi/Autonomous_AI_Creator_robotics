"""
FastAPI Server & REST API Entrypoint
Exposes required endpoints:
  - POST /api/agent/init
  - GET /api/agent/feed
and dashboard state endpoints.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from app.agent.memory import memory_instance
from app.agent.publisher import publisher_instance
from app.agent.persona import BUILTIN_PERSONAS

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle startup & shutdown handler."""
    logger.info("Initializing Autonomous AI Creator application...")
    # Initialize default agent if feed is empty
    if len(memory_instance.posts) == 0:
        publisher_instance.initialize_agent(persona_name="Ada", domain="AI Security")
    else:
        # Resume loop for active persona
        publisher_instance.initialize_agent(persona_name=memory_instance.active_persona_id)
        
    yield
    logger.info("Shutting down background loops...")
    publisher_instance.is_running = False


app = FastAPI(
    title="Autonomous AI Creator",
    description="An autonomous AI and technology persona that independently discovers topics, applies editorial judgment, uses memory, and publishes content over time.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for cross-origin evaluation and deployment flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request / Response Pydantic Models ---

class PersonaInitData(BaseModel):
    name: Optional[str] = "Ada"
    domain: Optional[str] = "AI Security"


class InitRequest(BaseModel):
    persona: Optional[PersonaInitData] = Field(default_factory=PersonaInitData)


class InitResponse(BaseModel):
    agentId: str


class FeedPost(BaseModel):
    id: str
    createdAt: str
    text: str
    rationale: str
    sources: List[str]


class FeedResponse(BaseModel):
    posts: List[FeedPost]


# --- Required Hackathon API Endpoints ---

@app.post("/api/agent/init", response_model=InitResponse)
async def initialize_agent(req: Optional[InitRequest] = None):
    """
    1. Initialize Agent
    Called exactly once before evaluation begins.
    Request: { "persona": { "name": "Ada", "domain": "AI Security" } }
    Response: { "agentId": "abc-123" }
    """
    name = None
    domain = None
    if req and req.persona:
        name = req.persona.name
        domain = req.persona.domain
        
    agent_id = publisher_instance.initialize_agent(persona_name=name, domain=domain)
    return InitResponse(agentId=agent_id)


@app.get("/api/agent/feed", response_model=FeedResponse)
async def get_feed(agentId: Optional[str] = Query(None)):
    """
    2. Retrieve Feed
    After initialization, this is the main endpoint called by evaluators.
    Response: { "posts": [ { "id": "p7", "createdAt": "...", "text": "...", "rationale": "...", "sources": [...] } ] }
    Posts are returned in reverse chronological order (newest first).
    """
    # Fetch posts from persistent memory
    raw_posts = memory_instance.get_feed()
    
    formatted_posts = []
    for p in raw_posts:
        formatted_posts.append(FeedPost(
            id=str(p.get("id", "")),
            createdAt=str(p.get("createdAt", "")),
            text=str(p.get("text", "")),
            rationale=str(p.get("rationale", "")),
            sources=list(p.get("sources", []))
        ))
        
    return FeedResponse(posts=formatted_posts)


# --- Dashboard Support Endpoints ---

@app.get("/api/agent/status")
async def get_agent_status():
    """Returns comprehensive state for the interactive dashboard UI."""
    persona = publisher_instance.active_persona
    return {
        "agentId": memory_instance.agent_id,
        "persona": persona.model_dump(),
        "availablePersonas": list(BUILTIN_PERSONAS.keys()),
        "postCount": len(memory_instance.posts),
        "rejectionCount": len(memory_instance.rejected_topics),
        "conceptCount": len(memory_instance.concept_index),
        "isLoopRunning": publisher_instance.is_running,
        "recentRejections": memory_instance.rejected_topics[:10],
        "conceptIndex": memory_instance.concept_index[:20]
    }


@app.post("/api/agent/trigger")
async def trigger_autonomous_tick(background_tasks: BackgroundTasks):
    """Triggers an immediate autonomous tick (discovery -> editorial filter -> post)."""
    new_post = await publisher_instance.execute_autonomous_tick()
    if new_post:
        return {"status": "published", "post": new_post}
    return {"status": "rejections_only", "message": "Candidates evaluated but rejected by editorial judgment."}


# --- Static Files & Dashboard UI ---

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def serve_dashboard():
    """Serves main interactive dashboard HTML UI."""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"status": "running", "docs": "/docs", "feed": "/api/agent/feed"})
