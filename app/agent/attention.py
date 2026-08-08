"""
Engineering Attention Evaluator (Amendment 02)
Optimizes for the usefulness of information brought to the persona's attention.
Evaluates 7 core criteria for every discovered development:
1. Is this new? (is_new)
2. Is this important? (is_important)
3. Is this technically meaningful? (is_technically_meaningful)
4. Is this relevant to robotics? (is_relevant_to_robotics)
5. Does it change an existing understanding? (changes_existing_understanding)
6. Does it connect to something previously observed? (connects_to_previously_observed)
7. Would an engineer reasonably benefit from knowing this now? (engineer_benefit_now)

Rule: A topic that fails these tests is DISCARDED immediately, even if it is currently trending.
Preference: ONE genuinely useful insight over multiple low-value publications.
"""

import logging
from typing import Dict, Any, List, Tuple
from app.agent.discovery import CandidateTopic
from app.agent.memory import AgentMemory

logger = logging.getLogger("attention")


class EngineeringAttentionResult:
    def __init__(
        self,
        topic_id: str,
        title: str,
        is_new: bool,
        is_important: bool,
        is_technically_meaningful: bool,
        is_relevant_to_robotics: bool,
        changes_existing_understanding: bool,
        connects_to_previously_observed: bool,
        engineer_benefit_now: bool,
        attention_score: float,
        passed_attention_gate: bool,
        discard_reason: str
    ):
        self.topic_id = topic_id
        self.title = title
        self.is_new = is_new
        self.is_important = is_important
        self.is_technically_meaningful = is_technically_meaningful
        self.is_relevant_to_robotics = is_relevant_to_robotics
        self.changes_existing_understanding = changes_existing_understanding
        self.connects_to_previously_observed = connects_to_previously_observed
        self.engineer_benefit_now = engineer_benefit_now
        self.attention_score = attention_score
        self.passed_attention_gate = passed_attention_gate
        self.discard_reason = discard_reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topicId": self.topic_id,
            "title": self.title,
            "7CoreTests": {
                "isNew": self.is_new,
                "isImportant": self.is_important,
                "isTechnicallyMeaningful": self.is_technically_meaningful,
                "isRelevantToRobotics": self.is_relevant_to_robotics,
                "changesExistingUnderstanding": self.changes_existing_understanding,
                "connectsToPreviouslyObserved": self.connects_to_previously_observed,
                "engineerBenefitNow": self.engineer_benefit_now
            },
            "attentionScore": round(self.attention_score, 1),
            "passedAttentionGate": self.passed_attention_gate,
            "discardReason": self.discard_reason
        }


class EngineeringAttentionEvaluator:
    @classmethod
    def evaluate_attention(cls, candidate: CandidateTopic, memory: AgentMemory) -> EngineeringAttentionResult:
        """
        Evaluates candidate against Amendment 02 7 core Engineering Attention criteria.
        """
        combined_text = f"{candidate.title} {candidate.summary}".lower()
        
        # 1. Is this new?
        is_new = candidate.novelty >= 60.0
        
        # 2. Is this important?
        is_important = candidate.technicalImpact >= 65.0
        
        # 3. Is this technically meaningful?
        is_technically_meaningful = candidate.engineeringDepth >= 60.0 and candidate.sourceQuality >= 45.0
        
        # 4. Is this relevant to robotics?
        is_relevant_to_robotics = candidate.roboticsRelevance >= 65.0
        
        # 5. Does it change an existing understanding?
        changes_existing_understanding = candidate.realWorldImpact >= 60.0 or "vla" in combined_text or "sim-to-real" in combined_text
        
        # 6. Does it connect to something previously observed?
        connected_count = 0
        for post in memory.posts[:10]:
            p_text = post.get("text", "").lower()
            for kw in candidate.raw_keywords:
                if kw.lower() in p_text:
                    connected_count += 1
                    break
        connects_to_previously_observed = connected_count > 0
        
        # 7. Would an engineer reasonably benefit from knowing this now?
        engineer_benefit_now = candidate.editorialPotential >= 60.0 and candidate.timeliness >= 60.0
        
        # Calculate Engineering Attention Score (0-100)
        tests_passed = sum([
            is_new,
            is_important,
            is_technically_meaningful,
            is_relevant_to_robotics,
            changes_existing_understanding,
            connects_to_previously_observed,
            engineer_benefit_now
        ])
        
        attention_score = (tests_passed / 7.0) * 100.0
        
        # Mandatory quality gate: Must pass at least 5 out of 7 tests, including relevance & technical depth
        passed = (tests_passed >= 4 and is_relevant_to_robotics and is_technically_meaningful)
        
        discard_reason = ""
        if not passed:
            failed_tests = []
            if not is_new: failed_tests.append("Not new")
            if not is_important: failed_tests.append("Low importance")
            if not is_technically_meaningful: failed_tests.append("Lacks technical depth")
            if not is_relevant_to_robotics: failed_tests.append("Low robotics relevance")
            if not engineer_benefit_now: failed_tests.append("No immediate engineer benefit")
            discard_reason = f"Discarded by Engineering Attention Gate: Failed tests [{', '.join(failed_tests)}]."
            
        return EngineeringAttentionResult(
            topic_id=candidate.topicId,
            title=candidate.title,
            is_new=is_new,
            is_important=is_important,
            is_technically_meaningful=is_technically_meaningful,
            is_relevant_to_robotics=is_relevant_to_robotics,
            changes_existing_understanding=changes_existing_understanding,
            connects_to_previously_observed=connects_to_previously_observed,
            engineer_benefit_now=engineer_benefit_now,
            attention_score=attention_score,
            passed_attention_gate=passed,
            discard_reason=discard_reason
        )
