"""
Autonomous Robotics Intelligence Engine (Amendment 01)
Primary Objective: Autonomous Engineering Attention & Judgment.
Independently determines:
1. What changed in robotics (Discovery & Delta Detection)
2. What deserves investigation (Evidence Audit)
3. What is technically significant vs. noise (Weighted Significance Gate)
4. What connects to previously observed developments (Knowledge Graph Interconnection)
5. What deserves an engineering opinion (Systems Engineering Perspective)
6. When there is nothing worth publishing (Quality Gate & Silence Decision)
7. Autonomous Robotics Intelligence Report (Useful even if publishing layer is disabled)
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from app.agent.persona import Persona, resolve_persona
from app.agent.discovery import CandidateTopic, discover_topics
from app.agent.memory import AgentMemory, memory_instance

logger = logging.getLogger("intelligence")


class IntelligenceSignal:
    def __init__(
        self,
        signal_id: str,
        timestamp: str,
        what_changed: str,
        deserves_investigation: bool,
        is_technically_significant: bool,
        is_noise: bool,
        noise_reason: Optional[str],
        connected_previous_topics: List[str],
        deserves_engineering_opinion: bool,
        candidate_representation: Dict[str, Any]
    ):
        self.signal_id = signal_id
        self.timestamp = timestamp
        self.what_changed = what_changed
        self.deserves_investigation = deserves_investigation
        self.is_technically_significant = is_technically_significant
        self.is_noise = is_noise
        self.noise_reason = noise_reason
        self.connected_previous_topics = connected_previous_topics
        self.deserves_engineering_opinion = deserves_engineering_opinion
        self.candidate_representation = candidate_representation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signalId": self.signal_id,
            "timestamp": self.timestamp,
            "whatChanged": self.what_changed,
            "deservesInvestigation": self.deserves_investigation,
            "isTechnicallySignificant": self.is_technically_significant,
            "isNoise": self.is_noise,
            "noiseReason": self.noise_reason,
            "connectedPreviousTopics": self.connected_previous_topics,
            "deservesEngineeringOpinion": self.deserves_engineering_opinion,
            "candidateRepresentation": self.candidate_representation
        }


class AutonomousRoboticsIntelligenceEngine:
    def __init__(self, memory: AgentMemory = memory_instance):
        self.memory = memory

    async def analyze_ecosystem(self, persona: Persona) -> Dict[str, Any]:
        """
        Executes autonomous engineering attention & judgment cycle.
        Returns full intelligence state independent of publishing.
        """
        now_str = datetime.now(timezone.utc).isoformat()
        raw_candidates = await discover_topics(count=6)
        
        evaluated_signals: List[IntelligenceSignal] = []
        significant_signals: List[IntelligenceSignal] = []
        noise_signals: List[IntelligenceSignal] = []
        
        for cand in raw_candidates:
            # 1. Delta Detection (What changed?)
            what_changed = cand.factualDevelopment or f"New development: {cand.title}"
            
            # 2. Noise & Hard Filter Check (What is merely noise?)
            is_noise = False
            noise_reason = None
            combined_text = f"{cand.title} {cand.summary}".lower()
            
            for rkw in persona.rejected_keywords:
                if rkw.lower() in combined_text:
                    is_noise = True
                    noise_reason = f"Promotional / Non-technical noise phrase: '{rkw}'"
                    break
                    
            if not is_noise and cand.sourceQuality < 45.0:
                is_noise = True
                noise_reason = "Unverified / Weak source credibility"
                
            # 3. Technical Significance Gate (What is technically significant?)
            is_significant = (cand.technicalImpact >= 70.0 and cand.engineeringDepth >= 65.0 and not is_noise)
            
            # 4. Connection to Previously Observed Developments
            connected_topics = []
            for post in self.memory.posts[:5]:
                p_text = post.get("text", "").lower()
                for kw in cand.raw_keywords:
                    if kw.lower() in p_text and kw.lower() not in connected_topics:
                        connected_topics.append(kw.lower())
                        
            # 5. Deserves Engineering Opinion & Investigation
            deserves_opinion = is_significant and cand.roboticsRelevance >= 65.0 and len(connected_topics) < 4
            
            signal = IntelligenceSignal(
                signal_id=cand.topicId,
                timestamp=now_str,
                what_changed=what_changed,
                deserves_investigation=is_significant,
                is_technically_significant=is_significant,
                is_noise=is_noise,
                noise_reason=noise_reason,
                connected_previous_topics=connected_topics[:3],
                deserves_engineering_opinion=deserves_opinion,
                candidate_representation=cand.to_dict()
            )
            
            evaluated_signals.append(signal)
            if is_noise:
                noise_signals.append(signal)
            elif is_significant:
                significant_signals.append(signal)
                
        # 6. Decision Gate (When there is nothing worth publishing)
        publishing_recommended = len(significant_signals) > 0 and any(s.deserves_engineering_opinion for s in significant_signals)
        
        return {
            "timestamp": now_str,
            "persona": persona.name,
            "domain": persona.domain,
            "totalEcosystemCandidatesAnalyzed": len(raw_candidates),
            "technicallySignificantDeltas": len(significant_signals),
            "filteredNoiseRatio": f"{(len(noise_signals) / max(1, len(raw_candidates))) * 100:.1f}%",
            "publishingRecommended": publishing_recommended,
            "signals": [s.to_dict() for s in evaluated_signals],
            "significantSignals": [s.to_dict() for s in significant_signals],
            "noiseSignals": [s.to_dict() for s in noise_signals]
        }


# Global intelligence instance
intelligence_instance = AutonomousRoboticsIntelligenceEngine()
