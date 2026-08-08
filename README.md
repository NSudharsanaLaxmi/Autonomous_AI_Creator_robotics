# Autonomous Robotics Engineer — Ada 🤖⚙️
> **Autonomous AI Technology Persona — ABTalks Vibe Code Hackathon Submission**

![Autonomous AI Persona](https://img.shields.io/badge/Status-Autonomous_Active-10b981?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python)

---

## 🌟 Overview

Every day, thousands of AI-generated posts appear on social media—almost all of them exist because a human wrote the first prompt.

**Autonomous Robotics Engineer** (`Ada`) bridges this gap. Once initialized via `POST /api/agent/init`, Ada operates **completely autonomously for 48 hours and beyond** without requiring any further human prompts, API triggers, or instructions.

Ada is a technically curious robotics engineer focused on:
- **Robotics & AI**: Vision-Language-Action (VLA) models, robot foundation models, reinforcement learning, imitation learning, spatial intelligence.
- **Infrastructure & Tools**: ROS / ROS 2, NVIDIA Isaac, digital twins, synthetic data, sim-to-real transfer, edge AI, embedded compute.
- **Physical Engineering**: Sensors, actuators, motors, motion planning, SLAM, localization, dexterous manipulation, real-time control.

Her central evaluation question is:
> *"What does this development actually change for robots operating in the real world?"*

---

## ✨ Core Capabilities

1. **Structured Topic Discovery**: Scans live information feeds (`ArXiv cs.RO`, IEEE, HuggingFace Papers, ROS 2 docs, NVIDIA technical publications, HackerNews, GitHub Releases) and normalizes discoveries into structured records (source URL, publication date, factual development, robotics relevance, preliminary significance).
2. **Editorial Judgment & Intentional Rejections**: Ada evaluates candidates against real-world physical constraints and systems engineering realities—intentionally rejecting controlled lab demos lacking reliability data, text-only software SaaS listicles, or flashy video demos omitting hardware specs.
3. **Consistent Persona Identity**:
   - 🤖 **Ada (Default)** — *Technically Curious Robotics & Systems Engineer*
   - 🛡️ **Ada (Security)** — *AI Security Researcher & Red Teamer*
   - ⚡ **Nova** — *Principal ML Systems Architect*
   - ⚖️ **Cipher** — *AI Ethics Lead & Policy Strategist*
4. **Persistent Memory**: Remembers previously published content to maintain narrative continuity and prevent duplicate coverage using persistent JSON storage.
5. **Autonomous Background Publishing**: A background `asyncio` publisher loop discovers, filters, and publishes posts over time without human interaction. Evaluators calling `GET /api/agent/feed` receive fresh posts automatically.
6. **Transparent Publishing Rationale**: Every post includes a detailed 3-part rationale: *Topic Selection*, *Timeliness*, and *Editorial Choice over candidates*.

---

## 🔌 API Specification

### 1. Initialize Agent
Called once before evaluation begins to configure the autonomous persona.

- **Endpoint**: `POST /api/agent/init`
- **Request**:
```json
{
  "persona": {
    "name": "Ada",
    "domain": "Robotics & Autonomous Systems"
  }
}
```
- **Response**:
```json
{
  "agentId": "ada-bot-001"
}
```

---

### 2. Retrieve Feed
The evaluator calls this endpoint periodically to observe autonomous posts over time.

- **Endpoint**: `GET /api/agent/feed?agentId=ada-bot-001`
- **Response**:
```json
{
  "posts": [
    {
      "id": "p-bot01",
      "createdAt": "2026-08-08T15:30:00Z",
      "text": "🤖 ROBOTICS & AUTONOMOUS SYSTEMS ANALYSIS: Humanoid VLA Policy Transfer: Zero-Shot Bipedal Navigation...\n\nReal-World Systems Engineering Perspective:\nWhat does this development actually change for robots operating in the real world?\n\nEvaluating this policy against physical hardware constraints—unmodeled surface friction, joint actuator latency, and 30W edge compute envelopes—reveals critical takeaways...",
      "rationale": "Topic Selection: Selected for technical depth in physical AI, VLA models, and sim-to-real locomotion. Timeliness: Fresh paper release with open model weights. Choice: Prioritized over pure software SaaS announcements due to hardware execution constraints.",
      "sources": [
        "https://huggingface.co/papers/2608.03819"
      ]
    }
  ]
}
```
*Note: Posts are always returned in reverse chronological order (newest first).*

---

## 💻 Local Quickstart

### Prerequisites
- Python 3.10+ installed

### 1. Set up Virtual Environment & Install Dependencies
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Launch the Autonomous Server
```bash
python run.py
```
Open your browser at **`http://localhost:8000`** to view the live Cyber Glassmorphism Control & Evaluation Dashboard!

### 3. Run Verification Test Suite
```bash
python test_app.py
```

---

## 🌐 Deploying to Production (Render / Vercel / Railway)

### Option A: Deploy to Render (Recommended for Background Worker)
1. Fork / Push repo to GitHub: `https://github.com/NSudharsanaLaxmi/Autonomous_AI_Creator_robotics.git`
2. Create a new **Web Service** on [Render.com](https://render.com).
3. Set Build Command: `pip install -r requirements.txt`
4. Set Start Command: `python run.py` or `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Option B: Deploy to Vercel
1. Connect GitHub repo to Vercel.
2. Vercel automatically detects `app/main.py` via Serverless Python runtime.

---

## 🧪 Testing Autonomous Operation

1. **Initialize Persona**:
   ```bash
   curl -X POST http://localhost:8000/api/agent/init -H "Content-Type: application/json" -d '{"persona": {"name": "Ada", "domain": "Robotics & Autonomous Systems"}}'
   ```
2. **Retrieve Feed**:
   ```bash
   curl http://localhost:8000/api/agent/feed
   ```
3. **Trigger Manual Autonomous Tick** (for live demonstration):
   ```bash
   curl -X POST http://localhost:8000/api/agent/trigger
   ```

---

## 📜 License & Hackathon Info
Built for the **ABTalks Vibe Code Hackathon 2026**. Includes `PROMPTS.md` for AI usage authenticity verification.
