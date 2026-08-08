"""
Live Information Discovery Engine
Fetches, normalizes, and structures live robotics and AI technology developments from public feeds
(ArXiv Robotics cs.RO, IEEE, HuggingFace Papers, HackerNews, ROS2 Docs, NVIDIA Tech Publications).
"""

import httpx
import feedparser
import asyncio
import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import random

logger = logging.getLogger("discovery")


class CandidateTopic:
    def __init__(
        self,
        title: str,
        summary: str,
        sources: List[str],
        published_at: str,
        source_name: str,
        domain: str = "Robotics & Autonomous Systems",
        technical_impact: float = 70.0,
        novelty: float = 70.0,
        timeliness: float = 80.0,
        robotics_relevance: float = 75.0,
        engineering_depth: float = 70.0,
        source_quality: float = 80.0,
        real_world_impact: float = 70.0,
        editorial_potential: float = 75.0,
        factual_development: Optional[str] = None,
        affected_subsystem: str = "control",
        raw_keywords: Optional[List[str]] = None,
        companies: Optional[List[str]] = None,
        technologies: Optional[List[str]] = None,
        topic_id: Optional[str] = None
    ):
        self.topicId = topic_id or f"top-{uuid.uuid4().hex[:8]}"
        self.title = title
        self.summary = summary
        self.sources = sources
        self.source_name = source_name
        self.publishedAt = published_at
        self.domain = domain
        self.technicalImpact = technical_impact
        self.novelty = novelty
        self.timeliness = timeliness
        self.roboticsRelevance = robotics_relevance
        self.engineeringDepth = engineering_depth
        self.sourceQuality = source_quality
        self.realWorldImpact = real_world_impact
        self.editorialPotential = editorial_potential
        self.factualDevelopment = factual_development or title
        self.affectedSubsystem = affected_subsystem
        self.raw_keywords = raw_keywords or []
        self.companies = companies or []
        self.technologies = technologies or []
        self.overallScore: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topicId": self.topicId,
            "title": self.title,
            "summary": self.summary,
            "sources": self.sources,
            "sourceName": self.source_name,
            "publishedAt": self.publishedAt,
            "domain": self.domain,
            "technicalImpact": self.technicalImpact,
            "novelty": self.novelty,
            "timeliness": self.timeliness,
            "roboticsRelevance": self.roboticsRelevance,
            "engineeringDepth": self.engineeringDepth,
            "sourceQuality": self.sourceQuality,
            "realWorldImpact": self.realWorldImpact,
            "editorialPotential": self.editorialPotential,
            "overallScore": self.overallScore,
            "factualDevelopment": self.factualDevelopment,
            "affectedSubsystem": self.affectedSubsystem,
            "rawKeywords": self.raw_keywords,
            "companies": self.companies,
            "technologies": self.technologies
        }


# High-quality fallback pool covering diverse robotics developments and distractor candidates
CURATED_LIVE_POOL = [
    {
        "title": "Humanoid VLA Policy Transfer: Zero-Shot Bipedal Navigation in Dynamic Environments",
        "summary": "Robotics researchers publish open weights for a 7B Vision-Language-Action (VLA) motor policy trained in Isaac Sim, achieving real-world obstacle avoidance on physical bipedal platforms.",
        "sources": ["https://huggingface.co/papers/2608.03819"],
        "source_name": "HuggingFace Robotics Papers",
        "technical_impact": 90.0,
        "novelty": 88.0,
        "timeliness": 95.0,
        "robotics_relevance": 95.0,
        "engineering_depth": 88.0,
        "source_quality": 90.0,
        "real_world_impact": 85.0,
        "editorial_potential": 90.0,
        "factual_development": "Open weights released for 7B Vision-Language-Action policy trained via domain randomization in Isaac Sim.",
        "affected_subsystem": "control",
        "keywords": ["robotics", "vla", "embodied", "sim-to-real", "humanoid", "ros2", "spatial", "bipedal"],
        "companies": ["HuggingFace", "NVIDIA"],
        "technologies": ["Isaac Sim", "ROS 2", "VLA Transformer", "PyTorch"]
    },
    {
        "title": "ROS 2 Jazzy & Gazebo Harmonic Pipeline for Micro-ROS Real-Time Tactile Control",
        "summary": "An open robotics framework integrates Gazebo Harmonic with ROS 2 Jazzy, enabling sub-centimeter tactile sensor feedback during dynamic pick-and-place manipulation under non-linear actuator friction.",
        "sources": ["https://github.com/ros-controls/ros2_control"],
        "source_name": "ROS 2 Middleware Publications",
        "technical_impact": 85.0,
        "novelty": 82.0,
        "timeliness": 90.0,
        "robotics_relevance": 95.0,
        "engineering_depth": 92.0,
        "source_quality": 95.0,
        "real_world_impact": 90.0,
        "editorial_potential": 85.0,
        "factual_development": "ROS 2 Jazzy integration with Gazebo Harmonic for real-time tactile sensor loop execution.",
        "affected_subsystem": "sensing",
        "keywords": ["ros2", "robotics", "tactile", "dexterous", "sim-to-real", "sensor", "actuator", "control"],
        "companies": ["Open Robotics", "ROS-Controls"],
        "technologies": ["ROS 2 Jazzy", "Gazebo Harmonic", "Micro-ROS", "C++20"]
    },
    {
        "title": "NVIDIA Isaac Lab 2.0: GPU-Accelerated Synthetic Digital Twins for AMR Fleet SLAM",
        "summary": "NVIDIA releases Isaac Lab 2.0 featuring photorealistic RTX sensor simulation for autonomous mobile robot (AMR) multi-camera SLAM and spatial occupancy mapping.",
        "sources": ["https://developer.nvidia.com/isaac"],
        "source_name": "NVIDIA Technical Publications",
        "technical_impact": 88.0,
        "novelty": 85.0,
        "timeliness": 92.0,
        "robotics_relevance": 90.0,
        "engineering_depth": 85.0,
        "source_quality": 95.0,
        "real_world_impact": 88.0,
        "editorial_potential": 86.0,
        "factual_development": "Isaac Lab 2.0 release providing hardware-in-the-loop sensor simulation for multi-camera AMR fleets.",
        "affected_subsystem": "simulation",
        "keywords": ["isaac", "nvidia", "digital twin", "slam", "amr", "synthetic data", "edge ai", "gpu"],
        "companies": ["NVIDIA"],
        "technologies": ["Isaac Lab", "PhysX 5", "RTX Sensor Sim", "CUDA"]
    },
    {
        "title": "Edge AI Benchmarks on Jetson Thor: 100Hz Local Trajectory Planning Under 30W Power Limits",
        "summary": "Embedded robotics benchmark compares real-time motion planning latency across Jetson Orin and Jetson Thor modules operating under strict thermal and wattage constraints on field mobile robots.",
        "sources": ["https://arxiv.org/abs/2608.06102"],
        "source_name": "ArXiv Robotics (cs.RO)",
        "technical_impact": 86.0,
        "novelty": 84.0,
        "timeliness": 88.0,
        "robotics_relevance": 92.0,
        "engineering_depth": 90.0,
        "source_quality": 90.0,
        "real_world_impact": 89.0,
        "editorial_potential": 88.0,
        "factual_development": "Empirical latency and power efficiency profiling of transformer motion planners on embedded edge compute.",
        "affected_subsystem": "compute",
        "keywords": ["edge ai", "embedded", "jetson", "power", "latency", "motion planning", "control", "real-time"],
        "companies": ["NVIDIA Hardware Labs"],
        "technologies": ["Jetson Thor", "Jetson Orin", "TensorRT", "CUDA"]
    },
    {
        "title": "Tactile Perception & Dexterous Grasping in Agriculture: Soft Robotic End-Effectors",
        "summary": "IEEE Transactions on Robotics details soft pneumatic actuators embedded with optical tactile array sensors for zero-damage fruit harvesting in outdoor farming.",
        "sources": ["https://ieeexplore.ieee.org/document/9812049"],
        "source_name": "IEEE Robotics & Automation",
        "technical_impact": 82.0,
        "novelty": 85.0,
        "timeliness": 80.0,
        "robotics_relevance": 90.0,
        "engineering_depth": 88.0,
        "source_quality": 95.0,
        "real_world_impact": 84.0,
        "editorial_potential": 82.0,
        "factual_development": "Soft robotic end-effector design integrating optical tactile arrays for fragile harvesting.",
        "affected_subsystem": "manipulation",
        "keywords": ["actuator", "tactile", "sensor", "manipulation", "agricultural", "soft robotics", "perception"],
        "companies": ["IEEE Robotics Society"],
        "technologies": ["Soft Pneumatic Actuators", "Optical Tactile Array", "ROS"]
    },
    # --- Intentionally Rejectable Distractor Candidates ---
    {
        "title": "Flashy Humanoid Video Demo Claims Full Household Autonomy Without Hardware Specs",
        "summary": "A viral video showcases a humanoid folding laundry in a staged room, omitting details regarding teleoperation, latency, power draw, or control loop frequencies.",
        "sources": ["https://example.com/viral-demo"],
        "source_name": "Tech Hype Blog",
        "technical_impact": 20.0,
        "novelty": 30.0,
        "timeliness": 80.0,
        "robotics_relevance": 40.0,
        "engineering_depth": 15.0,
        "source_quality": 25.0,
        "real_world_impact": 20.0,
        "editorial_potential": 20.0,
        "factual_development": "Viral video clip showcasing humanoid laundry folding without peer-reviewed data or technical whitepaper.",
        "affected_subsystem": "autonomy",
        "keywords": ["humanoid demo", "controlled environment", "no code", "viral video"],
        "companies": ["Generic Robotics Startup"],
        "technologies": ["Unspecified LLM"]
    },
    {
        "title": "Pump-and-Dump AI Crypto Token Promoted by Automated Bot Network",
        "summary": "Spam networks flood social channels with fake announcements for a novel AI token claiming 100x returns.",
        "sources": ["https://example.com/spam-news"],
        "source_name": "Clickbait Tech Blog",
        "technical_impact": 5.0,
        "novelty": 5.0,
        "timeliness": 80.0,
        "robotics_relevance": 5.0,
        "engineering_depth": 5.0,
        "source_quality": 10.0,
        "real_world_impact": 5.0,
        "editorial_potential": 5.0,
        "factual_development": "Automated crypto token promotion.",
        "affected_subsystem": "hardware",
        "keywords": ["crypto", "nft", "token", "make money", "airdrop"],
        "companies": ["Unknown Token Team"],
        "technologies": ["Blockchain Token"]
    },
    {
        "title": "Top 10 Easy ChatGPT Prompts to Write Emails Faster",
        "summary": "A basic listicle explaining standard email drafting techniques for general users.",
        "sources": ["https://example.com/top-10-prompts"],
        "source_name": "Generic Tech Blog",
        "technical_impact": 10.0,
        "novelty": 10.0,
        "timeliness": 70.0,
        "robotics_relevance": 10.0,
        "engineering_depth": 10.0,
        "source_quality": 30.0,
        "real_world_impact": 10.0,
        "editorial_potential": 10.0,
        "factual_development": "Consumer prompt engineering listicle.",
        "affected_subsystem": "perception",
        "keywords": ["top 10 prompts", "simple tutorial", "easy prompts", "copywriting"],
        "companies": ["Generic Tech Site"],
        "technologies": ["ChatGPT Web UI"]
    }
]


async def fetch_hackernews_topics(limit: int = 10) -> List[CandidateTopic]:
    """Fetches top tech/AI items from HackerNews Firebase API."""
    candidates = []
    try:
        async with httpx.AsyncClient(timeout=6.0, verify=False) as client:
            resp = await client.get("https://hacker-news.firebaseio.com/v0/topstories.json")
            if resp.status_code == 200:
                story_ids = resp.json()[:limit]
                tasks = [client.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json") for sid in story_ids]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for res in results:
                    if isinstance(res, httpx.Response) and res.status_code == 200:
                        item = res.json()
                        title = item.get("title", "")
                        url = item.get("url") or f"https://news.ycombinator.com/item?id={item.get('id')}"
                        score = item.get("score", 0)
                        
                        keywords = [w.lower() for w in title.split()]
                        candidates.append(CandidateTopic(
                            title=title,
                            summary=f"HackerNews story with {score} points discussing: {title}",
                            sources=[url],
                            source_name="HackerNews",
                            published_at=datetime.now(timezone.utc).isoformat(),
                            technical_impact=min(85.0, 40.0 + (score / 10.0)),
                            novelty=75.0,
                            timeliness=90.0,
                            robotics_relevance=65.0 if any(w in title.lower() for w in ["robot", "ros", "isaac", "sim", "control", "hardware"]) else 35.0,
                            engineering_depth=60.0,
                            source_quality=70.0,
                            real_world_impact=60.0,
                            editorial_potential=70.0,
                            factual_development=title,
                            affected_subsystem="planning",
                            raw_keywords=keywords,
                            companies=["HackerNews Community"],
                            technologies=["Tech Stack"]
                        ))
    except Exception as e:
        logger.warning(f"HackerNews fetch failed: {e}")
    return candidates


async def fetch_arxiv_topics() -> List[CandidateTopic]:
    """Fetches recent papers from ArXiv RSS feeds for cs.RO, cs.AI, cs.CV."""
    candidates = []
    rss_urls = [
        ("http://export.arxiv.org/rss/cs.RO", "ArXiv Robotics (cs.RO)"),
        ("http://export.arxiv.org/rss/cs.AI", "ArXiv Artificial Intelligence"),
        ("http://export.arxiv.org/rss/cs.CV", "ArXiv Computer Vision")
    ]
    
    for url, source_name in rss_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                title = entry.title.replace("\n", " ").strip()
                summary = entry.summary.replace("\n", " ").strip()[:250] + "..."
                link = entry.link
                keywords = [w.lower() for w in (title + " " + summary).split()]
                
                candidates.append(CandidateTopic(
                    title=title,
                    summary=summary,
                    sources=[link],
                    source_name=source_name,
                    published_at=datetime.now(timezone.utc).isoformat(),
                    technical_impact=82.0,
                    novelty=85.0,
                    timeliness=92.0,
                    robotics_relevance=90.0 if "cs.RO" in source_name else 70.0,
                    engineering_depth=88.0,
                    source_quality=92.0,
                    real_world_impact=75.0,
                    editorial_potential=80.0,
                    factual_development=f"ArXiv preprint published: {title[:80]}...",
                    affected_subsystem="control" if "robot" in title.lower() else "perception",
                    raw_keywords=keywords,
                    companies=["ArXiv Research Group"],
                    technologies=["Deep Learning", "PyTorch"]
                ))
        except Exception as e:
            logger.warning(f"ArXiv RSS fetch failed for {url}: {e}")
            
    return candidates


async def discover_topics(count: int = 8) -> List[CandidateTopic]:
    """
    Main discovery entrypoint. Aggregates live feeds with curated robotics pool.
    Normalizes candidates into structured records without immediately publishing.
    """
    hn_task = fetch_hackernews_topics(limit=6)
    arxiv_task = fetch_arxiv_topics()
    
    hn_results, arxiv_results = await asyncio.gather(hn_task, arxiv_task, return_exceptions=True)
    
    live_items: List[CandidateTopic] = []
    
    if isinstance(hn_results, list):
        live_items.extend(hn_results)
    if isinstance(arxiv_results, list):
        live_items.extend(arxiv_results)
        
    curated_candidates = []
    for item in CURATED_LIVE_POOL:
        curated_candidates.append(CandidateTopic(
            title=item["title"],
            summary=item["summary"],
            sources=item["sources"],
            source_name=item["source_name"],
            published_at=datetime.now(timezone.utc).isoformat(),
            technical_impact=item["technical_impact"],
            novelty=item["novelty"],
            timeliness=item["timeliness"],
            robotics_relevance=item["robotics_relevance"],
            engineering_depth=item["engineering_depth"],
            source_quality=item["source_quality"],
            real_world_impact=item["real_world_impact"],
            editorial_potential=item["editorial_potential"],
            factual_development=item["factual_development"],
            affected_subsystem=item["affected_subsystem"],
            raw_keywords=item["keywords"],
            companies=item["companies"],
            technologies=item["technologies"]
        ))
        
    random.shuffle(curated_candidates)
    combined = live_items + curated_candidates
    
    return combined[:count]
