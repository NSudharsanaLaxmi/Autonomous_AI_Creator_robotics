"""
Novelty vs Significance Matrix Evaluator (Amendment 06)
Decouples Novelty (recency/popularity) from Technical Significance (real-world impact/empirical depth).
Evaluates 4 Quadrants:
1. Quadrant I: High Novelty + High Significance -> TOP PRIORITY
2. Quadrant II: Moderate/Low Novelty + High Significance (Real-world deployment of prior research) -> HIGH PRIORITY
3. Quadrant III: High Novelty + Low Significance (Trending product announcement / SaaS fluff) -> REJECTED
4. Quadrant IV: Low Novelty + Low Significance -> REJECTED

Rule: Trending status is NEVER sufficient justification for publication.
If Significance < 60.0, candidate is REJECTED regardless of Novelty score.
"""

import logging
from typing import Dict, Any, Tuple
from app.agent.discovery import CandidateTopic

logger = logging.getLogger("matrix")


class MatrixEvaluationResult:
    def __init__(
        self,
        novelty_score: float,
        significance_score: float,
        quadrant: str,  # Q1, Q2, Q3, Q4
        quadrant_name: str,
        is_publishable: bool,
        rejection_reason: str = ""
    ):
        self.novelty_score = novelty_score
        self.significance_score = significance_score
        self.quadrant = quadrant
        self.quadrant_name = quadrant_name
        self.is_publishable = is_publishable
        self.rejection_reason = rejection_reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "noveltyScore": round(self.novelty_score, 1),
            "significanceScore": round(self.significance_score, 1),
            "quadrant": self.quadrant,
            "quadrantName": self.quadrant_name,
            "isPublishable": self.is_publishable,
            "rejectionReason": self.rejection_reason
        }


class NoveltySignificanceMatrixEvaluator:
    @classmethod
    def evaluate_matrix(cls, candidate: CandidateTopic) -> MatrixEvaluationResult:
        """
        Evaluates candidate along 2 independent axes: Novelty vs Technical Significance.
        """
        combined_text = f"{candidate.title} {candidate.summary}".lower()
        
        # 1. Axis 1: Novelty Score (How new is the information?)
        novelty = candidate.novelty
        if candidate.timeliness >= 80.0:
            novelty = max(novelty, candidate.timeliness)
            
        # 2. Axis 2: Technical Significance Score (How much could this actually matter in the physical world?)
        # Evaluated from empirical evidence, hardware deployment, open weights, and subsystem depth
        significance = candidate.technicalImpact * 0.40 + candidate.realWorldImpact * 0.35 + candidate.engineeringDepth * 0.25
        
        # Boost significance for verified real-world hardware deployment of prior research
        if "deployment" in combined_text or "field trial" in combined_text or "real-world" in combined_text:
            significance = min(100.0, significance + 15.0)
            
        # Penalty for promotional announcements with zero empirical data
        if any(w in combined_text for w in ["announces", "unveils", "teaser", "coming soon"]) and "paper" not in combined_text:
            significance = max(10.0, significance - 25.0)

        # 3. Classify Quadrant
        high_novelty = novelty >= 65.0
        high_significance = significance >= 60.0

        if high_novelty and high_significance:
            quadrant = "Q1"
            quadrant_name = "High Novelty + High Significance (Top Priority)"
            publishable = True
            reason = ""
        elif not high_novelty and high_significance:
            quadrant = "Q2"
            quadrant_name = "Moderate/Low Novelty + High Significance (Real-World Field Deployment Milestone)"
            publishable = True
            reason = ""
        elif high_novelty and not high_significance:
            quadrant = "Q3"
            quadrant_name = "High Novelty + Low Significance (Trending Fluff / Product Teaser)"
            publishable = False
            reason = "Rejected by Novelty-Significance Matrix: High trending novelty but low technical significance (Significance < 60.0)."
        else:
            quadrant = "Q4"
            quadrant_name = "Low Novelty + Low Significance"
            publishable = False
            reason = "Rejected by Novelty-Significance Matrix: Low technical significance and low novelty."

        return MatrixEvaluationResult(
            novelty_score=novelty,
            significance_score=significance,
            quadrant=quadrant,
            quadrant_name=quadrant_name,
            is_publishable=publishable,
            rejection_reason=reason
        )
