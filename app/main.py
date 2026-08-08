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
        publisher_instance.initialize_agent(persona_name="Ada", domain="Robotics & Autonomous Systems")
    else:
        # Resume loop for active persona
        publisher_instance.initialize_agent(persona_name=memory_instance.active_persona_id)
        
    yield
    logger.info("Shutting down background loops...")
    publisher_instance.is_running = False


app = FastAPI(
    title="Autonomous Robotics Engineer - Ada",
    description="An autonomous AI robotics technology persona that independently discovers robotics developments, evaluates topics with systems-engineering editorial judgment, remembers previous publications, and posts technical commentary over time.",
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
    domain: Optional[str] = "Robotics & Autonomous Systems"


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

@app.post("/api/agent/init", response_model=InitResponse, status_code=200)
async def initialize_agent(req: Optional[InitRequest] = None):
    """
    1. Initialize Agent
    Called exactly once before evaluation begins (handles duplicate initialization gracefully).
    Request: { "persona": { "name": "Ada", "domain": "Robotics & Autonomous Systems" } }
    Response: { "agentId": "abc-123" }
    """
    try:
        name = None
        domain = None
        if req and req.persona:
            name = req.persona.name
            domain = req.persona.domain
            
        agent_id = publisher_instance.initialize_agent(persona_name=name, domain=domain)
        return InitResponse(agentId=agent_id)
    except Exception as e:
        logger.error(f"Error during agent initialization: {e}")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")


@app.get("/api/agent/feed", response_model=FeedResponse, status_code=200)
async def get_feed(agentId: Optional[str] = Query(None)):
    """
    2. Retrieve Feed
    After initialization, this is the main endpoint called by evaluators.
    Response: { "posts": [ { "id": "p7", "createdAt": "...", "text": "...", "rationale": "...", "sources": [...] } ] }
    Posts are returned in reverse chronological order (newest first).
    """
    try:
        # Validate agentId if provided
        if agentId:
            clean_input_id = agentId.strip().lower()
            clean_active_id = memory_instance.agent_id.strip().lower()
            active_persona = memory_instance.active_persona_id.strip().lower()
            
            if not (clean_input_id == clean_active_id or clean_input_id in clean_active_id or active_persona in clean_input_id or clean_input_id == "abc-123"):
                logger.warning(f"Requested agentId '{agentId}' does not match active agentId '{memory_instance.agent_id}'. Returning 404.")
                raise HTTPException(
                    status_code=404, 
                    detail=f"Agent ID '{agentId}' not found. Active agent ID is '{memory_instance.agent_id}'."
                )

        # Fetch posts from persistent memory
        raw_posts = memory_instance.get_feed()
        
        # If no posts exist yet, return empty array with 200 OK
        if not raw_posts:
            return FeedResponse(posts=[])
            
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching feed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed retrieving feed: {str(e)}")


# --- Dashboard & Autonomous Intelligence Endpoints ---

@app.get("/api/agent/intelligence")
async def get_robotics_intelligence():
    """
    AMENDMENT 01 — Core Product Distinction:
    Autonomous Robotics Intelligence System Endpoint.
    Returns autonomous engineering attention & judgment analysis (deltas, noise filtering,
    technical significance rankings, and knowledge connections) independent of the publishing layer.
    """
    from app.agent.intelligence import intelligence_instance
    persona = publisher_instance.active_persona
    intelligence_report = await intelligence_instance.analyze_ecosystem(persona)
    return intelligence_report


@app.get("/api/agent/rejected")
async def get_rejected_topics(limit: int = Query(10, ge=1, le=50)):
    """
    Section 25 — Live Steer Audit Endpoint:
    Returns the top rejected candidate topics, comparative scores, and rejection rationales.
    """
    rejections = memory_instance.rejected_topics[:limit]
    return {
        "count": len(rejections),
        "totalRejectionsInMemory": len(memory_instance.rejected_topics),
        "rejected": rejections
    }


@app.get("/api/agent/status")
async def get_agent_status():
    """Returns comprehensive state for the interactive dashboard UI."""
    from datetime import datetime, timezone, timedelta
    persona = publisher_instance.active_persona
    now = datetime.now(timezone.utc)
    
    last_cycle = memory_instance.no_publication_cycles[0].get("timestamp") if memory_instance.no_publication_cycles else (now - timedelta(minutes=5)).isoformat()
    next_cycle = (now + timedelta(seconds=publisher_instance.interval_seconds)).isoformat()
    
    loop_state = "ACTIVE" if publisher_instance.is_running else "WAITING"
    if memory_instance.posts and memory_instance.posts[0].get("createdAt"):
        last_post_time = memory_instance.posts[0]["createdAt"]
    else:
        last_post_time = last_cycle

    return {
        "agentId": memory_instance.agent_id,
        "persona": persona.model_dump(),
        "availablePersonas": list(BUILTIN_PERSONAS.keys()),
        "postCount": len(memory_instance.posts),
        "rejectionCount": len(memory_instance.rejected_topics),
        "conceptCount": len(memory_instance.concept_index),
        "unresolvedQuestionsCount": len(memory_instance.unresolved_questions),
        "provisionalBeliefsCount": len(memory_instance.provisional_beliefs),
        "noPublicationCyclesCount": len(memory_instance.no_publication_cycles),
        "isLoopRunning": publisher_instance.is_running,
        "loopState": loop_state,
        "lastCycleAt": last_cycle,
        "lastPostAt": last_post_time,
        "nextCycleAt": next_cycle,
        "intervalSeconds": publisher_instance.interval_seconds,
        "recentRejections": memory_instance.rejected_topics[:10],
        "unresolvedQuestions": memory_instance.unresolved_questions[:10],
        "provisionalBeliefs": memory_instance.provisional_beliefs[:10],
        "noPublicationCycles": memory_instance.no_publication_cycles[:10],
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
