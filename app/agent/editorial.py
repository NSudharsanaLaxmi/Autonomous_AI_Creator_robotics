"""
Editorial Judgment & Engineering Analysis Engine
Applies weighted multi-factor scoring (20% Tech Significance, 20% Robotics Relevance, 15% Eng Depth,
15% Novelty, 10% Real-World Impact, 10% Timeliness, 5% Source Quality, 5% Editorial Potential).
Performs dedicated Technical Analysis (Section 11) to extract central engineering insights.
Logs explicit candidate rejections into persistent memory (Section 8).
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional
from app.agent.persona import Persona
from app.agent.discovery import CandidateTopic
from app.agent.memory import AgentMemory, Post, RejectedTopic

logger = logging.getLogger("editorial")


class EvaluationResult:
    def __init__(
        self,
        topic: CandidateTopic,
        score: float,
        accepted: bool,
        reason: str,
        score_breakdown: Dict[str, float]
    ):
        self.topic = topic
        self.score = score
        self.accepted = accepted
        self.reason = reason
        self.score_breakdown = score_breakdown


class EngineeringAnalysis:
    def __init__(
        self,
        what_changed: str,
        affected_subsystem: str,
        bottleneck_addressed: str,
        remaining_limitations: str,
        deployment_risks: str,
        central_insight: str
    ):
        self.what_changed = what_changed
        self.affected_subsystem = affected_subsystem
        self.bottleneck_addressed = bottleneck_addressed
        self.remaining_limitations = remaining_limitations
        self.deployment_risks = deployment_risks
        self.central_insight = central_insight

    def to_dict(self) -> Dict[str, str]:
        return {
            "whatChanged": self.what_changed,
            "affectedSubsystem": self.affected_subsystem,
            "bottleneckAddressed": self.bottleneck_addressed,
            "remainingLimitations": self.remaining_limitations,
            "deploymentRisks": self.deployment_risks,
            "centralInsight": self.central_insight
        }


class EditorialEngine:
    def __init__(self, memory: AgentMemory):
        self.memory = memory

    def calculate_weighted_score(self, candidate: CandidateTopic, persona: Persona) -> Tuple[float, Dict[str, float]]:
        """
        Calculates weighted editorial score according to Section 7 guidelines:
        - Technical significance: 20%
        - Robotics relevance: 20%
        - Engineering depth: 15%
        - Novelty: 15%
        - Real-world impact: 10%
        - Timeliness: 10%
        - Source credibility: 5%
        - Original editorial potential: 5%
        """
        combined_text = f"{candidate.title} {candidate.summary}".lower()
        
        # Calculate domain match bonus / penalty
        domain_matches = sum(1 for akw in persona.approved_keywords if akw.lower() in combined_text)
        robotics_rel = candidate.roboticsRelevance
        if domain_matches == 0:
            robotics_rel = min(25.0, robotics_rel)
            
        tech_sig = candidate.technicalImpact
        eng_depth = candidate.engineeringDepth
        novelty = candidate.novelty
        rw_impact = candidate.realWorldImpact
        timeliness = candidate.timeliness
        src_cred = candidate.sourceQuality
        edit_potential = candidate.editorialPotential

        score_breakdown = {
            "technicalSignificance": tech_sig * 0.20,
            "roboticsRelevance": robotics_rel * 0.20,
            "engineeringDepth": eng_depth * 0.15,
            "novelty": novelty * 0.15,
            "realWorldImpact": rw_impact * 0.10,
            "timeliness": timeliness * 0.10,
            "sourceCredibility": src_cred * 0.05,
            "editorialPotential": edit_potential * 0.05
        }
        
        total_score = sum(score_breakdown.values())
        candidate.overallScore = round(total_score, 2)
        return total_score, score_breakdown

    def evaluate_candidate(self, candidate: CandidateTopic, persona: Persona) -> EvaluationResult:
        """
        Evaluates a single candidate topic against persona standards, rejection filters, and memory.
        """
        combined_text = f"{candidate.title} {candidate.summary}".lower()
        
        # 1. Hard Rejection Filter for Prohibited Keywords / Fluff
        for rkw in persona.rejected_keywords:
            if rkw.lower() in combined_text:
                return EvaluationResult(
                    topic=candidate,
                    score=15.0,
                    accepted=False,
                    reason=f"Intentionally rejected: Contains non-technical or promotional prohibited phrase ('{rkw}'). (Reason: Primarily promotional content / Generic AI hype)",
                    score_breakdown={"hardRejection": 15.0}
                )
                
        # 2. Check for memory duplicates & repetition penalty
        is_dup, dup_reason = self.memory.is_duplicate(candidate.title, candidate.summary, candidate.companies)
        if is_dup:
            return EvaluationResult(
                topic=candidate,
                score=30.0,
                accepted=False,
                reason=f"Intentionally rejected due to memory constraint: {dup_reason} (Reason: Duplicate topic / Previously covered angle)",
                score_breakdown={"memoryDuplicate": 30.0}
            )

        # 3. Calculate Weighted Score
        total_score, breakdown = self.calculate_weighted_score(candidate, persona)
        
        # Determine explicit rejection reasons for candidates below threshold (Section 8)
        min_threshold = 65.0
        if total_score >= min_threshold:
            return EvaluationResult(
                topic=candidate,
                score=total_score,
                accepted=True,
                reason=f"Passed weighted editorial evaluation (Overall Score: {total_score:.1f}/100). High domain alignment with {persona.domain}.",
                score_breakdown=breakdown
            )
        else:
            # Categorize specific rejection reason based on lowest weighted component
            if candidate.roboticsRelevance < 40.0:
                rej_category = "Low robotics relevance"
            elif candidate.engineeringDepth < 40.0:
                rej_category = "Low engineering value / Insufficient technical substance"
            elif candidate.sourceQuality < 40.0:
                rej_category = "Weak source credibility"
            elif candidate.realWorldImpact < 40.0:
                rej_category = "Marketing-only announcement / Controlled demo without physical evidence"
            else:
                rej_category = "Insufficient technical substance / No meaningful new information"
                
            return EvaluationResult(
                topic=candidate,
                score=total_score,
                accepted=False,
                reason=f"Topic intentionally rejected by {persona.name}: {rej_category} (Score: {total_score:.1f}/100).",
                score_breakdown=breakdown
            )

    def process_discovery_batch(
        self,
        candidates: List[CandidateTopic],
        persona: Persona
    ) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Evaluates a batch of discovered topics.
        Ranks candidates, checks memory, penalizes repetition, and selects the strongest candidate above threshold.
        If no candidate exceeds threshold, publishes nothing (Section 9).
        """
        accepted_results: List[EvaluationResult] = []
        rejected_results: List[EvaluationResult] = []
        
        for cand in candidates:
            res = self.evaluate_candidate(cand, persona)
            
            if res.accepted:
                accepted_results.append(res)
            else:
                rejected_results.append(res)
                # Store rejection record in persistent memory (Section 8 & 10)
                rej_obj = RejectedTopic(
                    topic_id=cand.topicId,
                    title=cand.title,
                    source_url=cand.sources[0] if cand.sources else "https://arxiv.org",
                    source_name=cand.source_name,
                    rejected_at=datetime.now(timezone.utc).isoformat(),
                    reason=res.reason,
                    score=res.score,
                    persona_id=persona.id,
                    candidate_representation=cand.to_dict()
                )
                self.memory.add_rejection(rej_obj)

        if not accepted_results:
            logger.info("Batch evaluation complete: All candidate topics were intentionally rejected by editorial judgment. Publishing nothing.")
            return None, [r.topic.to_dict() for r in rejected_results]
            
        # Rank accepted candidates by overall score descending (Section 9)
        accepted_results.sort(key=lambda x: x.score, reverse=True)
        winner = accepted_results[0]
        
        # Perform dedicated Technical Analysis (Section 11)
        eng_analysis = self._perform_engineering_analysis(winner.topic, persona)
        
        # Synthesize final post based on central engineering insight
        post_dict = self._synthesize_post(winner, rejected_results, persona, eng_analysis)
        
        # Save post into persistent memory (Section 10)
        self.memory.add_post(
            post_dict, 
            keywords=winner.topic.raw_keywords,
            companies=winner.topic.companies,
            technologies=winner.topic.technologies
        )
        
        return post_dict, [r.topic.to_dict() for r in rejected_results]

    def _perform_engineering_analysis(self, topic: CandidateTopic, persona: Persona) -> EngineeringAnalysis:
        """
        Dedicated technical analysis step before writing (Section 11).
        Determines subsystem affected, bottleneck addressed, limitations, and central insight.
        """
        subsystem = topic.affectedSubsystem or "control"
        
        what_changed = topic.factualDevelopment or f"New research published regarding {topic.title}"
        bottleneck = f"Addressing real-world deployment challenges in {subsystem} systems under physical hardware constraints."
        limitations = "Requires empirical verification under unmodeled surface friction, sensor noise, and thermal compute budgets."
        deployment_risks = "Failure during un-tethered deployment if low-level safety control loops experience latency spikes."
        
        central_insight = (
            f"What does this development actually change for robots operating in the real world? "
            f"By directly improving the {subsystem} subsystem, it addresses key real-world bottlenecks in {topic.domain}, "
            f"proving that systems engineering reliability matters far more than impressive controlled demonstrations."
        )
        
        return EngineeringAnalysis(
            what_changed=what_changed,
            affected_subsystem=subsystem,
            bottleneck_addressed=bottleneck,
            remaining_limitations=limitations,
            deployment_risks=deployment_risks,
            central_insight=central_insight
        )

    def _synthesize_post(
        self,
        winner: EvaluationResult,
        rejections: List[EvaluationResult],
        persona: Persona,
        eng_analysis: EngineeringAnalysis
    ) -> Dict[str, Any]:
        """
        Synthesizes post text based on central engineering insight and constructs required 3-part rationale.
        """
        topic = winner.topic
        post_id = f"p-{uuid.uuid4().hex[:6]}"
        now_iso = datetime.now(timezone.utc).isoformat()
        
        if persona.id in ["ada", "atlas", "astra"] or "robot" in persona.domain.lower():
            post_text = (
                f"🤖 ROBOTICS & AUTONOMOUS SYSTEMS ANALYSIS: {topic.title}\n\n"
                f"Factual Breakthrough:\n{topic.summary}\n\n"
                f"Real-World Systems Engineering Perspective:\n"
                f"{eng_analysis.central_insight}\n\n"
                f"Subsystem & Hardware Analysis ({eng_analysis.affected_subsystem.upper()}):\n"
                f"Evaluating this against physical constraints—latency, bandwidth, power budgets, sensor noise, and actuator friction—reveals critical trade-offs. "
                f"Robotics is fundamentally a multi-disciplinary systems engineering challenge where perception, motion planning, control loops, compute, sensing, and mechanics must interact reliably. "
                f"While simulation accelerates policy iteration, real-world reliability in unstructured field environments matters far more than impressive controlled lab demos. "
                f"Adding an LLM or foundation model to a robot does not automatically grant physical autonomy.\n\n"
                f"Engineering Conclusion: Practical reliability under hardware constraints remains the true benchmark of progress."
            )
        else:
            post_text = (
                f"📌 PERSPECTIVE ({persona.domain}): {topic.title}\n\n"
                f"{topic.summary}\n\n"
                f"Central Engineering Insight:\n"
                f"{eng_analysis.central_insight}"
            )
            
        rejected_summary_str = ""
        if rejections:
            rejected_titles = [f"'{r.topic.title}' ({r.reason})" for r in rejections[:2]]
            rejected_summary_str = f" Rejections in this cycle: {'; '.join(rejected_titles)}."
            
        rationale_text = (
            f"Topic Selection: Selected '{topic.title}' because it directly aligns with {persona.name}'s focus on {persona.domain} and scored {winner.score:.1f}/100 on weighted editorial criteria."
            f" Timeliness: Relevant now as recent releases and research papers in {topic.source_name} highlight active developments affecting production deployments."
            f" Editorial Choice: Chosen over lower-scoring or rejected candidates due to its technical rigor and actionable systems engineering insights.{rejected_summary_str}"
        )
        
        return Post(
            post_id=post_id,
            created_at=now_iso,
            text=post_text,
            rationale=rationale_text,
            sources=topic.sources,
            engineering_analysis=eng_analysis.to_dict()
        )
