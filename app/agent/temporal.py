"""
Temporal Continuity Engine (Amendment 12)
Reasons about change over time across discovery cycles.
Evaluates:
1. What is genuinely new since the previous cycle?
2. Has a previously observed story developed?
3. Has new evidence changed an earlier understanding?
4. Has an unresolved question received an answer?
5. Is a previously rejected topic now worth reconsidering?

Ensures each cycle is a continuation of the agent's ongoing existence.
"""

import logging
from typing import Dict, Any, List, Optional
from app.agent.discovery import CandidateTopic
from app.agent.memory import AgentMemory

logger = logging.getLogger("temporal")


class TemporalContinuityResult:
    def __init__(
        self,
        delta_since_last_cycle: str,
        is_story_development: bool,
        developed_story_title: Optional[str],
        has_belief_changed: bool,
        belief_change_detail: str,
        has_question_answered: bool,
        answered_question_text: str,
        is_rejected_reconsidered: bool,
        reconsideration_reason: str
    ):
        self.delta_since_last_cycle = delta_since_last_cycle
        self.is_story_development = is_story_development
        self.developed_story_title = developed_story_title
        self.has_belief_changed = has_belief_changed
        self.belief_change_detail = belief_change_detail
        self.has_question_answered = has_question_answered
        self.answered_question_text = answered_question_text
        self.is_rejected_reconsidered = is_rejected_reconsidered
        self.reconsideration_reason = reconsideration_reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "deltaSinceLastCycle": self.delta_since_last_cycle,
            "isStoryDevelopment": self.is_story_development,
            "developedStoryTitle": self.developed_story_title,
            "hasBeliefChanged": self.has_belief_changed,
            "beliefChangeDetail": self.belief_change_detail,
            "hasQuestionAnswered": self.has_question_answered,
            "answeredQuestionText": self.answered_question_text,
            "isRejectedReconsidered": self.is_rejected_reconsidered,
            "reconsiderationReason": self.reconsideration_reason
        }


class TemporalContinuityEngine:
    @classmethod
    def evaluate_temporal_delta(cls, candidate: CandidateTopic, memory: AgentMemory) -> TemporalContinuityResult:
        """
        Evaluates temporal continuity across discovery cycles.
        """
        title_lower = candidate.title.lower()
        summary_lower = candidate.summary.lower()
        
        # 1. Delta since last cycle
        delta_str = f"Fresh development observed in cycle: {candidate.factualDevelopment or candidate.title}"
        
        # 2. Check if a previously observed story has developed
        is_story_dev = False
        dev_story_title = None
        for post in memory.posts[:10]:
            p_text = post.get("text", "").lower()
            p_words = set(w for w in p_text.split() if len(w) > 4)
            cand_words = set(w for w in (title_lower + " " + summary_lower).split() if len(w) > 4)
            common = cand_words.intersection(p_words)
            if len(common) >= 3:
                is_story_dev = True
                dev_story_title = post.get("text", "")[:60]
                break

        # 3. Check if new evidence changed an earlier belief
        belief_changed = False
        belief_detail = ""
        for bel in memory.provisional_beliefs:
            st = bel.get("stance", "").lower()
            st_words = set(w for w in st.split() if len(w) > 4)
            cand_words = set(w for w in (title_lower + " " + summary_lower).split() if len(w) > 4)
            if len(st_words.intersection(cand_words)) >= 2:
                belief_changed = True
                belief_detail = f"Updated stance on active engineering belief '{bel['id']}' based on fresh empirical evidence."
                break

        # 4. Check if an unresolved curiosity question received an answer
        q_answered = False
        q_text = ""
        for q in memory.unresolved_questions:
            q_topic = q.get("topic", "").lower()
            q_words = set(w for w in q_topic.split() if len(w) > 4)
            cand_words = set(w for w in (title_lower + " " + summary_lower).split() if len(w) > 4)
            if len(q_words.intersection(cand_words)) >= 2:
                q_answered = True
                q_text = q.get("question", "")
                break

        # 5. Check if a previously rejected topic is worth reconsidering
        rejected_reconsidered = False
        reconsideration_reason = ""
        for rej in memory.rejected_topics[:15]:
            rej_title = rej.get("title", "").lower()
            rej_words = set(w for w in rej_title.split() if len(w) > 4)
            cand_words = set(w for w in (title_lower + " " + summary_lower).split() if len(w) > 4)
            if len(rej_words.intersection(cand_words)) >= 3:
                if candidate.sourceQuality >= 70.0 or "paper" in summary_lower or "weights" in summary_lower:
                    rejected_reconsidered = True
                    reconsideration_reason = f"Previously rejected topic '{rej['id']}' re-evaluated due to new primary source evidence and open weights."
                    break

        return TemporalContinuityResult(
            delta_since_last_cycle=delta_str,
            is_story_development=is_story_dev,
            developed_story_title=dev_story_title,
            has_belief_changed=belief_changed,
            belief_change_detail=belief_detail,
            has_question_answered=q_answered,
            answered_question_text=q_text,
            is_rejected_reconsidered=rejected_reconsidered,
            reconsideration_reason=reconsideration_reason
        )
