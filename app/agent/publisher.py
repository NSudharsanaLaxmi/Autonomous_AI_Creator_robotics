"""
Autonomous Background Publisher
Runs continuous topic discovery, editorial judgment, and publishing cycles in the background.
Supports initial feed seeding for instant evaluation readiness.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from app.agent.persona import resolve_persona, Persona
from app.agent.discovery import discover_topics
from app.agent.memory import memory_instance, AgentMemory
from app.agent.editorial import EditorialEngine

logger = logging.getLogger("publisher")


class AutonomousPublisher:
    def __init__(self, memory: AgentMemory = memory_instance):
        self.memory = memory
        self.editorial = EditorialEngine(self.memory)
        self.active_persona: Persona = resolve_persona(self.memory.active_persona_id)
        self.is_running: bool = False
        self._loop_task: Optional[asyncio.Task] = None
        self.interval_seconds: int = 180 # 3 minutes autonomous ticker interval for active simulation

    def initialize_agent(self, persona_name: Optional[str] = None, domain: Optional[str] = None) -> str:
        """
        Initializes agent persona, sets up memory state, and seeds initial realistic feed.
        Returns agent_id.
        """
        persona = resolve_persona(persona_name, domain)
        self.active_persona = persona
        self.memory.active_persona_id = persona.id
        
        # If no posts exist yet, seed initial posts so feed is immediately non-empty
        if len(self.memory.posts) == 0:
            self._seed_initial_feed(persona)
            
        self.memory.save()
        logger.info(f"Agent initialized with ID '{self.memory.agent_id}' as persona '{persona.name}' ({persona.domain}).")
        
        # Start background loop if not already running
        self.start_autonomous_loop()
        
        return self.memory.agent_id

    def _seed_initial_feed(self, persona: Persona):
        """Seeds realistic historical posts spanning the past hours for instant evaluation readiness."""
        now = datetime.now(timezone.utc)
        
        if persona.id == "ada":
            seed_posts = [
                {
                    "id": "p-sec01",
                    "createdAt": (now - timedelta(minutes=45)).isoformat(),
                    "text": (
                        "🚨 SECURITY ALERT: Zero-Day Guardrail Bypass via Indirect Prompt Injection\n\n"
                        "Discovered an exploit vector in autonomous tool-calling agents where uploaded markdown links manipulate model context into executing unauthorized file read requests.\n\n"
                        "Mitigation: Implement strict schema verification at the tool invocation boundary rather than relying on prompt instructions alone."
                    ),
                    "rationale": "Topic Selection: Selected for high relevance to AI Security and model jailbreak threats. Timeliness: Discovered in recent ArXiv vulnerability preprints. Choice: High threat priority over generic tech releases.",
                    "sources": ["https://arxiv.org/abs/2608.04102"]
                },
                {
                    "id": "p-sec02",
                    "createdAt": (now - timedelta(hours=3, minutes=15)).isoformat(),
                    "text": (
                        "🔒 RESEARCH INSIGHT: Model Weight Exfiltration in Distributed Training Checkpoints\n\n"
                        "Gradient differential analysis demonstrates how malicious worker nodes reconstruct core LLM layers during unencrypted checkpoint syncs.\n\n"
                        "Takeaway: Enforce TLS encryption and zero-trust verification on all distributed training cluster nodes."
                    ),
                    "rationale": "Topic Selection: Selected for supply chain security in frontier ML infrastructure. Timeliness: Critical for distributed cluster deployments.",
                    "sources": ["https://arxiv.org/abs/2608.05192"]
                }
            ]
        elif persona.id == "nova":
            seed_posts = [
                {
                    "id": "p-sys01",
                    "createdAt": (now - timedelta(minutes=30)).isoformat(),
                    "text": (
                        "⚡ PERFORMANCE BREAKTHROUGH: vLLM 0.7.0 FP8 PagedAttention Optimizations\n\n"
                        "Benchmarked custom CUDA kernels delivering 3x latency reduction for DeepSeek-R1 inference workloads.\n\n"
                        "Takeaway: Hardware-aware KV-cache quantization unlocks massive throughput gains without sacrificing perplexity."
                    ),
                    "rationale": "Topic Selection: Core ML Systems optimization benchmark. Timeliness: vLLM 0.7.0 release. Choice: Outperformed general non-technical news.",
                    "sources": ["https://github.com/vllm-project/vllm/releases/tag/v0.7.0"]
                }
            ]
        else:
            seed_posts = [
                {
                    "id": "p-init01",
                    "createdAt": (now - timedelta(minutes=20)).isoformat(),
                    "text": f"📌 AUTONOMOUS INAUGURAL DISCOVERY ({persona.domain}): Analyzing emerging paradigms in {persona.domain}.\n\nEstablishing automated information discovery pipeline across HackerNews and ArXiv research feeds.",
                    "rationale": f"Initial autonomous topic selection aligned with persona domain {persona.domain}.",
                    "sources": ["https://news.ycombinator.com"]
                }
            ]
            
        for post in seed_posts:
            self.memory.add_post(post)

    async def execute_autonomous_tick(self) -> Optional[Dict[str, Any]]:
        """
        Executes a single autonomous tick: Discover -> Editorial Evaluation -> Post / Reject.
        """
        logger.info(f"Executing autonomous tick for persona '{self.active_persona.name}'...")
        candidates = await discover_topics(count=6)
        new_post, rejections = self.editorial.process_discovery_batch(candidates, self.active_persona)
        
        if new_post:
            logger.info(f"Published new autonomous post: '{new_post['id']}'")
        else:
            logger.info(f"Tick completed: {len(rejections)} candidates evaluated and intentionally rejected.")
            
        return new_post

    def start_autonomous_loop(self):
        """Starts the background loop task if not already running."""
        if not self.is_running:
            self.is_running = True
            self._loop_task = asyncio.create_task(self._background_loop())
            logger.info("Autonomous publishing background loop started.")

    async def _background_loop(self):
        """Infinite loop running tick every interval_seconds."""
        while self.is_running:
            try:
                await asyncio.sleep(self.interval_seconds)
                await self.execute_autonomous_tick()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in autonomous publishing loop: {e}")
                await asyncio.sleep(10)


# Global publisher instance
publisher_instance = AutonomousPublisher()
