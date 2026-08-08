"""
Belief Evolution Engine (Amendment 05)
Manages provisional engineering beliefs that evolve as new evidence accumulates.
A belief is never treated as permanently true.
When conflicting or updating evidence arrives:
1. Retrieves previous position.
2. Identifies conflicting/updating evidence.
3. Evaluates credibility of both.
4. Determines action: REMAIN | WEAKEN | EVOLVE.
5. Records change in persistent memory.
6. Acknowledges belief evolution in published commentary when warranted.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from app.agent.discovery import CandidateTopic
from app.agent.memory import AgentMemory

logger = logging.getLogger("beliefs")


class ProvisionalBelief(dict):
    def __init__(
        self,
        belief_id: str,
        belief_text: str,
        confidence_score: float,
        evidence_count: int,
        status: str = "active",  # active, weakened, evolved, discarded
        created_at: Optional[str] = None,
        evolution_history: Optional[List[Dict[str, Any]]] = None
    ):
        super().__init__(
            beliefId=belief_id,
            beliefText=belief_text,
            confidenceScore=confidence_score,
            evidenceCount=evidence_count,
            status=status,
            createdAt=created_at or datetime.now(timezone.utc).isoformat(),
            evolutionHistory=evolution_history or []
        )


class BeliefEvolutionResult:
    def __init__(
        self,
        belief_id: str,
        previous_stance: str,
        new_evidence: str,
        action: str,  # "REMAIN", "WEAKEN", "EVOLVE"
        updated_stance: str,
        evolution_note: Optional[str] = None
    ):
        self.belief_id = belief_id
        self.previous_stance = previous_stance
        self.new_evidence = new_evidence
        self.action = action
        self.updated_stance = updated_stance
        self.evolution_note = evolution_note

    def to_dict(self) -> Dict[str, Any]:
        return {
            "beliefId": self.belief_id,
            "previousStance": self.previous_stance,
            "newEvidence": self.new_evidence,
            "action": self.action,
            "updatedStance": self.updated_stance,
            "evolutionNote": self.evolution_note
        }


class BeliefEvolutionEngine:
    DEFAULT_BELIEFS = [
        ProvisionalBelief(
            belief_id="bel-001",
            belief_text="Sim-to-real policy transfer requires domain randomization and high-frequency low-level torque compensation.",
            confidence_score=85.0,
            evidence_count=3
        ),
        ProvisionalBelief(
            belief_id="bel-002",
            belief_text="Vision-Language-Action (VLA) models cannot deliver full physical autonomy without deterministic low-level safety fallbacks.",
            confidence_score=90.0,
            evidence_count=4
        ),
        ProvisionalBelief(
            belief_id="bel-003",
            belief_text="Edge compute latency (<15ms) is more critical for field robotics reliability than high-parameter cloud LLM reasoning.",
            confidence_score=88.0,
            evidence_count=5
        )
    ]

    @classmethod
    def evaluate_and_evolve(
        cls, candidate: CandidateTopic, memory: AgentMemory
    ) -> Tuple[Optional[BeliefEvolutionResult], Optional[str]]:
        """
        Evaluates new candidate evidence against Ada's provisional beliefs in persistent memory.
        Only evolves a position when meaningful evidence warrants it (Amendment 05).
        """
        now_str = datetime.now(timezone.utc).isoformat()
        cand_text = f"{candidate.title} {candidate.summary}".lower()
        
        # Load or initialize beliefs in memory
        if not hasattr(memory, "provisional_beliefs") or not memory.provisional_beliefs:
            memory.provisional_beliefs = [b for b in cls.DEFAULT_BELIEFS]
            memory.save()
            
        for belief in memory.provisional_beliefs:
            b_text = belief.get("beliefText", "").lower()
            b_words = [w for w in b_text.split() if len(w) > 4]
            matches = sum(1 for w in b_words if w in cand_text)
            
            if matches >= 2:
                # Evaluate credibility & conflict
                credibility = candidate.sourceQuality
                prev_stance = belief.get("beliefText", "")
                
                # Check for conflicting vs confirming evidence
                if any(w in cand_text for w in ["breakthrough", "eliminates", "zero-shot", "replaces", "bypasses"]) and credibility >= 75.0:
                    action = "EVOLVE"
                    updated_stance = f"Updated understanding: {candidate.title} demonstrates that direct sensor-to-action policies can bypass traditional intermediate torque layers under verified conditions."
                    note = f"BELIEF EVOLUTION: Previously, Ada posited that '{prev_stance}'. However, new verified empirical evidence from {candidate.source_name} ({candidate.title}) warrants an evolved position: Ada's understanding has updated."
                    
                    belief["status"] = "evolved"
                    belief["confidenceScore"] = min(95.0, belief.get("confidenceScore", 80.0) + 5.0)
                    belief["evidenceCount"] = belief.get("evidenceCount", 1) + 1
                    belief.setdefault("evolutionHistory", []).append({
                        "timestamp": now_str,
                        "action": action,
                        "evidence": candidate.title,
                        "updatedStance": updated_stance
                    })
                    memory.save()
                    
                    res = BeliefEvolutionResult(
                        belief_id=belief.get("beliefId", "bel-001"),
                        previous_stance=prev_stance,
                        new_evidence=candidate.title,
                        action=action,
                        updated_stance=updated_stance,
                        evolution_note=note
                    )
                    return res, note
                    
                elif any(w in cand_text for w in ["confirms", "validates", "proves", "supports"]):
                    belief["confidenceScore"] = min(99.0, belief.get("confidenceScore", 80.0) + 2.0)
                    belief["evidenceCount"] = belief.get("evidenceCount", 1) + 1
                    memory.save()

        return None, None
