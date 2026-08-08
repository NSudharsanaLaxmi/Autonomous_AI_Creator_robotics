"""
Structured Decision Trace Engine (Amendment 14)
Maintains concise structured decision metadata for observability and reproducibility without exposing private Chain-of-Thought (CoT).

Records:
1. candidateScores
2. evidenceReferences
3. rejectionCategories
4. selectedTopic
5. engineeringAngle
6. memoryMatches
7. publicationDecision
8. publicationRationale
9. prePublicationAuditScores
10. temporalContinuityContext
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger("trace")


class StructuredDecisionTrace:
    def __init__(
        self,
        trace_id: str,
        timestamp: str,
        publication_decision: str,  # "PUBLISHED" or "RESTRAINT_NO_PUB"
        selected_topic: Optional[Dict[str, Any]],
        candidate_scores: List[Dict[str, Any]],
        evidence_references: List[str],
        rejection_categories: List[Dict[str, Any]],
        engineering_angle: Optional[Dict[str, Any]],
        memory_matches: List[str],
        publication_rationale: Optional[str],
        pre_publication_audit_scores: Dict[str, bool],
        temporal_continuity_context: Dict[str, Any]
    ):
        self.trace_id = trace_id
        self.timestamp = timestamp
        self.publication_decision = publication_decision
        self.selected_topic = selected_topic
        self.candidate_scores = candidate_scores
        self.evidence_references = evidence_references
        self.rejection_categories = rejection_categories
        self.engineering_angle = engineering_angle
        self.memory_matches = memory_matches
        self.publication_rationale = publication_rationale
        self.pre_publication_audit_scores = pre_publication_audit_scores
        self.temporal_continuity_context = temporal_continuity_context

    def to_dict(self) -> Dict[str, Any]:
        return {
            "traceId": self.trace_id,
            "timestamp": self.timestamp,
            "publicationDecision": self.publication_decision,
            "selectedTopic": self.selected_topic,
            "candidateScores": self.candidate_scores,
            "evidenceReferences": self.evidence_references,
            "rejectionCategories": self.rejection_categories,
            "engineeringAngle": self.engineering_angle,
            "memoryMatches": self.memory_matches,
            "publicationRationale": self.publication_rationale,
            "prePublicationAuditScores": self.pre_publication_audit_scores,
            "temporalContinuityContext": self.temporal_continuity_context
        }
