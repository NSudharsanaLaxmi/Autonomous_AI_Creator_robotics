"""
Persistent Agent Memory Engine (Section 10 & Amendments 03, 04, 05)
Maintains 5 explicit memory structures:
1. Published Memory: Post ID, Topic, Timestamp, Main argument, Editorial angle, Sources, Technologies, Companies, Keywords.
2. Rejected Memory: Topic, Timestamp, Rejection reason, Score, Candidate representation.
3. Editorial Memory: Recurring themes, Stable opinions, Provisional Engineering Beliefs (Amendment 05).
4. Similarity Memory: Checks duplicate stories, duplicate arguments, duplicate hooks, repetitive source coverage, and company repetition.
5. Curiosity Memory (Amendment 03): Persistent unresolved engineering questions arising naturally from observed developments.
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone

logger = logging.getLogger("memory")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
MEMORY_FILE = os.path.join(DATA_DIR, "agent_memory.json")


class Post(dict):
    def __init__(
        self,
        post_id: str,
        created_at: str,
        text: str,
        rationale: str,
        sources: List[str],
        engineering_analysis: Optional[Dict[str, Any]] = None,
        companies: Optional[List[str]] = None,
        technologies: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ):
        super().__init__(
            id=post_id,
            createdAt=created_at,
            text=text,
            rationale=rationale,
            sources=sources,
            engineeringAnalysis=engineering_analysis or {},
            companies=companies or [],
            technologies=technologies or [],
            keywords=keywords or []
        )


class RejectedTopic(dict):
    def __init__(
        self,
        topic_id: str,
        title: str,
        source_url: str,
        source_name: str,
        rejected_at: str,
        reason: str,
        score: float,
        persona_id: str,
        candidate_representation: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            id=topic_id,
            title=title,
            source_url=source_url,
            source_name=source_name,
            rejectedAt=rejected_at,
            reason=reason,
            score=score,
            personaId=persona_id,
            candidateRepresentation=candidate_representation or {}
        )


class AgentMemory:
    def __init__(self, memory_filepath: str = MEMORY_FILE):
        self.filepath = memory_filepath
        self.agent_id: str = "ada-bot-001"
        self.active_persona_id: str = "ada"
        
        # 1. Published Memory
        self.posts: List[Dict[str, Any]] = []
        
        # 2. Rejected Memory
        self.rejected_topics: List[Dict[str, Any]] = []
        
        # 3. Editorial Memory & Provisional Beliefs (Amendment 05)
        self.editorial_themes: List[str] = [
            "Sim-to-real transfer bottlenecks",
            "Physical hardware execution vs software simulation",
            "Edge compute latency & power envelopes",
            "Real-world reliability over lab demonstrations",
            "LLM integration vs true physical autonomy"
        ]
        self.company_coverage_counts: Dict[str, int] = {}
        self.concept_index: List[str] = []
        self.provisional_beliefs: List[Dict[str, Any]] = []
        
        # 5. Curiosity Memory (Amendment 03)
        self.unresolved_questions: List[Dict[str, Any]] = []
        
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
                    self.editorial_themes = data.get("editorial_themes", self.editorial_themes)
                    self.company_coverage_counts = data.get("company_coverage_counts", {})
                    self.concept_index = data.get("concept_index", [])
                    self.provisional_beliefs = data.get("provisional_beliefs", [])
                    self.unresolved_questions = data.get("unresolved_questions", [])
                    logger.info(f"Loaded {len(self.posts)} posts, {len(self.rejected_topics)} rejections, {len(self.provisional_beliefs)} beliefs, and {len(self.unresolved_questions)} curiosity questions.")
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
                    "editorial_themes": self.editorial_themes,
                    "company_coverage_counts": self.company_coverage_counts,
                    "concept_index": self.concept_index,
                    "provisional_beliefs": self.provisional_beliefs,
                    "unresolved_questions": self.unresolved_questions
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed saving memory file: {e}")

    def add_question(self, question_dict: Dict[str, Any]):
        """Adds a natural engineering question into persistent curiosity memory (Amendment 03)."""
        self.unresolved_questions.insert(0, question_dict)
        if len(self.unresolved_questions) > 50:
            self.unresolved_questions = self.unresolved_questions[:50]
        self.save()

    def is_duplicate(self, title: str, summary: str, companies: Optional[List[str]] = None) -> Tuple[bool, str]:
        """Similarity Memory Check (Section 10)."""
        title_lower = title.lower()
        title_words = set(w for w in title_lower.split() if len(w) > 3)
        
        if companies:
            for comp in companies:
                if self.company_coverage_counts.get(comp, 0) >= 3:
                    return True, f"Repetitive company coverage: Company '{comp}' covered {self.company_coverage_counts[comp]} times recently."
        
        for post in self.posts:
            post_text = post.get("text", "").lower()
            post_words = set(w for w in post_text.split() if len(w) > 3)
            
            overlap = title_words.intersection(post_words)
            if len(overlap) >= 4:
                common_str = ", ".join(list(overlap)[:3])
                return True, f"High conceptual overlap with previous post '{post['id']}' on topics: {common_str}"
                
        return False, ""

    def add_post(self, post: Dict[str, Any], keywords: Optional[List[str]] = None, companies: Optional[List[str]] = None, technologies: Optional[List[str]] = None):
        """Adds a post at the top of the feed (newest first) and updates editorial & similarity memory."""
        self.posts.insert(0, post)
        
        if keywords:
            for kw in keywords:
                if kw.lower() not in self.concept_index:
                    self.concept_index.append(kw.lower())
                    
        if companies:
            for comp in companies:
                self.company_coverage_counts[comp] = self.company_coverage_counts.get(comp, 0) + 1
                
        self.save()

    def add_rejection(self, rejection: Dict[str, Any]):
        """Adds a rejection record to rejected memory."""
        self.rejected_topics.insert(0, rejection)
        if len(self.rejected_topics) > 100:
            self.rejected_topics = self.rejected_topics[:100]
        self.save()

    def get_feed(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Returns posts in reverse chronological order (newest first)."""
        if limit:
            return self.posts[:limit]
        return self.posts


# Global memory instance
memory_instance = AgentMemory()
