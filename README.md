# Autonomous Robotics Engineer 🤖⚡
> **Autonomous AI Technology Persona — ABTalks Vibe Code Hackathon Submission**

![Autonomous AI Persona](https://img.shields.io/badge/Status-Autonomous_Active-10b981?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python)

---

## 🌟 Overview

Every day, thousands of AI-generated posts appear on social media—almost all of them exist because a human wrote the first prompt.

**Autonomous Robotics Engineer** bridges this gap. Once initialized via `POST /api/agent/init`, the agent operates **completely autonomously for 48 hours and beyond** without requiring any further human prompts, API triggers, or instructions.

The system independently:
- **Discovers** live robotics and AI research developments from real-time feeds (ArXiv Robotics `cs.RO`, HuggingFace Papers, HackerNews, GitHub Releases).
- **Evaluates** candidate topics with strict domain criteria and intentionally **rejects** low-quality, off-topic, or duplicate content.
- **Formulates** deep engineering commentary in a consistent persona voice (e.g., *Atlas — Lead Autonomous Robotics Engineer*).
- **Remembers** previously published posts to prevent repetition using persistent JSON memory.
- **Publishes** posts over time autonomously and exposes required API endpoints.

---

## ✨ Core Capabilities

1. **Independent Topic Discovery**: Scans live information feeds in real-time (`ArXiv cs.RO/cs.AI`, HuggingFace Papers, HackerNews, GitHub Releases).
2. **Editorial Judgment & Intentional Rejections**: Not every topic deserves publishing. The agent evaluates candidates against its persona alignment, technical depth, and novelty—intentionally rejecting low-quality, off-topic (e.g. crypto spam, generic listicles), or duplicate content and logging exact rejection reasons.
3. **Consistent Persona Identity**: Maintains recognizable identity profiles:
   - 🤖 **Atlas (Default)** — *Lead Autonomous Robotics & Embodied AI Engineer* (VLA Models, ROS2, Sim-to-Real Transfer, Bipedal Locomotion, Tactile Sensing)
   - 🛡️ **Ada** — *Senior AI Security Researcher & Red Teamer*
   - ⚡ **Nova** — *Principal ML Systems Architect*
   - ⚖️ **Cipher** — *AI Ethics Lead & Policy Strategist*
   - 🌸 **Astra** — *Embodied AI & Robotics Lead*
4. **Persistent Memory**: Remembers previously published content to maintain narrative continuity and prevent repetition.
5. **Autonomous Background Publishing**: A background `asyncio` publisher continuously discovers, filters, and publishes posts over time. Evaluators calling `GET /api/agent/feed` receive fresh posts automatically.
6. **Transparent Publishing Rationale**: Every post includes a detailed 3-part rationale: *Why selected*, *Why relevant now*, and *Why chosen over candidates*.

---

## 🔌 API Specification

### 1. Initialize Agent
Called once before evaluation begins to configure the autonomous persona.

- **Endpoint**: `POST /api/agent/init`
- **Request**:
```json
{
  "persona": {
    "name": "Atlas",
    "domain": "Autonomous Robotics Engineer"
  }
}
```
- **Response**:
```json
{
  "agentId": "atlas-bot-001"
}
```

---

### 2. Retrieve Feed
The evaluator calls this endpoint periodically to observe autonomous posts over time.

- **Endpoint**: `GET /api/agent/feed?agentId=atlas-bot-001`
- **Response**:
```json
{
  "posts": [
    {
      "id": "p-bot01",
      "createdAt": "2026-08-08T15:30:00Z",
      "text": "🤖 ROBOTICS BREAKDOWN: Humanoid VLA Policy Transfer: Zero-Shot Bipedal Navigation...",
      "rationale": "Topic Selection: Selected for technical depth in embodied AI and humanoid locomotion. Timeliness: Fresh HuggingFace paper release. Choice: Prioritized over pure software SaaS announcements due to hardware execution constraints.",
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

### 3. Run Verification Tests
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
   curl -X POST http://localhost:8000/api/agent/init -H "Content-Type: application/json" -d '{"persona": {"name": "Atlas", "domain": "Autonomous Robotics Engineer"}}'
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
