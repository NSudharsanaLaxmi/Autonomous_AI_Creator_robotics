"""
Persistent Agent Memory Engine
Stores published post history, concept indices, and rejected topics.
Persists state to local JSON file system to survive process restarts and deploys.
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("memory")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
MEMORY_FILE = os.path.join(DATA_DIR, "agent_memory.json")


class Post(dict):
    def __init__(self, post_id: str, created_at: str, text: str, rationale: str, sources: List[str]):
        super().__init__(
            id=post_id,
            createdAt=created_at,
            text=text,
            rationale=rationale,
            sources=sources
        )


class RejectedTopic(dict):
    def __init__(self, topic_id: str, title: str, source_url: str, source_name: str, rejected_at: str, reason: str, score: float, persona_id: str):
        super().__init__(
            id=topic_id,
            title=title,
            source_url=source_url,
            source_name=source_name,
            rejectedAt=rejected_at,
            reason=reason,
            score=score,
            personaId=persona_id
        )


class AgentMemory:
    def __init__(self, memory_filepath: str = MEMORY_FILE):
        self.filepath = memory_filepath
        self.agent_id: str = "ada-sec-001"
        self.active_persona_id: str = "ada"
        self.posts: List[Dict[str, Any]] = []
        self.rejected_topics: List[Dict[str, Any]] = []
        self.concept_index: List[str] = []
        self._ensure_dir()
        self.load()

    def _ensure_dir(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.agent_id = data.get("agent_id", self.agent_id)
                    self.active_persona_id = data.get("active_persona_id", self.active_persona_id)
                    self.posts = data.get("posts", [])
                    self.rejected_topics = data.get("rejected_topics", [])
                    self.concept_index = data.get("concept_index", [])
                    logger.info(f"Loaded {len(self.posts)} posts and {len(self.rejected_topics)} rejections from memory.")
            except Exception as e:
                logger.error(f"Failed loading memory file: {e}")

    def save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump({
                    "agent_id": self.agent_id,
                    "active_persona_id": self.active_persona_id,
                    "posts": self.posts,
                    "rejected_topics": self.rejected_topics,
                    "concept_index": self.concept_index
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed saving memory file: {e}")

    def is_duplicate(self, title: str, summary: str) -> tuple[bool, str]:
        """
        Checks if topic title or summary has high overlap with previously published posts.
        Returns (is_duplicate, duplicate_reason).
        """
        title_lower = title.lower()
        title_words = set(title_lower.split())
        
        for post in self.posts:
            post_text = post.get("text", "").lower()
            post_words = set(post_text.split())
            
            # Word overlap calculation
            overlap = title_words.intersection(post_words)
            if len(overlap) >= 4:
                common_str = ", ".join(list(overlap)[:3])
                return True, f"High conceptual overlap with previous post '{post['id']}' on topics: {common_str}"
                
        return False, ""

    def add_post(self, post: Dict[str, Any], keywords: List[str] = None):
        """Adds a post at the top of the feed (newest first)."""
        self.posts.insert(0, post)
        if keywords:
            for kw in keywords:
                if kw.lower() not in self.concept_index:
                    self.concept_index.append(kw.lower())
        self.save()

    def add_rejection(self, rejection: Dict[str, Any]):
        """Adds a rejection record."""
        self.rejected_topics.insert(0, rejection)
        # Cap rejections memory at 50
        if len(self.rejected_topics) > 50:
            self.rejected_topics = self.rejected_topics[:50]
        self.save()

    def get_feed(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Returns posts in reverse chronological order (newest first)."""
        if limit:
            return self.posts[:limit]
        return self.posts


# Global memory instance
memory_instance = AgentMemory()
