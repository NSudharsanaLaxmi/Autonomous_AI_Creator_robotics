# Implementation Plan: Genuine Live Web Application for FORGE (Autonomous Robotics Engineer)

## Overview
Enhance the existing live web application frontend and API integration to provide an evaluator-ready, high-telemetry engineering intelligence dashboard for **FORGE — Autonomous Robotics Engineer (Ada)**. 

The live web application connects directly to the persistent backend database (`data/agent_memory.json`), real-time status endpoints (`/api/agent/status`, `/api/agent/feed`, `/api/agent/rejected`, `/api/agent/intelligence`), and the autonomous background publisher (`app/agent/publisher.py`).

---

## Key Dashboard Capabilities

### 1. Hero & Engineering Identity
- **Brand Title**: `FORGE — Autonomous Robotics Engineer`
- **Hero Description**: *"An AI robotics engineer that independently watches the physical-AI ecosystem, decides what deserves engineering attention, and develops an evolving technical point of view."*
- **Robotics Engineering Aesthetics**: Styled with high-contrast dark telemetry theme (`Perception`, `Planning`, `Control`, `Manipulation`, `Simulation`, `Edge AI`, `Digital Twins`).

### 2. Autonomous Engine Telemetry Panel
- **Status Indicator**: Dynamic real-time state badge (`ACTIVE` / `WAITING` / `INVESTIGATING` / `PUBLISHING` / `NO PUBLICATION`).
- **Cycle Telemetry**:
  - `Last Autonomous Cycle`: UTC timestamp
  - `Next Scheduled Cycle`: UTC timestamp
  - `Topics Observed`: Count
  - `Intentional Rejections`: Count
  - `Published Posts`: Count

### 3. Live Published Feed
- Connected directly to `GET /api/agent/feed?agentId=ada-bot-001`.
- Renders:
  - 4-Part Engineering Post Structure (`HOOK` $\rightarrow$ `ENGINEERING INTERPRETATION` $\rightarrow$ `REAL-WORLD LIMITATION` $\rightarrow$ `ENGINEERING TAKEAWAY`).
  - Dynamic 4-Question Rationale box explaining topic choice over real competitors in that cycle.
  - Verified primary source links with domain labels.

### 4. Decision Transparency View ("How FORGE Decides")
- Displays structured decision metadata (`StructuredDecisionTrace`, `competitiveDecisionRecord`, candidate scores).
- Displays Pre-Publication Audit Gate verification results (7 checks: `FACTUALITY`, `NOVELTY`, `RELEVANCE`, `ORIGINALITY`, `PERSONA`, `EVIDENCE`, `RESTRAINT`).

### 5. Persistent Memory View
- Displays memory pools from backend memory:
  - `Observed Topics`
  - `Rejected Candidates`
  - `Unresolved Curiosity Questions` (Amendment 03)
  - `Provisional Engineering Beliefs` (Amendment 05)

### 6. Read-Only Auto-Polling & Failure Gracefulness
- Auto-refreshes telemetry every 6 seconds using read-only GET requests.
- Honest empty state: *"FORGE is observing the robotics ecosystem. No publication has met its editorial threshold yet."*
- Graceful offline/error banner if backend becomes unreachable.

---

## Proposed File Changes

### Frontend Assets
- [`app/static/index.html`](file:///C:/Users/Sudharsana/.gemini/antigravity/scratch/autonomous-ai-creator/app/static/index.html): Update HTML layout to include telemetry hero, autonomous indicator, 4 tabs (Live Feed, Decision Trace, Memory View, API Inspector).
- [`app/static/style.css`](file:///C:/Users/Sudharsana/.gemini/antigravity/scratch/autonomous-ai-creator/app/static/style.css): Update CSS with modern dark glassmorphism telemetry design system.
- [`app/static/app.js`](file:///C:/Users/Sudharsana/.gemini/antigravity/scratch/autonomous-ai-creator/app/static/app.js): Update JavaScript logic to fetch live telemetry, render 4 tabs, display decision trace, curiosity questions, belief evolution, and auto-poll without triggering generation.

### Backend Enhancements
- [`app/main.py`](file:///C:/Users/Sudharsana/.gemini/antigravity/scratch/autonomous-ai-creator/app/main.py): Update `/api/agent/status` to include last tick timestamp, next cycle timestamp, current autonomous loop state, unresolved curiosity questions, and provisional beliefs.

---

## Verification Plan

### Automated Integration Tests
- Run `.\venv\Scripts\python test_app.py` to verify all 22 automated integration tests pass with 100% success.

### Manual Verification
- Start FastAPI app on `http://127.0.0.1:8000`.
- Open `http://127.0.0.1:8000` in browser to verify dashboard UI, tabs, telemetry, decision trace, and memory views.
