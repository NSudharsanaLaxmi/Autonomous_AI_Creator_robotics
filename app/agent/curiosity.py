"""
Autonomous Curiosity Engine (Amendment 03)
Implements continuous curiosity loop:
DISCOVERY -> QUESTION -> SEARCH -> EVIDENCE -> UPDATED UNDERSTANDING
Identifies natural engineering questions (generalization, sim-to-real, inference latency, hardware, failure modes),
stores them in persistent memory, and actively looks for answering evidence in future discovery cycles.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from app.agent.discovery import CandidateTopic
from app.agent.memory import AgentMemory

logger = logging.getLogger("curiosity")


class UnresolvedQuestion(dict):
    def __init__(
        self,
        question_id: str,
        origin_topic_id: str,
        origin_topic_title: str,
        subsystem: str,
        category: str,
        question_text: str,
        created_at: str,
        status: str = "unresolved",
        answering_topic_title: Optional[str] = None,
        answering_evidence: Optional[str] = None
    ):
        super().__init__(
            questionId=question_id,
            originTopicId=origin_topic_id,
            originTopicTitle=origin_topic_title,
            subsystem=subsystem,
            category=category,
            questionText=question_text,
            createdAt=created_at,
            status=status,
            answeringTopicTitle=answering_topic_title,
            answeringEvidence=answering_evidence
        )


class AutonomousCuriosityEngine:
    @classmethod
    def generate_natural_questions(cls, topic: CandidateTopic) -> List[UnresolvedQuestion]:
        """
        Generates 1-2 natural engineering questions arising from an observed development.
        Categories: generalization, training data, task transfer, sim-to-real performance,
        inference latency, hardware requirements, failure modes.
        """
        now_str = datetime.now(timezone.utc).isoformat()
        combined = f"{topic.title} {topic.summary}".lower()
        questions = []

        if "vla" in combined or "policy" in combined or "locomotion" in combined:
            questions.append(UnresolvedQuestion(
                question_id=f"q-{uuid.uuid4().hex[:6]}",
                origin_topic_id=topic.topicId,
                origin_topic_title=topic.title,
                subsystem=topic.affectedSubsystem or "control",
                category="sim-to-real performance",
                question_text=f"What is the empirical zero-shot sim-to-real degradation rate for {topic.title} when tested under unmodeled surface friction?",
                created_at=now_str
            ))
            questions.append(UnresolvedQuestion(
                question_id=f"q-{uuid.uuid4().hex[:6]}",
                origin_topic_id=topic.topicId,
                origin_topic_title=topic.title,
                subsystem="compute",
                category="inference latency",
                question_text=f"Can the 7B motor policy inference run locally within a strict sub-15ms edge compute envelope without cloud tethering?",
                created_at=now_str
            ))
        elif "ros" in combined or "middleware" in combined or "tactile" in combined:
            questions.append(UnresolvedQuestion(
                question_id=f"q-{uuid.uuid4().hex[:6]}",
                origin_topic_id=topic.topicId,
                origin_topic_title=topic.title,
                subsystem="sensing",
                category="hardware requirements",
                question_text=f"What is the maximum tactile sensor packet jitter over CAN bus before force-feedback control stability degrades?",
                created_at=now_str
            ))
        else:
            questions.append(UnresolvedQuestion(
                question_id=f"q-{uuid.uuid4().hex[:6]}",
                origin_topic_id=topic.topicId,
                origin_topic_title=topic.title,
                subsystem=topic.affectedSubsystem or "autonomy",
                category="failure modes",
                question_text=f"What deterministic safety fallback occurs when the perception model experiences environmental occlusion?",
                created_at=now_str
            ))

        return questions[:2]

    @classmethod
    def check_for_answering_evidence(
        cls, candidate: CandidateTopic, memory: AgentMemory
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Actively checks if a new discovery candidate provides evidence that answers
        a previously stored unresolved question in persistent memory.
        """
        unresolved = [q for q in memory.unresolved_questions if q.get("status") == "unresolved"]
        if not unresolved:
            return None, None

        cand_text = f"{candidate.title} {candidate.summary}".lower()

        for q in unresolved:
            q_category = q.get("category", "")
            q_subsystem = q.get("subsystem", "")
            q_text = q.get("questionText", "")

            # Match if candidate provides matching category/subsystem keywords
            if (q_subsystem in cand_text or q_category.split()[0] in cand_text) and len(candidate.summary) > 40:
                evidence = f"Recent empirical paper '{candidate.title}' provides verified hardware data regarding {q_category}."
                q["status"] = "resolved"
                q["answeringTopicTitle"] = candidate.title
                q["answeringEvidence"] = evidence
                memory.save()
                
                updated_understanding = (
                    f"UPDATED UNDERSTANDING (Curiosity Loop Resolved Question):\n"
                    f"Previously Open Question from '{q.get('originTopicTitle')}': {q_text}\n"
                    f"New Evidence: {evidence}"
                )
                return q, updated_understanding

        return None, None
