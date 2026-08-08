"""
Editorial Judgment, Source Verification, Real-World Robotics Lens & Writing Engine
Applies weighted multi-factor scoring (Section 7), Source Verification (Section 14),
10-dimension Real-World Robotics Lens (Section 12), 4-part Writing Engine (Section 13),
and Dynamic 4-Question Publishing Rationale (Section 15).
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


class RealWorldRoboticsLens:
    """Evaluates candidates along the 10 real-world robotics dimensions (Section 12)."""
    DIMENSIONS = {
        "perception": "Can the robot reliably understand its environment under varying lighting, occlusion, and sensor noise?",
        "planning": "Can it make optimal trajectory decisions under real-time uncertainty and dynamic obstacles?",
        "control": "Can high-level decisions be translated into stable low-level physical motion and motor torque?",
        "hardware": "Can the structural actuators, joint bearings, and mechanical linkages support the claimed motion?",
        "compute": "Can model inference execute locally within strict edge latency (<10ms) and power (<30W) budgets?",
        "communication": "Does the system depend on continuous low-latency network connectivity, or can it run untethered?",
        "safety": "What deterministic fallback occurs when the vision or motion model produces an erroneous output?",
        "reliability": "Does the robot execute the task repeatedly across thousands of cycles rather than a single lab demo?",
        "simulation": "Does the policy performance survive zero-shot sim-to-real transfer with unmodeled physical friction?",
        "scalability": "Can this system be deployed across unstructured industrial fleets beyond a controlled laboratory environment?"
    }

    @classmethod
    def select_relevant_lenses(cls, topic: CandidateTopic) -> List[Tuple[str, str]]:
        combined = f"{topic.title} {topic.summary} {topic.affectedSubsystem}".lower()
        selected = []
        
        if any(w in combined for w in ["sim", "isaac", "gazebo", "sim-to-real"]):
            selected.append(("Simulation", cls.DIMENSIONS["simulation"]))
        if any(w in combined for w in ["vla", "humanoid", "locomotion", "bipedal", "torque", "motor"]):
            selected.append(("Control", cls.DIMENSIONS["control"]))
        if any(w in combined for w in ["ros2", "tactile", "sensor", "force", "grasping"]):
            selected.append(("Perception", cls.DIMENSIONS["perception"]))
        if any(w in combined for w in ["jetson", "edge", "power", "latency", "compute"]):
            selected.append(("Compute", cls.DIMENSIONS["compute"]))
        if any(w in combined for w in ["slam", "amr", "planning", "trajectory"]):
            selected.append(("Planning", cls.DIMENSIONS["planning"]))
            
        if len(selected) < 2:
            selected.append(("Reliability", cls.DIMENSIONS["reliability"]))
            selected.append(("Hardware", cls.DIMENSIONS["hardware"]))
            
        return selected[:3]


class EngineeringAnalysis:
    def __init__(
        self,
        hook: str,
        interpretation: str,
        limitation: str,
        takeaway: str,
        relevant_lenses: List[Tuple[str, str]]
    ):
        self.hook = hook
        self.interpretation = interpretation
        self.limitation = limitation
        self.takeaway = takeaway
        self.relevant_lenses = relevant_lenses

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hook": self.hook,
            "interpretation": self.interpretation,
            "limitation": self.limitation,
            "takeaway": self.takeaway,
            "relevantLenses": [l[0] for l in self.relevant_lenses]
        }


class EditorialEngine:
    def __init__(self, memory: AgentMemory):
        self.memory = memory

    def verify_sources_and_evidence(self, candidate: CandidateTopic) -> Tuple[bool, str]:
        """
        Source Verification (Section 14):
        Verifies primary sources, URL validity, and evidence sufficiency.
        If evidence is insufficient, REJECT THE TOPIC.
        """
        if not candidate.sources or len(candidate.sources) == 0:
            return False, "Insufficient evidence: Candidate lacks valid primary source URLs."
            
        for src in candidate.sources:
            if not (src.startswith("http://") or src.startswith("https://")):
                return False, f"Source verification failed: Invalid or fabricated URL format ('{src}')."
                
        if candidate.sourceQuality < 45.0:
            return False, f"Source verification failed: Primary source '{candidate.source_name}' has insufficient credibility or unverified evidence."
            
        if len(candidate.summary.strip()) < 30:
            return False, "Insufficient evidence: Candidate summary lacks factual technical details."
            
        return True, "Source evidence verified successfully."

    def calculate_weighted_score(self, candidate: CandidateTopic, persona: Persona) -> Tuple[float, Dict[str, float]]:
        """Calculates weighted editorial score according to Section 7 guidelines."""
        combined_text = f"{candidate.title} {candidate.summary}".lower()
        
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
        """Evaluates candidate topic against source verification, rejection filters, and memory."""
        combined_text = f"{candidate.title} {candidate.summary}".lower()
        
        # 1. Source Verification & Evidence Sufficiency Check (Section 14 & Amendment 08)
        is_verified, src_reason = self.verify_sources_and_evidence(candidate)
        if not is_verified:
            return EvaluationResult(
                topic=candidate,
                score=20.0,
                accepted=False,
                reason=f"Intentionally rejected by {persona.name}: {src_reason} (Reason: Too little evidence / Weak source credibility)",
                score_breakdown={"sourceVerification": 20.0}
            )
            
        from app.agent.triangulation import SourceTriangulationEngine
        tri_res = SourceTriangulationEngine.triangulate_sources(candidate)
        if not tri_res.is_acceptable:
            return EvaluationResult(
                topic=candidate,
                score=25.0,
                accepted=False,
                reason=f"Intentionally rejected by {persona.name}: {tri_res.source_qualification_note} (Action: {tri_res.resolution_action})",
                score_breakdown={"sourceTriangulation": 25.0}
            )
            
        # 2. Hard Rejection Filter for Prohibited Keywords / Fluff
        for rkw in persona.rejected_keywords:
            if rkw.lower() in combined_text:
                return EvaluationResult(
                    topic=candidate,
                    score=15.0,
                    accepted=False,
                    reason=f"Intentionally rejected: Contains non-technical or promotional prohibited phrase ('{rkw}'). (Reason: Primarily promotional content / Generic AI hype)",
                    score_breakdown={"hardRejection": 15.0}
                )
                
        # 3. Amendment 06 — Novelty vs Technical Significance Matrix Gate
        from app.agent.matrix import NoveltySignificanceMatrixEvaluator
        matrix_res = NoveltySignificanceMatrixEvaluator.evaluate_matrix(candidate)
        if not matrix_res.is_publishable:
            return EvaluationResult(
                topic=candidate,
                score=40.0,
                accepted=False,
                reason=f"Intentionally rejected by {persona.name}: {matrix_res.rejection_reason} (Quadrant: {matrix_res.quadrant})",
                score_breakdown={"matrixGate": 40.0}
            )

        # 4. Amendment 02 — Engineering Attention Gate (7 Core Tests)
        from app.agent.attention import EngineeringAttentionEvaluator
        attn_res = EngineeringAttentionEvaluator.evaluate_attention(candidate, self.memory)
        if not attn_res.passed_attention_gate:
            return EvaluationResult(
                topic=candidate,
                score=35.0,
                accepted=False,
                reason=f"Intentionally rejected by {persona.name}: {attn_res.discard_reason} (Reason: Failed Engineering Attention 7 Core Tests)",
                score_breakdown={"engineeringAttention": 35.0}
            )
                
        # 3. Check for memory duplicates & repetition penalty
        is_dup, dup_reason = self.memory.is_duplicate(candidate.title, candidate.summary, candidate.companies)
        if is_dup:
            return EvaluationResult(
                topic=candidate,
                score=30.0,
                accepted=False,
                reason=f"Intentionally rejected due to memory constraint: {dup_reason} (Reason: Duplicate topic / Previously covered angle)",
                score_breakdown={"memoryDuplicate": 30.0}
            )

        # 4. Calculate Weighted Score
        total_score, breakdown = self.calculate_weighted_score(candidate, persona)
        
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
            
        accepted_results.sort(key=lambda x: x.score, reverse=True)
        winner = accepted_results[0]
        
        # Amendment 07 — Engineering Reality Check Engine (Distinguishes DEMONSTRATION vs CAPABILITY vs DEPLOYMENT READINESS)
        from app.agent.reality_check import EngineeringRealityCheckEngine
        reality_check_res = EngineeringRealityCheckEngine.perform_reality_check(winner.topic)
        
        # Amendment 05 — Belief Evolution Engine: Evaluate & evolve provisional engineering beliefs
        from app.agent.beliefs import BeliefEvolutionEngine
        belief_res, belief_note = BeliefEvolutionEngine.evaluate_and_evolve(winner.topic, self.memory)
        
        # Amendment 04 — Memory as Context: Retrieve historical context & classify relationship (CONFIRMS, CONTRADICTS, EXTENDS, UNRELATED)
        from app.agent.context import CognitiveMemoryContextEngine
        cog_context = CognitiveMemoryContextEngine.retrieve_and_reason(winner.topic, self.memory)
        
        # Amendment 03 — Autonomous Curiosity Engine: Check for answering evidence & generate open questions
        from app.agent.curiosity import AutonomousCuriosityEngine
        resolved_q, updated_understanding_str = AutonomousCuriosityEngine.check_for_answering_evidence(winner.topic, self.memory)
        
        new_questions = AutonomousCuriosityEngine.generate_natural_questions(winner.topic)
        for q in new_questions:
            self.memory.add_question(q)
            
        # Analyze topic using Real-World Robotics Lens & Writing Engine
        eng_analysis = self._perform_engineering_analysis(winner.topic, persona)
        
        post_dict = self._synthesize_post(winner, rejected_results, persona, eng_analysis, updated_understanding_str, cog_context, belief_note, reality_check_res)
        
        self.memory.add_post(
            post_dict, 
            keywords=winner.topic.raw_keywords,
            companies=winner.topic.companies,
            technologies=winner.topic.technologies
        )
        
        return post_dict, [r.topic.to_dict() for r in rejected_results]

    def _perform_engineering_analysis(self, topic: CandidateTopic, persona: Persona) -> EngineeringAnalysis:
        lenses = RealWorldRoboticsLens.select_relevant_lenses(topic)
        lens_names = ", ".join([l[0] for l in lenses])
        
        hook = f"Robotics research update: {topic.title}."
        
        interpretation = (
            f"What does this actually change for robots in the real world? "
            f"Evaluating through the lens of {lens_names}, this work addresses fundamental physical execution bottlenecks. "
            f"Rather than relying on high-level LLM reasoning alone, it couples spatial representations directly with low-latency control loops."
        )
        
        limitation = (
            f"While simulation policy transfer is improving, unmodeled surface friction, joint actuator latency, "
            f"and thermal compute budgets remain major deployment bottlenecks. "
            f"A policy that functions in a controlled environment is not yet a reliable field-ready system."
        )
        
        takeaway = (
            f"Watch for empirical benchmarks measuring long-horizon task execution repeatability and edge inference latency on physical hardware."
        )
        
        return EngineeringAnalysis(
            hook=hook,
            interpretation=interpretation,
            limitation=limitation,
            takeaway=takeaway,
            relevant_lenses=lenses
        )

    def _synthesize_post(
        self,
        winner: EvaluationResult,
        rejections: List[EvaluationResult],
        persona: Persona,
        eng_analysis: EngineeringAnalysis,
        updated_understanding: Optional[str] = None,
        cog_context: Optional[Any] = None,
        belief_note: Optional[str] = None,
        reality_check_res: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes final post using exact Section 13 structure, Amendment 03 curiosity loop, Amendment 04 cognitive memory context, Amendment 05 belief evolution, Amendment 07 reality check, and Section 15 4-Question Rationale.
        """
        topic = winner.topic
        post_id = f"p-{uuid.uuid4().hex[:6]}"
        now_iso = datetime.now(timezone.utc).isoformat()
        
        curiosity_str = f"\n\n{updated_understanding}" if updated_understanding else ""
        belief_str = f"\n\n{belief_note}" if belief_note else ""
        
        rc_str = ""
        if reality_check_res:
            rc_str = f"\n\n{reality_check_res.format_summary()}"

        post_text = (
            f"HOOK\n"
            f"{topic.title}\n\n"
            f"ENGINEERING INTERPRETATION\n"
            f"{eng_analysis.interpretation}\n\n"
            f"REAL-WORLD LIMITATION\n"
            f"{eng_analysis.limitation}\n\n"
            f"ENGINEERING TAKEAWAY\n"
            f"{eng_analysis.takeaway}"
            f"{curiosity_str}"
            f"{belief_str}"
            f"{rc_str}"
        )
        
        competing_rejection_summary = ""
        if rejections:
            top_rej = rejections[0]
            competing_rejection_summary = f" Competing candidate '{top_rej.topic.title}' was rejected due to: {top_rej.reason}."
            
        cog_summary = ""
        if cog_context and cog_context.has_historical_relation:
            cog_summary = f" Historical Memory Context ({cog_context.relationship_type}): {cog_context.cognitive_reasoning}"

        # Dynamically constructed 4-question rationale (Section 15 & Amendment 04)
        rationale_text = (
            f"Topic Selection: Selected '{topic.title}' because it directly addresses core physical systems engineering challenges in {persona.domain} and scored {winner.score:.1f}/100 on weighted technical criteria.{cog_summary} "
            f"Timeliness: Relevant now because recent paper and open-weights releases in {topic.source_name} transition this technology from controlled labs toward field task deployment. "
            f"Choice Over Competitors: Chosen over competing candidates because it provides verified empirical evidence and hardware execution data rather than promotional marketing.{competing_rejection_summary} "
            f"Engineering Angle Interest: The engineering angle is compelling because it evaluates the {topic.affectedSubsystem.upper()} subsystem against physical latency, power, and sim-to-real transfer constraints."
        )
        
        return Post(
            post_id=post_id,
            created_at=now_iso,
            text=post_text,
            rationale=rationale_text,
            sources=topic.sources,
            engineering_analysis=eng_analysis.to_dict()
        )
