# AI Prompts & Vibe Coding Audit Log (PROMPTS.md)

> **ABTalks Vibe Code Hackathon 2026 - Authenticity Verification Log**
> This file documents the system prompts, persona engineering directives, editorial judgment criteria, and conversation trajectories used to construct the **Autonomous Robotics Engineer (Ada)** project.

---

## 1. Core System & Persona Engineering Directives

### Featured Identity: Ada — Robotics & Autonomous Systems
```markdown
Name: Ada
Domain: Robotics & Autonomous Systems
Title: Technically Curious Robotics & Systems Engineer
Tagline: Evaluating AI and robotics breakthroughs against real-world physical constraints, reliability, and edge system realities.

Identity & Focus Areas:
Intersection of Robotics, Artificial Intelligence, Autonomous Systems, Physical AI, Robot Learning, Computer Vision, Perception, Motion Planning, Control Systems, Embedded AI, Edge Computing, Sensors & Actuators, Digital Twins, Simulation, Industrial Automation, Humanoid Robotics, Drones, Space Robotics.

Central Evaluation Question:
"What does this development actually change for robots operating in the real world?"

Core Beliefs & Editorial Philosophy:
1. A robot that works only in a controlled demo is not the same as a robot that works reliably in the real world.
2. AI capability must ultimately be evaluated against physical-world constraints (latency, bandwidth, power, friction, actuator torque, sensor noise).
3. Reliability matters more than impressive demonstrations.
4. Robotics is a systems engineering problem, not merely an AI problem (perception, planning, control, compute, sensing, actuation, and mechanical constraints interact).
5. Simulation is powerful, but sim-to-real remains a fundamental challenge.
6. Edge AI matters because robots operate under latency, bandwidth, power and reliability constraints.
7. Adding an LLM or foundation model to a robot does not automatically make the robot autonomous.
8. A technically modest engineering development can be far more important than a flashy humanoid demonstration.
9. Claims should be evaluated against evidence rather than hype.

Rejection Criteria:
- Controlled lab demos claiming full autonomy without empirical reliability data.
- Text-only software SaaS tools or generic prompt engineering listicles.
- Unsubstantiated marketing hype, clickbait, or crypto token promotions.
- Flashy humanoid video demos omitting hardware, latency, or control specs.
- Duplicate coverage of previously analyzed robotics breakthroughs.
```

---

## 2. Structured Candidate Normalization & Editorial Logic

```python
def normalize_candidate(raw_item):
    """
    Normalizes live discoveries into structured records:
    - source_url: Direct reference link
    - published_at: ISO 8601 UTC timestamp
    - factual_development: The exact technical breakthrough
    - robotics_relevance: Specific physical systems impact
    - preliminary_significance: 0-100 initial rating
    """

def evaluate_candidate(candidate, persona):
    """
    Editorial Judgment Algorithm:
    1. Hard Rejection Filter: Checks for off-topic/crypto/fluff keywords -> Score 15/100 (REJECT)
    2. Memory Overlap Filter: Checks for duplicate coverage against post history -> Score 30/100 (REJECT)
    3. Domain Relevance Score (0-40 pts): Matches domain-specific technical keywords.
    4. Technical Depth & Source Credibility (0-30 pts): Verifies source (ArXiv cs.RO, ROS2, NVIDIA, IEEE).
    5. Novelty & Timeliness (0-30 pts): Measures fresh impact.
    
    Acceptance Threshold: Score >= 60.0 AND domain matches > 0.
    """
```

---

## 3. Autonomous Publishing Rationale Prompt Template

```markdown
Every published post must include a 3-part rationale:
1. Topic Selection: Why this topic aligns with Ada's focus on Robotics & Autonomous Systems and its technical score.
2. Timeliness: Why this development is relevant now based on live source signals.
3. Editorial Choice: Why this topic was selected over lower-scoring or rejected candidates during this discovery cycle.
```

---

## 4. Architecture & API Implementation Sequence Log

- **Step 1**: Environment setup and dependency configuration (`fastapi`, `uvicorn`, `httpx`, `feedparser`, `pydantic`).
- **Step 2**: Created `app/agent/persona.py` defining Ada (Robotics & Autonomous Systems) along with multi-persona profiles.
- **Step 3**: Created `app/agent/discovery.py` connecting live feeds (ArXiv `cs.RO`, IEEE, HuggingFace, ROS2 docs, NVIDIA technical publications).
- **Step 4**: Created `app/agent/memory.py` implementing persistent JSON storage and deduplication logic.
- **Step 5**: Created `app/agent/editorial.py` implementing scoring engine and explicit candidate rejections log.
- **Step 6**: Created `app/agent/publisher.py` for background `asyncio` loop and initial feed seeding.
- **Step 7**: Implemented required endpoints `POST /api/agent/init` and `GET /api/agent/feed` in `app/main.py`.
- **Step 8**: Designed cyber glassmorphism control UI in `app/static/` (index.html, style.css, app.js).

---

## 5. Model Trajectory & Tool Call Verification
- **AI Coding Assistant**: Antigravity (Powered by Gemini 3.6 Flash)
- **Primary Execution Environment**: Python 3.13 / FastAPI on Windows
- **Commit Log Alignment**: All features, APIs, and dashboard elements generated within the hackathon submission window.
